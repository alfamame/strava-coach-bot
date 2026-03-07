"""
04_send_email.py
================
Gmailでコーチアドバイスを送信するモジュール。
03_coach_bot.py から呼び出して使います。
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS      = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECIPIENT_EMAIL    = os.getenv("RECIPIENT_EMAIL")


def send_coach_advice(advice_text: str) -> bool:
    """コーチアドバイスをGmailで送信する"""
    today = date.today().strftime("%Y年%m月%d日")
    subject = f"パーソナルコーチBot - {today}のアドバイス"

    msg = MIMEMultipart()
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = RECIPIENT_EMAIL
    msg["Subject"] = subject

    msg.attach(MIMEText(advice_text, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(msg)

    return True


if __name__ == "__main__":
    # テスト送信
    test_text = "これはテストメールです。\nコーチBotのメール送信が正常に動作しています。"
    print("テストメール送信中...")
    send_coach_advice(test_text)
    print(f"送信完了: {RECIPIENT_EMAIL}")
