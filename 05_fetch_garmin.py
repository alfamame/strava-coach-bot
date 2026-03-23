"""
05_fetch_garmin.py
==================
Garmin Connectから睡眠・Body Battery・HRV・ストレスデータを取得するモジュール。
03_coach_bot.py から呼び出して使います。

注意: garminconnect は非公式ライブラリです。個人利用のみ推奨。

使い方:
    python 05_fetch_garmin.py

必要なライブラリ:
    pip install garminconnect
"""

import os
import base64
import tarfile
import io
import tempfile
from datetime import date, timedelta
from dotenv import load_dotenv
from garminconnect import Garmin, GarminConnectAuthenticationError

load_dotenv()

GARMIN_EMAIL    = os.getenv("GARMIN_EMAIL")
GARMIN_PASSWORD = os.getenv("GARMIN_PASSWORD")


# ============================================================
# 認証
# ============================================================

def get_garmin_client() -> Garmin:
    """Garmin Connectにログインしてクライアントを返す。

    GARMIN_TOKENS 環境変数（base64エンコード済みトークン）があれば
    それを使用してログインをスキップする（GitHub Actions用）。
    なければメール/パスワードでログインする（ローカル用）。
    """
    garmin_tokens_b64 = os.getenv("GARMIN_TOKENS")

    if garmin_tokens_b64:
        token_bytes = base64.b64decode(garmin_tokens_b64)
        tmpdir = tempfile.mkdtemp()
        with tarfile.open(fileobj=io.BytesIO(token_bytes), mode="r:gz") as tar:
            tar.extractall(tmpdir)
        client = Garmin()
        client.garth.load(tmpdir)
        return client

    client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
    client.login()
    return client


# ============================================================
# データ取得関数
# ============================================================

def get_sleep_data(client: Garmin, target_date: str) -> dict:
    """指定日の睡眠データを取得"""
    try:
        data = client.get_sleep_data(target_date)
        daily = data.get("dailySleepDTO", {})
        return {
            "sleep_score": daily.get("sleepScores", {}).get("overall", {}).get("value"),
            "total_sleep_seconds": daily.get("sleepTimeSeconds"),
            "deep_sleep_seconds": daily.get("deepSleepSeconds"),
            "light_sleep_seconds": daily.get("lightSleepSeconds"),
            "rem_sleep_seconds": daily.get("remSleepSeconds"),
            "awake_seconds": daily.get("awakeSleepSeconds"),
        }
    except Exception as e:
        print(f"  ⚠️ 睡眠データ取得失敗: {e}")
        return {}


def get_body_battery(client: Garmin, target_date: str) -> dict:
    """指定日のBody Batteryデータを取得"""
    try:
        data = client.get_body_battery(target_date)
        if data and len(data) > 0:
            charged = data[0].get("charged")
            drained = data[0].get("drained")
            return {"charged": charged, "drained": drained}
        return {}
    except Exception as e:
        print(f"  ⚠️ Body Batteryデータ取得失敗: {e}")
        return {}


def get_hrv_data(client: Garmin, target_date: str) -> dict:
    """指定日のHRV（心拍変動）データを取得"""
    try:
        data = client.get_hrv_data(target_date)
        summary = data.get("hrvSummary", {})
        return {
            "weekly_avg": summary.get("weeklyAvg"),
            "last_night_avg": summary.get("lastNight"),
            "status": summary.get("hrvSummaryStatus"),
        }
    except Exception as e:
        print(f"  ⚠️ HRVデータ取得失敗: {e}")
        return {}


def get_stress_data(client: Garmin, target_date: str) -> dict:
    """指定日のストレスデータを取得"""
    try:
        data = client.get_stress_data(target_date)
        return {
            "avg_stress_level": data.get("avgStressLevel"),
            "max_stress_level": data.get("maxStressLevel"),
            "rest_stress_duration": data.get("restStressDuration"),
        }
    except Exception as e:
        print(f"  ⚠️ ストレスデータ取得失敗: {e}")
        return {}


def get_activities(client: Garmin, target_date: str) -> list:
    """指定日のアクティビティデータを取得（Strava重複項目は除外）"""
    try:
        activities = client.get_activities_by_date(target_date, target_date)
        result = []
        for act in activities:
            result.append({
                "name": act.get("activityName"),
                "type": act.get("activityType", {}).get("typeKey"),
                "calories": act.get("calories"),
                "aerobic_training_effect": act.get("aerobicTrainingEffect"),
                "anaerobic_training_effect": act.get("anaerobicTrainingEffect"),
                "aerobic_te_label": act.get("aerobicTrainingEffectMessage"),
                "anaerobic_te_label": act.get("anaerobicTrainingEffectMessage"),
            })
        return result
    except Exception as e:
        print(f"  ⚠️ アクティビティデータ取得失敗: {e}")
        return []


