import pickle
import json

with open('credentials.json', 'r') as f:
    credentials = json.load(f)

with open('token.pickle', 'wb') as f:
    pickle.dump(credentials, f)

print('✅ token.pickle 생성 완료!')
