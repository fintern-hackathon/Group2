#!/usr/bin/env python3
"""
Fintree App Uninstaller
Bu script projeyi tamamen kaldırır.
Kullanım: python uninstall.py
"""

import os
import shutil
import sys
from pathlib import Path

def confirm_uninstall():
    """Kullanıcıdan onay al"""
    print("🗑️  Fintree App Uninstaller")
    print("=" * 40)
    print("⚠️  DİKKAT: Bu işlem geri alınamaz!")
    print("📁 Silinecek klasör:", os.getcwd())
    print("\nSilinecek dosyalar:")
    print("  • Tüm Python dosyaları")
    print("  • Database (fintree.db)")
    print("  • Venv klasörü")
    print("  • __pycache__ klasörleri")
    print("  • Tüm proje dosyaları")
    
    while True:
        choice = input("\n❓ Devam etmek istiyor musunuz? (evet/hayır): ").lower().strip()
        if choice in ['evet', 'e', 'yes', 'y']:
            return True
        elif choice in ['hayır', 'h', 'no', 'n']:
            return False
        else:
            print("⚠️  Lütfen 'evet' veya 'hayır' yazın.")

def kill_running_processes():
    """Çalışan Python processlerini durdur"""
    try:
        import psutil
        current_pid = os.getpid()
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Eğer process python ve bu projeden bir dosya çalıştırıyorsa
                if (proc.info['name'] and 'python' in proc.info['name'].lower() and 
                    proc.info['cmdline'] and proc.info['pid'] != current_pid):
                    
                    cmdline = ' '.join(proc.info['cmdline'])
                    if any(file in cmdline for file in ['main.py', 'working_main.py', 'load_data.py']):
                        print(f"🔄 Durduruldu: PID {proc.info['pid']}")
                        proc.terminate()
                        proc.wait(timeout=3)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                pass
    except ImportError:
        print("📝 psutil bulunamadı, manuel olarak sunucuyu durdurun.")

def uninstall_project():
    """Projeyi tamamen kaldır"""
    project_root = Path.cwd()
    parent_dir = project_root.parent
    project_name = project_root.name
    
    try:
        print("\n🔄 Kaldırma işlemi başlıyor...")
        
        # 1. Çalışan processları durdur
        print("1️⃣ Çalışan processler durduruluyor...")
        kill_running_processes()
        
        # 2. Üst dizine çık
        print("2️⃣ Üst dizine çıkılıyor...")
        os.chdir(parent_dir)
        
        # 3. Proje klasörünü sil
        print(f"3️⃣ Proje klasörü siliniyor: {project_name}")
        if project_root.exists():
            shutil.rmtree(project_root, ignore_errors=True)
        
        print("\n✅ Fintree App başarıyla kaldırıldı!")
        print(f"📁 Silinen klasör: {project_root}")
        print("\n👋 İyi günler!")
        
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        print("💡 Manuel olarak klasörü silmeyi deneyin.")
        return False
    
    return True

def main():
    """Ana fonksiyon"""
    try:
        if confirm_uninstall():
            success = uninstall_project()
            sys.exit(0 if success else 1)
        else:
            print("\n🚫 Kaldırma işlemi iptal edildi.")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n🚫 İşlem kullanıcı tarafından iptal edildi.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 