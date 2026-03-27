import os
from dotenv import load_dotenv

load_dotenv()
print("? .env 로드 완료")

try:
    from google.oauth2.service_account import Credentials
    print("? Credentials import 완료")
    
    creds = Credentials.from_service_account_file('key.json', scopes=['https://www.googleapis.com/auth/spreadsheets'])
    print("? 인증 credentials 생성 완료")
    
    import gspread
    print("? gspread import 완료")
    
    client = gspread.authorize(creds)
    print("? gspread 클라이언트 생성 완료")
    
    sheets_id = os.getenv('GOOGLE_SHEETS_ID')
    print(f"? Sheets ID 로드")
    
    print(" Google Sheets 시트 열기 시작...")
    sh = client.open_by_key(sheets_id)
    print(f"? 시트 열음: {sh.title}")
    
    print("? 모든 단계 완료!")
    
except Exception as e:
    print(f"? 에러: {type(e).__name__}: {e}")
