# Strava パーソナルコーチBot

StravaのトレーニングデータをClaude APIで分析し、パーソナルコーチとしてアドバイスを生成。毎朝メールで配信するBot。

## ファイル構成

```
strava_coach_bot/
├── README.md           ← このファイル
├── .env                ← APIキー・個人情報（Gitに上げない）
├── .env.example        ← .envのテンプレート
├── 01_get_token.py     ← 最初の1回だけ実行（Stravaトークン取得）
├── 02_fetch_data.py    ← Stravaからトレーニングデータ取得・整形
├── 03_coach_bot.py     ← AIコーチアドバイス生成＋メール送信（メイン）
├── 04_send_email.py    ← Gmail送信モジュール
└── requirements.txt    ← 必要なライブラリ
```

## セットアップ手順

### Step 1: Stravaアプリ登録

1. https://www.strava.com/settings/api を開く
2. 以下を入力してアプリ作成：
   - Application Name: MyCoachBot（任意）
   - Category: Training
   - Authorization Callback Domain: localhost
   - Website: http://localhost
3. **Client ID** と **Client Secret** をメモする

### Step 2: ライブラリインストール

```bash
pip install -r requirements.txt
```

### Step 3: .envファイルを作成

`.env.example` を `.env` にコピーして値を入力：

```bash
cp .env.example .env
```

設定が必要な項目：
- Strava API（Client ID / Secret / Refresh Token）
- Anthropic API Key
- Gmail設定（送信元アドレス・アプリパスワード・受信先アドレス）
- アスリートプロフィール（年齢・体重・目標など）

### Step 4: Stravaトークン取得（最初の1回だけ）

```bash
python 01_get_token.py
```

ブラウザが開くので認証 → リダイレクト後のURLを貼り付け → `.env` の `STRAVA_REFRESH_TOKEN` に保存

### Step 5: Gmail アプリパスワード設定

1. Googleアカウント → セキュリティ → 2段階認証を有効化
2. アプリパスワードを生成（アプリ: メール）
3. 生成された16桁のパスワードを `.env` の `GMAIL_APP_PASSWORD` に設定

### Step 6: 動作確認

```bash
# Stravaデータ取得テスト
python 02_fetch_data.py

# コーチBot実行（アドバイス生成＋メール送信）
python 03_coach_bot.py
```

### Step 7: 毎朝6時の自動実行（cron設定）

```bash
crontab -e
```

以下を追加（パスは環境に合わせて変更）：

```
0 6 * * * cd "/path/to/strava_coach_bot" && python3 03_coach_bot.py >> /tmp/coach_bot.log 2>&1
```

ログ確認：
```bash
cat /tmp/coach_bot.log
```

> **注意**: macOS Apple SiliconではMacがスリープ中はcronが実行されません。充電ケーブルを接続しスリープを無効化した状態で使用してください。

## 環境変数一覧

| 変数名 | 説明 |
|--------|------|
| `STRAVA_CLIENT_ID` | Strava APIのClient ID |
| `STRAVA_CLIENT_SECRET` | Strava APIのClient Secret |
| `STRAVA_REFRESH_TOKEN` | Stravaのリフレッシュトークン（01実行後取得）|
| `ANTHROPIC_API_KEY` | Anthropic Claude APIキー |
| `GMAIL_ADDRESS` | 送信元GmailアドレスF |
| `GMAIL_APP_PASSWORD` | Gmailアプリパスワード（16桁）|
| `RECIPIENT_EMAIL` | コーチアドバイスの受信先メールアドレス |
| `ATHLETE_AGE` | 年齢 |
| `ATHLETE_GENDER` | 性別 |
| `ATHLETE_WEIGHT_KG` | 体重(kg) |
| `ATHLETE_BODY_FAT_PCT` | 体脂肪率(%) |
| `ATHLETE_VO2MAX` | VO2Max |
| `ATHLETE_ENDURANCE_LEVEL` | 持久力レベル |
| `ATHLETE_GOALS` | トレーニング目標 |
| `ATHLETE_TRAINING_PLAN` | 週間トレーニング計画 |
| `ATHLETE_NOTES` | 体の注意点・コンディション |

## 技術スタック

- Python
- Strava API（アクティビティデータ取得）
- Claude API（claude-sonnet-4-6）
- LangChain（langchain-anthropic）
- Gmail SMTP（smtplib）
- python-dotenv（環境変数管理）
