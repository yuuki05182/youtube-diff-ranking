import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pytz import timezone
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")

# 日本グループ
JAPAN_CHANNELS = {
    '僕が見たかった青空': 'UC-_iQWdEZY66nGGaHH0Ygmg',
    'AKB48': 'UCxjXU89x6owat9dA8Z-bzdw',
    '乃木坂46': 'UCUzpZpX2wRYOk3J8QTFGxDg',
    'NiziU': 'UCHp2q2i85qt_9nn2H7AvGOw',
    'ME:I': 'UCvTsv4KmVuBdECI08_HR87Q'
}

# 韓国グループ
KOREA_CHANNELS = {
    'ILLIT': 'UCEpFoWeCMCo5z3EvWaz6hQQ',
    'IVE': 'UC-Fnix71vRP64WXeo0ikd0Q',
    'LE SSERAFIM': 'UCs-QBT4qkj_YiQw1ZntDO3g',
    'Kep1er': 'UC8whlOg70m2Yr3qSMjUhh0g',
    'NewJeans': 'UCMki_UkHb4qSc0qyEcOHHJw'
}

ALL_CHANNELS = {**JAPAN_CHANNELS, **KOREA_CHANNELS}
CSV_FILE = 'youtube_stats.csv'
jst = timezone('Asia/Tokyo')
now = datetime.now(jst)
timestamp = now.strftime('%Y-%m-%dT%H:%M')

expected_columns = ['timestamp'] + list(ALL_CHANNELS.keys())

# CSV読み込み（列名補正付き）
try:
    df = pd.read_csv(CSV_FILE, encoding='utf-8-sig', skipinitialspace=True)
    df['timestamp'] = df['timestamp'].astype(str).str.strip()
    
    if set(df.columns) == set(expected_columns):
        df = df.loc[:, expected_columns]
    else:
        print("⚠️ 列構成が一致しないため、CSVを初期化します")
        df = pd.DataFrame(columns=expected_columns)

except FileNotFoundError:
    df = pd.DataFrame(columns=expected_columns)

# APIから再生数取得
def get_view_count(channel_id):
    url = f'https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={API_KEY}'
    response = requests.get(url)
    data = response.json()
    try:
        return int(data['items'][0]['statistics']['viewCount'])
    except (KeyError, IndexError):
        return None

# 今日のデータ取得
new_row = {'timestamp': timestamp}
for name, cid in ALL_CHANNELS.items():
    new_row[name] = get_view_count(cid)

# 差分計算（前日・1週間前）
diffs_japan = {}
weekly_diffs_japan = {}
diffs_korea = {}
weekly_diffs_korea = {}

today_date = now.strftime('%Y-%m-%d')
yesterday_date = (now - timedelta(days=1)).strftime('%Y-%m-%d')
week_ago_date = (now - timedelta(days=7)).strftime('%Y-%m-%d')

# 前日行の取得
yesterday_rows = df[df['timestamp'].str.startswith(yesterday_date)]
yesterday_row = yesterday_rows.iloc[-1] if not yesterday_rows.empty else None

# 1週間前の行の取得
week_rows = df[df['timestamp'].str.startswith(week_ago_date)]
week_row = week_rows.iloc[-1] if not week_rows.empty else None

# 差分計算（前日）
if yesterday_row is not None:
    for name in JAPAN_CHANNELS.keys():
        if pd.notnull(new_row[name]) and pd.notnull(yesterday_row[name]):
            diffs_japan[name] = new_row[name] - yesterday_row[name]
    for name in KOREA_CHANNELS.keys():
        if pd.notnull(new_row[name]) and pd.notnull(yesterday_row[name]):
            diffs_korea[name] = new_row[name] - yesterday_row[name]

# 差分計算（1週間前）
if week_row is not None:
    for name in JAPAN_CHANNELS.keys():
        if pd.notnull(new_row[name]) and pd.notnull(week_row[name]):
            weekly_diffs_japan[name] = new_row[name] - week_row[name]
    for name in KOREA_CHANNELS.keys():
        if pd.notnull(new_row[name]) and pd.notnull(week_row[name]):
            weekly_diffs_korea[name] = new_row[name] - week_row[name]

