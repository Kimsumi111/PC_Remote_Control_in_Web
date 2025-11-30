# app.py 최종 버전
import collections.abc
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

from flask import Flask, render_template
from flask_socketio import SocketIO
import pyautogui
import os
import socket
import qrcode # QR코드 생성용
from jamo import h2j, j2hcj 

# === [환경 설정] ===
pyautogui.FAILSAFE = False 
pyautogui.PAUSE = 0

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

# === [유틸리티] 내 IP 주소 자동으로 찾기 ===
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 실제 연결은 안 하고 구글 DNS 쪽으로 패킷을 던져보는 시늉만 해서 내 IP를 알아냄
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

# === [한글 처리 로직] ===
JAMO_MAP = {
    'ㄱ': 'r', 'ㄴ': 's', 'ㄷ': 'e', 'ㄹ': 'f', 'ㅁ': 'a', 'ㅂ': 'q', 'ㅅ': 't', 'ㅇ': 'd',
    'ㅈ': 'w', 'ㅊ': 'c', 'ㅋ': 'z', 'ㅌ': 'x', 'ㅍ': 'v', 'ㅎ': 'g',
    'ㄲ': 'R', 'ㄸ': 'E', 'ㅃ': 'Q', 'ㅆ': 'T', 'ㅉ': 'W',
    'ㅏ': 'k', 'ㅑ': 'i', 'ㅓ': 'j', 'ㅕ': 'u', 'ㅗ': 'h', 'ㅛ': 'y', 'ㅜ': 'n', 'ㅠ': 'b',
    'ㅡ': 'm', 'ㅣ': 'l', 'ㅐ': 'o', 'ㅒ': 'O', 'ㅔ': 'p', 'ㅖ': 'P',
    'ㅘ': 'hk', 'ㅙ': 'ho', 'ㅚ': 'hl', 'ㅝ': 'nj', 'ㅞ': 'np', 'ㅟ': 'nl', 'ㅢ': 'ml'
}

def type_korean(text):
    for char in text:
        if char in JAMO_MAP: # 낱글자 처리
            pyautogui.write(JAMO_MAP[char])
        elif '가' <= char <= '힣': # 완성형 한글 처리
            jamo_str = j2hcj(h2j(char))
            for jamo in jamo_str:
                key = JAMO_MAP.get(jamo, '')
                if key: pyautogui.write(key)
        else:
            pyautogui.write(char)

# === [라우팅 및 이벤트 핸들러] ===
@app.route('/')
def index(): return render_template('index.html')

@socketio.on('mouse_move')
def handle_mouse_move(data): pyautogui.moveRel(data['x'], data['y'])

@socketio.on('mouse_click')
def handle_click(data): 
    if data['type'] == 'left': pyautogui.click()
    elif data['type'] == 'right': pyautogui.rightClick()

@socketio.on('mouse_scroll')
def handle_scroll(data): pyautogui.scroll(int(data['dy'] * -20))

@socketio.on('keyboard_input')
def handle_keyboard(data): type_korean(data['text'])

@socketio.on('macro_action')
def handle_macro(data):
    cmd = data['command']
    if cmd == 'space': pyautogui.press('space')
    elif cmd == 'enter': pyautogui.press('enter')
    elif cmd == 'backspace': pyautogui.press('backspace')
    elif cmd == 'vol_up': pyautogui.press('volumeup')
    elif cmd == 'vol_down': pyautogui.press('volumedown')
    elif cmd == 'shutdown': os.system("shutdown /s /t 1")
    elif cmd == 'hangul': pyautogui.press('hangul')

# === [메인 실행] ===
if __name__ == '__main__':
    local_ip = get_local_ip()
    port = 8080
    url = f"http://{local_ip}:{port}"

    print("\n" + "="*40)
    print(f"🚀 [누워서 넷플릭스] 서버 시작됨")
    print(f"📱 접속 주소: {url}")
    print("="*40 + "\n")

    # QR코드 생성 및 터미널 출력
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.make()
    print("아래 QR코드를 폰 카메라로 찍으세요!\n")
    qr.print_ascii(invert=True) # 터미널 배경이 검은색이면 invert=True

    socketio.run(app, host='0.0.0.0', port=port)