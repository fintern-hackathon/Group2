#!/usr/bin/env python3
"""
🔓 Database Lock Çözümü Scripti
Mevcut database'in (fintree.db) bir kopyasını oluşturur,
connection.py'daki DATABASE_PATH'i yeni kopyaya günceller.
"""

import shutil
import os
import re

DB_ORIGINAL = "fintree.db"
DB_COPY = "fintree_unlocked.db"
CONNECTION_FILE = "app/database/connection.py"

# 1. Database dosyasının kopyasını oluştur
if not os.path.exists(DB_ORIGINAL):
    print(f"❌ Orijinal database bulunamadı: {DB_ORIGINAL}")
    exit(1)

shutil.copy2(DB_ORIGINAL, DB_COPY)
print(f"✅ Database kopyalandı: {DB_COPY}")

# 2. connection.py'daki DATABASE_PATH'i güncelle
with open(CONNECTION_FILE, "r", encoding="utf-8") as f:
    content = f.read()

new_content = re.sub(
    r'DATABASE_PATH\s*=\s*"[^"]+"',
    f'DATABASE_PATH = "{DB_COPY}"',
    content
)

if content == new_content:
    print("⚠️ Zaten doğru database kullanılıyor veya pattern bulunamadı.")
else:
    with open(CONNECTION_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ connection.py güncellendi: DATABASE_PATH = '{DB_COPY}'")

print("\n🎉 Artık yeni kopya database ile lock problemi yaşamadan devam edebilirsin!") 