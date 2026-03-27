import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
import gspread
import time

load_dotenv()
print("=" * 50)
print("Google Sheets 연동 테스트")
print("=" * 50)

start = time.time()
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file('key.json', scopes=SCOPES)
print(f"✓ 인증 완료 ({time.time() - start:.1f}초)")

client = gspread.authorize(creds)
sheets_id = os.getenv('GOOGLE_SHEETS_ID')
sh = client.open_by_key(sheets_id)
print(f"✓ 시트 열음: {sh.title} ({time.time() - start:.1f}초)")

ws = sh.worksheet('데이터')
data = ws.get_all_records()
print(f"✓ 읽은 행 수: {len(data)}")

if data:
    print(f"첫 행: {data[0]}")

print(f"✅ 완료! ({time.time() - start:.1f}초)")
