# Strava パーソナルコーチBot - プロジェクト情報

## プロジェクト概要
StravaのトレーニングデータをClaude APIで分析し、パーソナルコーチとしてアドバイスを生成するBot。毎朝メールで配信。

## ファイル構成
- `01_get_token.py` - Strava OAuthトークン取得（初回1回だけ実行）
- `02_fetch_data.py` - Stravaからトレーニングデータ取得・整形
- `03_coach_bot.py` - Claude APIでコーチアドバイス生成＋Gmail送信（メイン）
- `04_send_email.py` - Gmail SMTPメール送信モジュール
- `05_fetch_garmin.py` - Garmin Connectから睡眠・Body Battery・HRV・ストレスデータ取得（feature/garmin-connect ブランチ）
- `.env` - APIキー・個人情報保存（Gitに上げない）
- `.env.example` - .envのテンプレート

## ブランチ戦略
- `main` - 安定版・商用ベース（Strava + Claude + Gmail）
- `feature/garmin-connect` - 個人利用向け Garmin Connect 統合版

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
- Garmin Connect 非公式API（garminconnect ライブラリ）※feature ブランチのみ
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
GARMIN_EMAIL=            # feature/garmin-connect ブランチのみ
GARMIN_PASSWORD=         # feature/garmin-connect ブランチのみ
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
- `02_fetch_data.py` / `04_send_email.py` / `05_fetch_garmin.py` は `importlib` でimport
- max_tokens=4096（長いアドバイスでも途切れないよう設定）
- cronログ: `/tmp/coach_bot.log`
- Garmin Connect は非公式APIのため商用利用不可。個人利用・feature ブランチのみで使用
- `05_fetch_garmin.py` は昨日のデータを取得（今日分は翌日確定）
