import pandas as pd
from datetime import datetime, timedelta

# CSV読み込み
df = pd.read_csv("youtube_stats.csv", encoding="utf-8-sig", skipinitialspace=True)
df["timestamp"] = pd.to_datetime(df["timestamp"].astype(str).str.strip())
df = df.sort_values("timestamp")

# グループ定義
japan = ["僕が見たかった青空", "AKB48", "乃木坂46", "ME:I", "NiziU"]
korea = ["ILLIT", "LE SSERAFIM", "IVE", "Kep1er", "NewJeans"]

# 今日・前日データ取得
today = df.iloc[-1]
yesterday_date = (today["timestamp"] - timedelta(days=1)).date()
yesterday_rows = df[df["timestamp"].dt.date == yesterday_date]
yesterday = yesterday_rows.iloc[-1] if not yesterday_rows.empty else None

week_ago_date = (today["timestamp"] - timedelta(days=7)).date()
week_ago_rows = df[df["timestamp"].dt.date == week_ago_date]
week_ago = week_ago_rows.iloc[-1] if not week_ago_rows.empty else None

# 差分計算関数
def calc_diff(current, past, group):
    return {
        name: current[name] - past[name]
        for name in group
        if pd.notnull(current[name]) and pd.notnull(past[name])
    }

# HTML表生成関数（← ここに make_table を書く）
def make_table(diff_dict, title):
    ranked = sorted(diff_dict.items(), key=lambda x: x[1], reverse=True)
    rows = "".join(
        f"<tr><td>{i+1}</td><td>{name}</td><td>+{int(val):,}回</td></tr>"
        for i, (name, val) in enumerate(ranked)
    )
    return f"<h2>{title}</h2><table><tr><th>順位</th><th>グループ</th><th>再生数増加</th></tr>{rows}</table>"

# 差分ランキング
if yesterday is not None:
    japan_diff = calc_diff(today, yesterday, japan)
    korea_diff = calc_diff(today, yesterday, korea)

japan_weekly_diff = calc_diff(today, week_ago, japan) if week_ago is not None else {}
korea_weekly_diff = calc_diff(today, week_ago, korea) if week_ago is not None else {}

    # HTML本文の構築
html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>YouTube差分ランキング</title>
    <style>
        body {{ font-family: sans-serif; padding: 2em; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 2em; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: center; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>YouTube再生数差分ランキング</h1>
    <p>最終更新: {today['timestamp'].strftime('%Y年%m月%d日 %H:%M')}</p>

    {make_table(japan_diff, "日本グループ 日別再生数ランキング（1日前との差）")}
    {make_table(japan_weekly_diff, "日本グループ 週間再生数ランキング（7日前との差）") if japan_weekly_diff else "<p>🇯🇵 日本グループの7日前データがありません。</p>"}

    {make_table(korea_diff, "韓国グループ 日別再生数ランキング（1日前との差）")}
    {make_table(korea_weekly_diff, "韓国グループ 週間再生数ランキング（7日前との差）") if korea_weekly_diff else "<p>🇰🇷 韓国グループの7日前データがありません。</p>"}
</body>
</html>
"""

# HTMLファイルとして保存
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ index.html を生成しました。")


print(f"\n📊 {today['timestamp'].strftime('%Y-%m-%d %H:%M')} の日本グループ日別再生数ランキング")
ranked_japan = sorted(japan_diff.items(), key=lambda x: x[1], reverse=True)
for i, (name, diff) in enumerate(ranked_japan, 1):
        print(f"{i}位：{name}（+{int(diff):,}回）")

print(f"\n📊 {today['timestamp'].strftime('%Y-%m-%d %H:%M')} の韓国グループ日別再生数ランキング")
ranked_korea = sorted(korea_diff.items(), key=lambda x: x[1], reverse=True)
for i, (name, diff) in enumerate(ranked_korea, 1):
       print(f"{i}位：{name}（+{int(diff):,}回）")
else:
    print("⚠️ 前日データが見つかりません。差分ランキングを表示できません。")
