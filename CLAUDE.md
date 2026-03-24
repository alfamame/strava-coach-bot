# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要
StravaのトレーニングデータをClaude APIで分析し、パーソナルコーチアドバイスを生成してGmailで毎朝配信するBot。フロントエンド（LP）も含む。

## 実行コマンド

```bash
# ライブラリインストール
pip install -r requirements.txt

# 初回のみ：Stravaトークン取得
python 01_get_token.py

# データ取得テスト
python 02_fetch_data.py

# コーチBot実行（アドバイス生成＋メール送信）
python 03_coach_bot.py

# メール送信テスト
python 04_send_email.py
```

## アーキテクチャ

```
01_get_token.py   → Strava OAuth認証（初回1回のみ）
02_fetch_data.py  → Strava API呼び出し・データ整形（build_training_summary）
03_coach_bot.py   → メイン処理（02と04をimportlibで動的import）
04_send_email.py  → Gmail SMTP送信（send_coach_advice）
frontend/
└── index.html    → サービスLP「追い風」（単一HTMLファイル、依存なし）
```

**03_coach_bot.py のデータフロー：**
1. `02_fetch_data.build_training_summary(days=7)` でStravaデータ取得
2. `.env` からアスリートプロフィールを読み込み `build_athlete_profile()` で構築
3. LangChain + Claude API（claude-sonnet-4-6）でアドバイス生成
4. `04_send_email.send_coach_advice()` でGmail送信

## 重要な実装メモ

- `02_fetch_data.py` と `04_send_email.py` は `importlib.import_module` で動的importしている（ファイル名が数字始まりのため通常importできない）
- アスリートプロフィールは `.env` で管理（`ATHLETE_*` 変数群）、コードに直接書かない
- `max_tokens=4096` に設定済み
- Stravaアクセストークンは毎回 `STRAVA_REFRESH_TOKEN` から自動更新する（`get_access_token()` が呼び出しごとに新トークンを取得）
- `get_activity_zones()` はStravaプレミアムサブスクリプションが必要。現在のメインフローでは使用していない
- Gmail送信は SMTP_SSL（ポート465）経由。`GMAIL_APP_PASSWORD` はGoogleアカウントの「アプリパスワード」（16桁）であり、通常のパスワードではない

## 環境変数（.envに設定）

`.env.example` を `.env` にコピーして各値を設定する。

| 変数 | 説明 |
|------|------|
| `STRAVA_CLIENT_ID` / `STRAVA_CLIENT_SECRET` | Strava APIアプリ情報 |
| `STRAVA_REFRESH_TOKEN` | 01_get_token.py実行後に取得 |
| `ANTHROPIC_API_KEY` | Claude API（別途課金、Proプランとは別） |
| `GMAIL_ADDRESS` / `GMAIL_APP_PASSWORD` | Gmail送信用（アプリパスワード16桁） |
| `RECIPIENT_EMAIL` | 送信先アドレス |
| `ATHLETE_AGE` / `ATHLETE_GENDER` / `ATHLETE_WEIGHT_KG` etc. | プロフィール情報 |
