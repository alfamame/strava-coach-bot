"""
03_coach_bot.py
===============
AIパーソナルコーチBot（Claude API版）
Stravaのトレーニングデータを読み込み、
LangChain + Claude APIを使って今日のアドバイスを生成します。

使い方:
    python 03_coach_bot.py

必要なライブラリ:
    pip install langchain langchain-anthropic anthropic python-dotenv
"""

import os
from datetime import date
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

from importlib import import_module
fetch_data = import_module("02_fetch_data")
build_training_summary = fetch_data.build_training_summary

send_email_module = import_module("04_send_email")
send_coach_advice = send_email_module.send_coach_advice

load_dotenv()


# ============================================================
# コーチBot設定
# ============================================================

# アスリートプロフィール（.envから読み込む）
def build_athlete_profile() -> str:
    return f"""【アスリートプロフィール】
- 年齢: {os.getenv('ATHLETE_AGE')}歳 {os.getenv('ATHLETE_GENDER')}
- 体重: {os.getenv('ATHLETE_WEIGHT_KG')}kg / 体脂肪率: {os.getenv('ATHLETE_BODY_FAT_PCT')}%
- VO2Max: {os.getenv('ATHLETE_VO2MAX')}（ガーミン計測）
- ガーミン持久力スコア: {os.getenv('ATHLETE_ENDURANCE_LEVEL')}
- 主な目標:
  {os.getenv('ATHLETE_GOALS')}

【週間トレーニング計画】
  {os.getenv('ATHLETE_TRAINING_PLAN')}

【注意点・体の状態】
  {os.getenv('ATHLETE_NOTES')}
"""

ATHLETE_PROFILE = build_athlete_profile()

# ============================================================
# プロンプトテンプレート
# ============================================================

COACH_PROMPT = ChatPromptTemplate.from_template("""
あなたは経験豊富なパーソナルトレーナー兼サイクリングコーチです。
以下のアスリート情報とトレーニングデータをもとに、今日のアドバイスを日本語で提供してください。

{athlete_profile}

{training_summary}

【今日の日付】: {today}

---

以下の観点でアドバイスをまとめてください：

1. **直近のトレーニング状況の評価**
   - 疲労度はどの程度か
   - Zone配分は適切か

2. **今日のおすすめトレーニング**
   - 具体的なメニューと強度
   - 実施する場合の注意点

3. **今週の残りのスケジュール提案**
   - ライド・ラン・筋トレのバランス

4. **体のケアアドバイス**
   - 腰・股関節・体幹など気をつけること

アドバイスは具体的で実践しやすい内容にしてください。
""")


# ============================================================
# メイン処理
# ============================================================

def run_coach_bot():
    print("=" * 60)
    print("🚴 パーソナルコーチBot 起動中（Claude API版）...")
    print("=" * 60)
    print()

    # Step 1: Stravaデータを取得
    try:
        training_data = build_training_summary(days=7)
        summary_text = training_data["summary_text"]
        print("✅ Stravaデータ取得完了")
        print()
        print(summary_text)
        print()
    except Exception as e:
        print(f"⚠️ Stravaデータ取得エラー: {e}")
        print("サンプルデータで続行します...")
        summary_text = "直近7日間のデータが取得できませんでした。"

    # Step 2: Claude APIでアドバイス生成
    print("=" * 60)
    print("🤖 Claudeがアドバイスを生成中...")
    print("=" * 60)
    print()

    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        temperature=0.7,
        max_tokens=4096,
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    chain = COACH_PROMPT | llm

    response = chain.invoke({
        "athlete_profile": ATHLETE_PROFILE,
        "training_summary": summary_text,
        "today": date.today().strftime("%Y年%m月%d日"),
    })

    print(response.content)
    print()
    print("=" * 60)
    print("✅ アドバイス生成完了")
    print("=" * 60)

    # メール送信
    try:
        send_coach_advice(response.content)
        print(f"✅ メール送信完了: {os.getenv('RECIPIENT_EMAIL')}")
    except Exception as e:
        print(f"⚠️ メール送信失敗: {e}")

    return response.content


if __name__ == "__main__":
    run_coach_bot()
