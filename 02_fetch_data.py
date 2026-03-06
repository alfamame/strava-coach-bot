"""
02_fetch_data.py
================
Stravaからトレーニングデータを取得するモジュール。
コーチボット（03_coach_bot.py）から呼び出して使います。
"""

import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID     = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")


# ============================================================
# 認証：アクセストークンを自動更新
# ============================================================

def get_access_token():
    """リフレッシュトークンを使って新しいアクセストークンを取得"""
    response = requests.post(
        url="https://www.strava.com/api/v3/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token",
        }
    )
    data = response.json()
    if "access_token" not in data:
        raise Exception(f"トークン更新失敗: {data}")
    return data["access_token"]


# ============================================================
# データ取得関数
# ============================================================

def get_recent_activities(access_token, days=7):
    """直近N日間のアクティビティ一覧を取得"""
    after_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        headers=headers,
        params={
            "after": after_timestamp,
            "per_page": 30
        }
    )
    return response.json()


def get_activity_zones(access_token, activity_id):
    """アクティビティの心拍ゾーン時間を取得（Stravaサブスク必要）"""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"https://www.strava.com/api/v3/activities/{activity_id}/zones",
        headers=headers
    )
    return response.json()


def get_athlete_info(access_token):
    """アスリート（自分）の情報を取得"""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        "https://www.strava.com/api/v3/athlete",
        headers=headers
    )
    return response.json()


# ============================================================
# データ整形：コーチボット用のサマリーを作成
# ============================================================

def build_training_summary(days=7):
    """
    直近N日間のトレーニングデータをまとめてコーチボット用テキストを生成する
    
    Returns:
        dict: {
            "summary_text": str,   # LLMに渡すテキスト
            "activities": list,    # 生データ
        }
    """
    print(f"Stravaからデータ取得中（直近{days}日間）...")
    
    access_token = get_access_token()
    activities   = get_recent_activities(access_token, days=days)
    athlete      = get_athlete_info(access_token)

    if not activities:
        return {
            "summary_text": f"直近{days}日間にアクティビティはありませんでした。",
            "activities": []
        }

    # アクティビティを種別ごとに集計
    ride_summary = []
    run_summary  = []

    for act in activities:
        sport   = act.get("sport_type", act.get("type", "Unknown"))
        name    = act.get("name", "無名")
        dist_km = round(act.get("distance", 0) / 1000, 1)
        time_min = round(act.get("moving_time", 0) / 60)
        elev    = round(act.get("total_elevation_gain", 0))
        avg_hr  = act.get("average_heartrate")
        max_hr  = act.get("max_heartrate")
        avg_cad = act.get("average_cadence")
        date    = act.get("start_date_local", "")[:10]

        line = (
            f"  [{date}] {name} / {dist_km}km / {time_min}分"
            f" / 獲得標高{elev}m"
        )
        if avg_hr:
            line += f" / 平均心拍{avg_hr:.0f}bpm（最大{max_hr:.0f}bpm）"
        if avg_cad:
            line += f" / 平均ケイデンス{avg_cad:.0f}rpm"

        if "Ride" in sport or "Cycle" in sport:
            ride_summary.append(line)
        elif "Run" in sport or "Jog" in sport:
            run_summary.append(line)

    # サマリーテキストを組み立て
    lines = []
    lines.append(f"【直近{days}日間のトレーニングサマリー】")
    lines.append(f"アスリート: {athlete.get('firstname','')} {athlete.get('lastname','')}")
    lines.append("")

    if ride_summary:
        lines.append(f"■ ライド（{len(ride_summary)}回）")
        lines.extend(ride_summary)
        lines.append("")

    if run_summary:
        lines.append(f"■ ラン・ジョグ（{len(run_summary)}回）")
        lines.extend(run_summary)
        lines.append("")

    # 合計統計
    total_dist = sum(a.get("distance", 0) for a in activities) / 1000
    total_time = sum(a.get("moving_time", 0) for a in activities) / 3600
    total_elev = sum(a.get("total_elevation_gain", 0) for a in activities)

    lines.append(f"■ 合計")
    lines.append(f"  距離: {total_dist:.1f}km / 時間: {total_time:.1f}h / 獲得標高: {total_elev:.0f}m")

    summary_text = "\n".join(lines)
    
    return {
        "summary_text": summary_text,
        "activities": activities,
    }


# ============================================================
# 単体テスト用
# ============================================================

if __name__ == "__main__":
    result = build_training_summary(days=7)
    print(result["summary_text"])
    print(f"\n取得アクティビティ数: {len(result['activities'])}件")
