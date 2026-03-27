import pickle
import os

# 더미 token.pickle 생성 (테스트용)
token_data = {
    'access_token': 'test_token',
    'refresh_token': 'test_refresh_token'
}

with open('token.pickle', 'wb') as f:
    pickle.dump(token_data, f)

print('Token 파일 생성 완료!')
