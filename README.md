# Strava パーソナルコーチBot セットアップガイド

## フォルダ構成
```
strava_coach_bot/
├── README.md           ← このファイル
├── .env                ← APIキーを保存（Gitに上げない！）
├── .env.example        ← .envのテンプレート
├── 01_get_token.py     ← 最初の1回だけ実行（トークン取得）
├── 02_fetch_data.py    ← Stravaデータ取得
├── 03_coach_bot.py     ← AIコーチアドバイス生成
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
pip install requests python-dotenv openai langchain langchain-openai
```

### Step 3: .envファイルを作成
`.env.example` を `.env` にコピーして値を入力

### Step 4: トークン取得（最初の1回だけ）
```bash
python 01_get_token.py
```
ブラウザが開くので認証 → URLの `code=` 以降をコピー → 貼り付け

### Step 5: 動作確認
```bash
python 02_fetch_data.py
python 03_coach_bot.py
```
