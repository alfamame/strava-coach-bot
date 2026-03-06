# Strava パーソナルコーチBot - プロジェクト情報

## プロジェクト概要
StravaのトレーニングデータをClaude APIで分析し、パーソナルコーチとしてアドバイスを生成するBot。

## ファイル構成
- `01_get_token.py` - Strava OAuthトークン取得（初回1回だけ実行）
- `02_fetch_data.py` - Stravaからトレーニングデータ取得・整形
- `03_coach_bot.py` - Claude APIでコーチアドバイス生成（メイン）
- `.env` - APIキー保存（Gitに上げない）
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
- LangChain（langchain-anthropic）
- python-dotenv（環境変数管理）

## アスリートプロフィール（03_coach_bot.py内に定義）
- 52歳男性、体重70kg、体脂肪率27%
- VO2Max: 47（ガーミン計測）
- 目標: Stravaセグメント上位10%、週100kmロングライド、体脂肪減少
- 注意: 腰痛（デッドリフト）、猫背、体幹弱め

## 環境変数（.envに設定）
```
STRAVA_CLIENT_ID=
STRAVA_CLIENT_SECRET=
STRAVA_REFRESH_TOKEN=    # 01_get_token.py実行後に取得
ANTHROPIC_API_KEY=
```

## 開発メモ
- 03_coach_bot.py の `ATHLETE_PROFILE` を編集してプロフィール更新
- 取得日数はデフォルト7日間（`build_training_summary(days=7)`）
- 02_fetch_data.py は 03_coach_bot.py から `fetch_data` としてimportされる
