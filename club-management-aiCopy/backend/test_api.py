import sys
import io
import urllib.request
import urllib.parse
import json

# Terminal utf-8 output on Windows
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = 'http://localhost:8000'

def request(path, method='GET', data=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(f'{BASE}{path}', headers=headers, method=method)
    if data:
        req.data = json.dumps(data).encode('utf-8')
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))

print('[1] Testing Logins...')
status, res = request('/api/auth/login', 'POST', {'username': 'admin', 'password': 'admin123'})
assert status == 200, f'Admin login failed: {res}'
admin_token = res['token']

status, res = request('/api/auth/login', 'POST', {'username': 'thanhvien', 'password': 'thanhvien123'})
assert status == 200, f'Member login failed: {res}'
member_token = res['token']
print('   -> Admin and Member login successful.')

print('[2] Testing RBAC Security...')
status, res = request('/api/members', 'POST', {'name': 'Hacker', 'email': 'hack@mail.com'}, token=member_token)
assert status == 403, f'Expected 403 but got {status}: {res}'
print('   -> RBAC protected: Member cannot create member (HTTP 403).')

print('[3] Testing Error Handling on Duplicate Email...')
status, res = request('/api/members', 'POST', {'name': 'Duplicate', 'email': 'an.nguyen@email.com'}, token=admin_token)
assert status == 400, f'Expected 400 but got {status}: {res}'
print('   -> Handled duplicate email safely:', res['detail'])

print('[4] Testing Search, Filter & Sort on Members...')
encoded_query = urllib.parse.urlencode({'search': 'Cường', 'sort_by': 'name', 'order': 'asc'})
status, res = request(f'/api/members?{encoded_query}', token=admin_token)
assert status == 200 and len(res) == 1, f'Search failed: {res}'
print('   -> Search found member:', res[0]['name'])

print('[5] Testing Tasks Search & Sort...')
encoded_query_task = urllib.parse.urlencode({'search': 'Poster', 'sort_by': 'deadline', 'order': 'asc'})
status, res = request(f'/api/tasks?{encoded_query_task}', token=admin_token)
assert status == 200 and len(res) >= 1, f'Task search failed: {res}'
print('   -> Found task:', res[0]['name'])

print('[6] Testing Dashboard Stats API...')
status, res = request('/api/dashboard/stats')
assert status == 200, f'Dashboard stats failed: {res}'
assert 'department_distribution' in res
assert 'task_distribution' in res
assert 'attendance_overview' in res
print('   -> Dashboard stats returned all chart distributions successfully.')

print('\nALL AUTOMATED API TESTS PASSED!')
