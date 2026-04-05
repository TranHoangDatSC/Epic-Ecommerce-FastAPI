import requests

BASE_URL = 'http://localhost:8000'

# Login
login_data = {'username': 'admin@oldshop.com', 'password': 'admin123'}
response = requests.post(f'{BASE_URL}/api/v1/auth/login', data=login_data)
print(f"Login status: {response.status_code}")

if response.status_code == 200:
    token = response.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}

    # List moderators
    response = requests.get(f'{BASE_URL}/api/v1/admin/moderators', headers=headers)
    print(f"List moderators status: {response.status_code}")
    if response.status_code == 200:
        mods = response.json()
        print(f"Found {len(mods)} moderators")