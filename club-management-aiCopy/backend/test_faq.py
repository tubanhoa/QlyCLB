import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

test_questions = [
    'Chưa có kinh nghiệm có tham gia được không?',
    'Tham gia CLB có bị rớt môn không?',
    'Có phải đóng tiền quỹ gì không?',
    'Quyền lợi khi vào CLB là gì?',
    'Phỏng vấn vào CLB thường hỏi gì?',
    'Học ngành khác tham gia được không?',
    'Nên vào ban nào?',
    'Ban Kỹ thuật làm gì?',
    'Ban Truyền thông làm gì?',
    'Ban Sự kiện làm gì?',
    'Ban Đối ngoại làm gì?',
    'Ban Học thuật làm gì?',
    'Điểm rèn luyện được cộng bao nhiêu?',
    'Mẫu đơn xin nghỉ sinh hoạt CLB',
    'Lịch sinh hoạt CLB',
    'Chuyển ban được không'
]

print("Starting test of 16 FAQ questions...")
for idx, q in enumerate(test_questions, 1):
    req = urllib.request.Request(
        'http://localhost:8000/api/ai/chat',
        data=json.dumps({'message': q}).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    res = urllib.request.urlopen(req)
    data = json.loads(res.read().decode('utf-8'))
    ans = data.get('answer', '')
    clubs = data.get('suggestedClubs', [])
    followups = data.get('followUpQuestions', [])
    print(f"[{idx:02d}/16] {q:<42} -> AnsLen: {len(ans)} chars | Clubs: {len(clubs)} | Followups: {len(followups)}")

print("All 16 FAQ tests completed successfully!")
