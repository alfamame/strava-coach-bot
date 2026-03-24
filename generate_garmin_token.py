"""
generate_garmin_token.py
========================
Garmin Connect のOAuthトークンをローカルで生成し、
GitHub Secrets に登録できる base64 文字列を出力するスクリプト。

【使い方】
1. .env に GARMIN_EMAIL / GARMIN_PASSWORD を設定する
2. python generate_garmin_token.py を実行する
3. 出力された文字列を GitHub Secrets の GARMIN_TOKENS に登録する

【再生成のタイミング】
- 429エラーが再発したとき（トークンが無効になった場合）
"""

import base64
import io
import tarfile
import tempfile
import os
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv()

EMAIL    = os.getenv("GARMIN_EMAIL")
PASSWORD = os.getenv("GARMIN_PASSWORD")

if not EMAIL or not PASSWORD:
    raise SystemExit("❌ .env に GARMIN_EMAIL / GARMIN_PASSWORD を設定してください")

print(f"Garmin Connect にログイン中: {EMAIL}")
client = Garmin(EMAIL, PASSWORD)
client.login()
print("✅ ログイン成功")

# トークンを一時ディレクトリに保存
tmpdir = tempfile.mkdtemp()
client.garth.dump(tmpdir)

# tarball → base64 エンコード
buf = io.BytesIO()
with tarfile.open(fileobj=buf, mode="w:gz") as tar:
    tar.add(tmpdir, arcname=".")
token_b64 = base64.b64encode(buf.getvalue()).decode()

print()
print("=" * 60)
print("以下の文字列を GitHub Secrets の GARMIN_TOKENS に登録してください:")
print("=" * 60)
print(token_b64)
print("=" * 60)
