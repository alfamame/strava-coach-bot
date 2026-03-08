# Strava パーソナルコーチBot - プロジェクト情報

## プロジェクト概要
StravaのトレーニングデータをClaude APIで分析し、パーソナルコーチとしてアドバイスを生成するBot。毎朝メールで配信。

## ファイル構成
- `01_get_token.py` - Strava OAuthトークン取得（初回1回だけ実行）
- `02_fetch_data.py` - Stravaからトレーニングデータ取得・整形
- `03_coach_bot.py` - Claude APIでコーチアドバイス生成＋Gmail送信（メイン）
- `04_send_email.py` - Gmail SMTPメール送信モジュール
- `.env` - APIキー・個人情報保存（Gitに上げない）
- `.env.example` - .envのテンプレート

## 実行方法
```bash
# 初回セットアップのみ
python 01_get_token.py

# 毎日の使用
python 03_coach_bot.py
```

## 技術スタック
- Python
- Strava API（アクティビティデータ取得）
- Claude API（claude-sonnet-4-6）
- LangChain（langchain-anthropic、langchain-core）
- Gmail SMTP（smtplib + アプリパスワード）
- python-dotenv（環境変数管理）
- cron（macOS定期実行）

## アスリートプロフィール（.envで管理）
個人情報のため `.env` に定義し、`03_coach_bot.py` が読み込む。
更新は `.env` の以下の項目を編集：
- `ATHLETE_AGE` / `ATHLETE_GENDER`
- `ATHLETE_WEIGHT_KG` / `ATHLETE_BODY_FAT_PCT`
- `ATHLETE_VO2MAX` / `ATHLETE_ENDURANCE_LEVEL`
- `ATHLETE_GOALS` - 目標（/ 区切りで複数）
- `ATHLETE_TRAINING_PLAN` - 週間計画
- `ATHLETE_NOTES` - 体の注意点

## 環境変数（.envに設定）
```
STRAVA_CLIENT_ID=
STRAVA_CLIENT_SECRET=
STRAVA_REFRESH_TOKEN=    # 01_get_token.py実行後に取得
ANTHROPIC_API_KEY=
GMAIL_ADDRESS=
GMAIL_APP_PASSWORD=      # Googleアカウントのアプリパスワード（16桁）
RECIPIENT_EMAIL=
ATHLETE_AGE=
ATHLETE_GENDER=
ATHLETE_WEIGHT_KG=
ATHLETE_BODY_FAT_PCT=
ATHLETE_VO2MAX=
ATHLETE_ENDURANCE_LEVEL=
ATHLETE_GOALS=
ATHLETE_TRAINING_PLAN=
ATHLETE_NOTES=
```

## 開発メモ
- 取得日数はデフォルト7日間（`build_training_summary(days=7)`）
- `02_fetch_data.py` は `03_coach_bot.py` から `importlib` でimport
- `04_send_email.py` は `03_coach_bot.py` から `importlib` でimport
- max_tokens=4096（長いアドバイスでも途切れないよう設定）
- cronログ: `/tmp/coach_bot.log`
