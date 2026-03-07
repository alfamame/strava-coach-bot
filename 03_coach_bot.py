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

# あなたの情報（プロンプトに組み込む固定情報）
ATHLETE_PROFILE = """
【アスリートプロフィール】
- 年齢: 52歳 男性
- 体重: 70kg / 体脂肪率: 27%
- VO2Max: 47（ガーミン計測）
- ガーミン持久力スコア: 高度な経験者
- 主な目標:
  1. ロードバイクでStravaセグメント上位10%に入る
  2. 週100kmロングライドの完走
  3. 体脂肪率を落としながら筋力向上

【週間トレーニング計画】
- Zone2以下: 週4回（基礎有酸素）
- Zone3以上: 週2回（高強度）
- 休息日: 週1回
- 筋トレ: デッドリフト・スクワット（2日おき）

【注意点・体の状態】
- デッドリフトで腰痛が出やすい（フォーム改善中）
- 猫背気味でデスクワーク多め
- 背筋が弱め、体幹のブレあり
- 股関節の使い方を改善中
"""

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
