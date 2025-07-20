import asyncio
import json
from datetime import datetime
from sqlalchemy import select, func
from app.database.connection import init_db, get_db
from app.models.user import User
from app.models.transaction import DailyTransaction, UserTotal

# Test User ID
TEST_USER_ID = "7f3c989b-221e-47c3-b502-903199b39ad4"

async def create_test_user():
    """Test kullanıcısı oluştur"""
    async for session in get_db():
        try:
            # Check if user already exists
            result = await session.execute(select(User).where(User.id == TEST_USER_ID))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"✅ Test user already exists: {existing_user.name}")
                return existing_user
            
            # Create new test user
            new_user = User(
                id=TEST_USER_ID,
                email="test@fintree.com",
                name="Test User (JSON Data)",
                phone="555-0123",
                password_hash="demo_hash"
            )
            
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            
            # Create user totals record
            user_total = UserTotal(user_id=new_user.id)
            session.add(user_total)
            await session.commit()
            
            print(f"✅ Test user created: {new_user.name}")
            return new_user
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error creating test user: {e}")
            raise
        break

async def load_transactions_from_json():
    """JSON dosyasından daily transaction'ları yükle"""
    
    # Load JSON data
    with open('ekstre_dataset_realistic_4_months_final_clean.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    print(f"📄 JSON dosyasından {len(json_data)} günlük transaction bulundu")
    
    async for session in get_db():
        try:
            loaded_count = 0
            skipped_count = 0
            
            for record in json_data:
                # Parse date
                date_str = record.get('date')
                transaction_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                # Check if transaction already exists
                result = await session.execute(
                    select(DailyTransaction).where(
                        DailyTransaction.user_id == TEST_USER_ID,
                        DailyTransaction.date == transaction_date
                    )
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Parse expenses
                expenses = record.get('expenses_summary', {})
                
                # Create daily transaction
                transaction = DailyTransaction(
                    user_id=TEST_USER_ID,
                    date=transaction_date,
                    income=float(record.get('income', 0.0)),
                    food=float(expenses.get('food', 0.0)),
                    transport=float(expenses.get('transport', 0.0)),
                    bills=float(expenses.get('bills', 0.0)),
                    entertainment=float(expenses.get('entertainment', 0.0)),
                    health=float(expenses.get('health', 0.0)),
                    clothing=float(expenses.get('clothing', 0.0))
                )
                
                # Calculate totals
                transaction.calculate_totals()
                
                session.add(transaction)
                loaded_count += 1
                
                # Commit her 50 record'da bir
                if loaded_count % 50 == 0:
                    await session.commit()
                    print(f"📥 {loaded_count} transaction yüklendi...")
            
            # Final commit
            await session.commit()
            
            print(f"✅ Toplam {loaded_count} transaction yüklendi")
            print(f"⏭️ {skipped_count} transaction zaten mevcuttu (atlandı)")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error loading transactions: {e}")
            raise
        break

async def update_user_totals():
    """Kullanıcının total verilerini güncelle"""
    async for session in get_db():
        try:
            # Get all transactions for user
            result = await session.execute(
                select(
                    func.sum(DailyTransaction.income).label('total_income'),
                    func.sum(DailyTransaction.total_expenses).label('total_expenses'),
                    func.count(DailyTransaction.id).label('days_count'),
                    func.min(DailyTransaction.date).label('first_date')
                ).where(DailyTransaction.user_id == TEST_USER_ID)
            )
            
            totals = result.one()
            
            # Update user totals
            user_total_result = await session.execute(
                select(UserTotal).where(UserTotal.user_id == TEST_USER_ID)
            )
            user_total = user_total_result.scalar_one_or_none()
            
            if user_total:
                # SQLAlchemy ORM update
                from sqlalchemy import update
                await session.execute(
                    update(UserTotal)
                    .where(UserTotal.user_id == TEST_USER_ID)
                    .values(
                        total_income=float(totals.total_income or 0),
                        total_expenses=float(totals.total_expenses or 0),
                        days_in_system=int(totals.days_count or 0),
                        first_transaction_date=totals.first_date
                    )
                )
                
                await session.commit()
                
                print(f"✅ User totals updated:")
                print(f"   💰 Total Income: {float(totals.total_income or 0):,.2f} TL")
                print(f"   💸 Total Expenses: {float(totals.total_expenses or 0):,.2f} TL")
                print(f"   📅 Days in system: {int(totals.days_count or 0)}")
                print(f"   🗓️ First transaction: {totals.first_date}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error updating user totals: {e}")
            raise
        break

async def main():
    """Ana yükleme fonksiyonu"""
    print("🗄️ SQLite Database Data Loading")
    print("=" * 50)
    
    # Initialize database
    await init_db()
    
    # Create test user
    await create_test_user()
    
    # Load transactions
    await load_transactions_from_json()
    
    # Update user totals
    await update_user_totals()
    
    print(f"\n🎉 Data loading completed!")
    print(f"📋 Test User ID: {TEST_USER_ID}")
    print(f"🌐 Test with: http://192.168.1.16:8006/api/v1/analytics/{TEST_USER_ID}/score")

if __name__ == "__main__":
    asyncio.run(main()) 