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

today_date_str = today["timestamp"].strftime("%Y年%m月%d日")
yesterday_date_str = yesterday["timestamp"].strftime("%Y年%m月%d日") if yesterday is not None else "前日データなし"
week_ago_date_str = week_ago["timestamp"].strftime("%Y年%m月%d日") if week_ago is not None else "7日前データなし"

# 差分計算関数
def calc_diff(current, past, group):
        return {
            name: current[name] - past[name]
            for name in group
            if pd.notnull(current[name]) and pd.notnull(past[name])
        }

# HTML表生成関数（← ここに make_table を書く）
def make_table(diff_dict, title):
    if not diff_dict:
        return "<p>データがありません。</p>"
    ranked = sorted(diff_dict.items(), key=lambda x: x[1], reverse=True)
    rows = "".join(
        f"<tr><td>{i+1}</td><td>{name}</td><td>{'+{:,}回'.format(val) if val != 0 else '未更新'}</td></tr>"
        for i, (name, val) in enumerate(ranked)
    )
    return f"<table><tr><th>順位</th><th>グループ</th><th>再生数増加</th></tr>{rows}</table>"

# 差分ランキング
if yesterday is not None:
# 差分計算と表示
    japan_diff = calc_diff(today, yesterday, japan)
    korea_diff = calc_diff(today, yesterday, korea)

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

japan_weekly_diff = calc_diff(today, week_ago, japan) if week_ago is not None else {}
korea_weekly_diff = calc_diff(today, week_ago, korea) if week_ago is not None else {}

# HTML本文の構築
html = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>YouTube差分ランキング</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script async defer src="https://scripts.simpleanalyticscdn.com/latest.js"></script>
        <style>
            body {{
                font-family: "Helvetica Neue", sans-serif;
                margin: 0;
                padding: 1.5em;
                line-height: 1.6;
                background-color: #fff;
                color: #333;
            }}

            h1, h2 {{
                margin-top: 1.5em;
                font-weight: 600;
                font-size: 1.2em;
            }}

            .table-container {{
                overflow-x: auto;
                margin-bottom: 2em;
                border: 1px solid #ddd;
                border-radius: 6px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                min-width: 320px;
            }}

            th, td {{
                padding: 10px 6px;
                border-bottom: 1px solid #eee;
                border-right: 1px solid #ddd;  /* ← ここが縦線 */
                text-align: center;
                font-size: 0.95em;
                word-break: break-word;
            }}

            td:last-child, th:last-child {{
            border-right: none;  /* ← 最後の列は縦線なし */

            th {{
                background-color: #f9f9f9;
                font-weight: 500;
            }}

            @media screen and (max-width: 600px) {{
                body {{
                    padding: 1em;
                }}

                h1, h2 {{
                    font-size: 1em;
                }}

                th, td {{
                    padding: 8px 4px;
                    font-size: 0.85em;
                }}

                table {{
                    font-size: 0.9em;
                }}
            }}
        </style>
    </head>
    <body>
        <h1>YouTube再生数差分ランキング</h1>
        <p>最終更新: {today['timestamp'].strftime('%Y年%m月%d日 %H:%M')}</p>
        
        <h2>日本グループ 日別再生数ランキング</h2>
        <h3>（前回の更新日 → {today_date_str} の差分）</h3>
        <div class="table-container">
            {make_table(japan_diff, "")}
        </div>

        <h2>日本グループ 週間再生数ランキング</h2>
        <h3>（{week_ago_date_str} → {today_date_str} の差分）</h3>
        <div class="table-container">
            {make_table(japan_weekly_diff, "") if japan_weekly_diff else "<p>データがありません。</p>"}
        </div>

        <h2>韓国グループ 日別再生数ランキング</h2>
        <h3>（前回の更新日 → {today_date_str} の差分）</h3>
        <div class="table-container">
            {make_table(korea_diff, "")}
        </div>

        <h2>韓国グループ 週間再生数ランキング</h2>
        <h3>（{week_ago_date_str} → {today_date_str} の差分）</h3>
        <div class="table-container">
            {make_table(korea_weekly_diff, "") if korea_weekly_diff else "<p>データがありません。</p>"}
        </div>
    </body>
    </html>
    """

# HTMLファイルとして保存
with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html)
print("✅ docs/index.html を生成しました。")