# ============================================================
# サマリー生成
# ============================================================

def build_garmin_summary(days: int = 1) -> dict:
    """
    直近N日間のGarminデータをまとめてコーチボット用テキストを生成する

    Returns:
        dict: {
            "summary_text": str,   # LLMに渡すテキスト
            "raw": dict,           # 生データ
        }
    """
    print("Garmin Connectからデータ取得中...")

    client = get_garmin_client()
    today = date.today()
    yesterday = today - timedelta(days=1)
    target = yesterday.strftime("%Y-%m-%d")  # 昨日のデータ（当日基準）

    print(f"  対象日: {target}（睡眠は直近{days}日間）")

    # 睡眠は直近days日分を取得
    sleep_list = []
    for i in range(days):
        d = (yesterday - timedelta(days=i)).strftime("%Y-%m-%d")
        s = get_sleep_data(client, d)
        if s:
            sleep_list.append((d, s))

    battery    = get_body_battery(client, target)
    hrv        = get_hrv_data(client, target)
    stress     = get_stress_data(client, target)
    activities = get_activities(client, target)

    # テキスト生成
    lines = [f"【Garminデータ（睡眠: 直近{days}日間 / その他: {target}）】"]

    # 睡眠（複数日）
    if sleep_list:
        lines.append(f"■ 睡眠（直近{days}日間）")
        for d, sleep in sleep_list:
            score     = sleep.get("sleep_score", "不明")
            total_h   = round(sleep.get("total_sleep_seconds", 0) / 3600, 1)
            deep_min  = round(sleep.get("deep_sleep_seconds", 0) / 60)
            rem_min   = round(sleep.get("rem_sleep_seconds", 0) / 60)
            awake_min = round(sleep.get("awake_seconds", 0) / 60)
            lines.append(
                f"  [{d}] スコア{score}点 / {total_h}時間"
                f"（深い睡眠: {deep_min}分 / REM: {rem_min}分 / 覚醒: {awake_min}分）"
            )
    else:
        lines.append("■ 睡眠: データなし")

    # Body Battery
    if battery:
        charged = battery.get("charged", "不明")
        drained = battery.get("drained", "不明")
        lines.append(f"■ Body Battery: 充電 {charged} / 消費 {drained}")
    else:
        lines.append("■ Body Battery: データなし")

    # HRV
    if hrv:
        last_night = hrv.get("last_night_avg") or "不明"
        weekly_avg = hrv.get("weekly_avg") or "不明"
        status     = hrv.get("status") or ""
        if last_night != "不明":
            lines.append(f"■ HRV（心拍変動）: 昨夜平均 {last_night}ms / 週平均 {weekly_avg}ms（状態: {status}）")
        else:
            lines.append(f"■ HRV（心拍変動）: 週平均 {weekly_avg}ms（状態: {status}）※昨夜データなし")
    else:
        lines.append("■ HRV: データなし")

    # ストレス
    if stress:
        avg_stress = stress.get("avg_stress_level", "不明")
        max_stress = stress.get("max_stress_level", "不明")
        lines.append(f"■ ストレス: 平均 {avg_stress} / 最大 {max_stress}")
    else:
        lines.append("■ ストレス: データなし")

    # アクティビティ（Strava重複項目除外・Garmin固有のみ）
    if activities:
        lines.append(f"■ アクティビティ（トレーニング効果・カロリー）")
        for act in activities:
            name    = act.get("name") or act.get("type") or "不明"
            cal     = act.get("calories")
            ae      = act.get("aerobic_training_effect")
            an      = act.get("anaerobic_training_effect")
            ae_lbl  = act.get("aerobic_te_label") or ""
            an_lbl  = act.get("anaerobic_te_label") or ""
            parts = [f"  {name}"]
            if cal:
                parts.append(f"カロリー: {cal}kcal")
            if ae is not None:
                parts.append(f"有酸素TE: {ae}（{ae_lbl}）")
            if an is not None:
                parts.append(f"無酸素TE: {an}（{an_lbl}）")
            lines.append(" / ".join(parts))
    else:
        lines.append("■ アクティビティ: データなし")

    summary_text = "\n".join(lines)

    return {
        "summary_text": summary_text,
        "raw": {
            "sleep": sleep_list,
            "battery": battery,
            "hrv": hrv,
            "stress": stress,
            "activities": activities,
        }
    }


# ============================================================
# 単体テスト用
# ============================================================

if __name__ == "__main__":
    result = build_garmin_summary()
    print(result["summary_text"])
