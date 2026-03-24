# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要
StravaのトレーニングデータとGarmin Connectのコンディションデータを Claude API で分析し、パーソナルコーチアドバイスを毎朝メール配信するBot。プロダクト名は「追い風」。

## 実行コマンド

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# 初回のみ：Strava OAuthトークン取得（ブラウザ認証が必要）
python 01_get_token.py

# メインBot実行（Strava + Garmin → Claude → Gmail）
python 03_coach_bot.py

# 各モジュールの単体動作確認
python 02_fetch_data.py      # Stravaデータ取得テスト
python 05_fetch_garmin.py    # Garminデータ取得テスト
python 04_send_email.py      # メール送信テスト
```

## アーキテクチャ

### データフロー
```
Strava API (02) ─┐
                  ├→ 03_coach_bot.py → Claude API → Gmail (04)
Garmin API  (05) ─┘
```

`03_coach_bot.py` がエントリポイント。`importlib` で他モジュールを動的ロードしている（ファイル名が数字始まりで通常の `import` が使えないため）。

### 各モジュールの責務
- **02_fetch_data.py** — Strava REST API からアクティビティ一覧・心拍ゾーン・アスリート情報を取得し、LLM 向けのテキストサマリー（`build_training_summary(days=7)`）を返す
- **05_fetch_garmin.py** — Garmin Connect 非公式ライブラリで睡眠・Body Battery・HRV・ストレスを取得。**常に「昨日」のデータを参照**（当日分は翌日以降に確定するため）。`build_garmin_summary(days=7)` を返す
- **03_coach_bot.py** — 上記2つのサマリーとアスリートプロフィール（.env）を LangChain の `ChatPromptTemplate` に渡し、LangChain LCEL チェーン（`COACH_PROMPT | llm`）で Claude API を呼び出す。モデルは `claude-sonnet-4-6`、`temperature=0.7`、`max_tokens=4096`
- **04_send_email.py** — Gmail SMTP（SSL/465番ポート）でメール送信
- **frontend/index.html** — 静的ランディングページ（バックエンドとは非接続）

### アスリートプロフィール
個人情報は `.env` で管理。`03_coach_bot.py` 起動時に `build_athlete_profile()` が読み込み、プロンプトに埋め込む。変更は `.env` の `ATHLETE_*` 変数を編集すればよい。

## 自動実行（GitHub Actions）
`.github/workflows/coach_bot.yml` が毎日 **6:30 JST**（21:30 UTC）に `03_coach_bot.py` を実行。すべての認証情報は GitHub Secrets で管理。ローカル実行時は `.env` から読み込む。`TZ=Asia/Tokyo` を明示設定しないと Garmin のデータ日付がズレるので注意。

## Garminトークンのセットアップ（GitHub Actions用）
GitHub Actions 環境ではブラウザ認証できないため、ローカルでログイン済みの `garth` セッションをトークンとして渡す。

```bash
# ローカルでGarminにログイン後、セッションディレクトリをtar.gz化してbase64エンコード
python -c "
from garminconnect import Garmin
import os, tarfile, base64, io
client = Garmin('YOUR_EMAIL', 'YOUR_PASSWORD')
client.login()
client.garth.dump('~/.garth')
"
# ~/.garth ディレクトリをtar.gz→base64にしてGitHub Secretsの GARMIN_TOKENS に設定
tar czf - -C ~/.garth . | base64
```

`GARMIN_TOKENS` が設定されている場合、`get_garmin_client()` はパスワード認証をスキップしてトークンを復元する。

## 重要な制約
- Garmin Connect ライブラリは**非公式API**のため商用利用不可。個人利用のみ
- Strava の心拍ゾーン取得（`get_activity_zones()`）は Strava サブスクリプションが必要
- cron ローカル実行時のログ: `/tmp/coach_bot.log`

## 環境変数（.env / GitHub Secrets）
```
STRAVA_CLIENT_ID / STRAVA_CLIENT_SECRET / STRAVA_REFRESH_TOKEN
ANTHROPIC_API_KEY
GMAIL_ADDRESS / GMAIL_APP_PASSWORD / RECIPIENT_EMAIL
GARMIN_EMAIL / GARMIN_PASSWORD
GARMIN_TOKENS          # GitHub Actions用：base64エンコード済みgarthセッション
ATHLETE_AGE / ATHLETE_GENDER / ATHLETE_WEIGHT_KG / ATHLETE_BODY_FAT_PCT
ATHLETE_VO2MAX / ATHLETE_ENDURANCE_LEVEL
ATHLETE_GOALS          # / 区切りで複数指定
ATHLETE_TRAINING_PLAN  # 週間計画
ATHLETE_NOTES          # 体の注意点
```
