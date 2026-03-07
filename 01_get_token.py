"""
01_get_token.py
==============
【最初の1回だけ実行するスクリプト】
Strava APIのアクセストークンとリフレッシュトークンを取得します。
取得したリフレッシュトークンを .env ファイルに保存してください。
"""

import webbrowser
import requests
from urllib.parse import urlparse, parse_qs
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REDIRECT_URI = "http://localhost/"

def get_authorization_url():
    """認証URLを生成してブラウザで開く"""
    url = (
        f"http://www.strava.com/oauth/authorize?"
        f"client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&approval_prompt=force"
        f"&scope=activity:read_all,profile:read_all"
    )
    return url

def exchange_code_for_token(code):
    """認証コードをトークンに交換する"""
    response = requests.post(
        url="https://www.strava.com/api/v3/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
        }
    )
    return response.json()

def main():
    print("=" * 60)
    print("Strava APIトークン取得ツール")
    print("=" * 60)
    print()

    # Step 1: 認証URLをブラウザで開く
    auth_url = get_authorization_url()
    print("【Step 1】ブラウザでStravaの認証ページを開きます...")
    print()
    print(f"もし自動で開かない場合は、以下のURLを手動でブラウザに貼り付けてください：")
    print(f"\n{auth_url}\n")
    
    webbrowser.open(auth_url)

    # Step 2: 認証後のURLからcodeを取得
    print("=" * 60)
    print("【Step 2】Stravaで「許可する」をクリックした後...")
    print()
    print("ブラウザのアドレスバーに表示されたURLをコピーして貼り付けてください")
    print("（例: http://localhost/?state=&code=XXXXXXXXXX&scope=...）")
    print()
    
    redirected_url = input("リダイレクト後のURL全体を貼り付け: ").strip()
    
    # URLからcodeを抽出
    try:
        parsed = urlparse(redirected_url)
        code = parse_qs(parsed.query)["code"][0]
        print(f"\n✅ codeの取得に成功しました: {code[:10]}...")
    except Exception:
        # URLでなくcodeだけ貼り付けた場合
        code = redirected_url
        print(f"\n✅ codeを使用します: {code[:10]}...")

    # Step 3: トークンを取得
    print("\n【Step 3】トークンを取得中...")
    tokens = exchange_code_for_token(code)

    if "access_token" not in tokens:
        print(f"\n❌ エラーが発生しました: {tokens}")
        return

    print("\n✅ トークンの取得に成功しました！")
    print("=" * 60)
    print()
    print("【重要】以下の値を .env ファイルに保存してください：")
    print()
    print(f"STRAVA_CLIENT_ID={CLIENT_ID}")
    print(f"STRAVA_CLIENT_SECRET={CLIENT_SECRET}")
    print(f"STRAVA_REFRESH_TOKEN={tokens['refresh_token']}")
    print()
    print("=" * 60)
    print("※ access_token は6時間で期限切れになりますが、")
    print("  refresh_token を使って自動更新されるので保存不要です。")
    print("=" * 60)

    # 確認用：アスリート情報を取得してみる
    print("\n【確認】あなたのStravaプロフィール情報を取得中...")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    athlete = requests.get(
        "https://www.strava.com/api/v3/athlete",
        headers=headers
    ).json()
    
    print(f"\n✅ 接続成功！")
    print(f"   名前: {athlete.get('firstname', '')} {athlete.get('lastname', '')}")
    print(f"   都市: {athlete.get('city', '未設定')}")
    print(f"\nセットアップ完了です！次は 02_fetch_data.py を実行してください。")

if __name__ == "__main__":
    main()