# 重複除去と追加は差分計算の後に行う
today_date = now.strftime('%Y-%m-%d')
df = df[~df['timestamp'].str.startswith(today_date)]
df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

# 20日以上前の行を削除
df['timestamp_dt'] = pd.to_datetime(df['timestamp'], errors='coerce')
ten_days_ago = now - timedelta(days=20)
ten_days_ago = ten_days_ago.replace(tzinfo=None)
df = df[df['timestamp_dt'] >= ten_days_ago]
df = df.drop(columns=['timestamp_dt'])

# 整形（整数型へ変換）
for name in ALL_CHANNELS.keys():
    df[name] = pd.to_numeric(df[name], errors='coerce').astype('Int64')

# 保存（小数点なし）
df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig', float_format='%.0f')

# ランキング表示（日本）
print(f"\n📊 {timestamp} の日本グループ日別再生数ランキング")
if diffs_japan:
    ranked_japan = sorted(diffs_japan.items(), key=lambda x: x[1], reverse=True)
    for i, (name, diff) in enumerate(ranked_japan, 1):
        status = f"+{int(diff):,}回" if diff != 0 else "未更新"
        print(f"{i}位：{name}（{status}）")
else:
    print("前回データがないため、日本グループの差分ランキングは表示できません。")

# 日本グループ：週差ランキング
print(f"\n📊 {timestamp} の日本グループ週間再生数差ランキング（1週間前との差）")
if weekly_diffs_japan:
    ranked_week_japan = sorted(weekly_diffs_japan.items(), key=lambda x: x[1], reverse=True)
    for i, (name, diff) in enumerate(ranked_week_japan, 1):
        print(f"{i}位：{name}（+{int(diff):,}回）")
else:
    print("1週間前のデータがないため、日本グループの週差ランキングは表示できません。")

# ランキング表示（韓国）
print(f"\n📊 {timestamp} の韓国グループ日別再生数ランキング")
if diffs_korea:
    ranked_korea = sorted(diffs_korea.items(), key=lambda x: x[1], reverse=True)
    for i, (name, diff) in enumerate(ranked_korea, 1):
        status = f"+{int(diff):,}回" if diff != 0 else "未更新"
        print(f"{i}位：{name}（{status}）")
else:
    print("前回データがないため、韓国グループの差分ランキングは表示できません。")

# 韓国グループ：週差ランキング
print(f"\n📊 {timestamp} の韓国グループ週間再生数差ランキング（1週間前との差）")
if weekly_diffs_korea:
    ranked_week_korea = sorted(weekly_diffs_korea.items(), key=lambda x: x[1], reverse=True)
    for i, (name, diff) in enumerate(ranked_week_korea, 1):
        print(f"{i}位：{name}（+{int(diff):,}回）")
else:
    print("1週間前のデータがないため、韓国グループの週差ランキングは表示できません。")

print("\n🔍 差分検証ログ（日本）")
if yesterday_row is not None:
    for name in JAPAN_CHANNELS.keys():
        new_val = new_row[name]
        prev_val = yesterday_row[name]
        diff = new_val - prev_val if pd.notnull(new_val) and pd.notnull(prev_val) else 'N/A'
        print(f"{name}: new={new_val}, prev={prev_val}, diff={diff}")
else:
    print("前日データが存在しないため、日本グループの差分検証はできません。")

print("\n🔍 差分検証ログ（韓国）")
if yesterday_row is not None:
    for name in KOREA_CHANNELS.keys():
        new_val = new_row[name]
        prev_val = yesterday_row[name]
        diff = new_val - prev_val if pd.notnull(new_val) and pd.notnull(prev_val) else 'N/A'
        print(f"{name}: new={new_val}, prev={prev_val}, diff={diff}")
else:
    print("前日データが存在しないため、韓国グループの差分検証はできません。")

print("🔍 new_row =", new_row)

print("📁 現在の保存先 =", os.path.abspath(CSV_FILE))

print("📅 timestamp =", timestamp)
print("🕒 実行時刻 =", datetime.now())

print(f"📅 実行時刻：{timestamp}（推奨：毎日11:00 JST以降）")

    
