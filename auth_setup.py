import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
TOKEN_FILE = 'token.pickle'
CLIENT_SECRET = 'client_secret.json'

if not os.path.exists(CLIENT_SECRET):
    print(f"Error: {CLIENT_SECRET} not found!")
    exit(1)

creds = None
flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, YOUTUBE_SCOPES)
creds = flow.run_local_server(port=0)

with open(TOKEN_FILE, 'wb') as token:
    pickle.dump(creds, token)

print("✅ Authentication successful! token.pickle created.")
