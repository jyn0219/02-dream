"""01 清洗与停留识别：data/raw 的原始 AIS → data/clean/stops.csv。

跑完之后屏幕上会打印一份「清洗日志」，每行都是「操作 — 规则 — 理由 — 行数变化」，
可以直接改写进 M2 报告（第 7 讲第 7.1 节的格式）。

运行：python analysis/01_clean.py
预期（默认参数）：215 次停留、56 艘船、合计 512.5 小时、中位数约 76 分钟。
"""

import pandas as pd

from b1core import CLEAN, GAP, RAW, ROOT, TAU, V0, find_stops, load_ais


def main() -> None:
    # 先用原始文件的行数，才能说清每一步删了多少行（只读一列，快）
    n_raw = len(pd.read_csv(RAW, usecols=["mmsi"]))
    df = load_ais()
    n_valid = len(df)

    print("清洗日志（可直接改写进 M2）")
    print(f"1. 读入原始文件 {n_raw:,} 行；timestamp 按「日/月/年」解析，"
          f"按 mmsi + timestamp 排序（排序不改变行数）。")
    print(f"2. 删除 timestamp / mmsi / lat / lon / sog 任一缺失的记录 "
          f"{n_raw - n_valid} 行 → 余 {n_valid:,} 行。")
    print(f"3. 计算同一艘船相邻两条记录的间隔：中位数 {df.dt.median():.0f} 秒，"
          f"超过 {GAP} 分钟的缺口 {int((df.dt > GAP * 60).sum())} 处；"
          f"缺口不删，按规则切断停留。")
    print(f"4. 船型按整艘船取众数（原始数据中 shiptype 为 Undefined 的 "
          f"{int((df.shiptype == 'Undefined').sum()):,} 行不再单独成类）；共 {df.mmsi.nunique()} 艘船。")
    print(f"5. 识别停留：航速门槛 {V0} 节、最短时长 {TAU} 分钟、缺口 {GAP} 分钟。")

    stops = find_stops(df)
    print(f"   → 停留 {len(stops)} 次，涉及 {stops.mmsi.nunique()} 艘船，"
          f"合计 {stops.minutes.sum() / 60:.1f} 小时；"
          f"时长中位数 {stops.minutes.median():.1f} 分钟，"
          f"平均数 {stops.minutes.mean():.1f} 分钟，"
          f"P90 {stops.minutes.quantile(0.9):.1f} 分钟。")
    com = stops[stops.shiptype.isin(["Tanker", "Cargo"])]
    print(f"   → 其中油轮与货船 {len(com)} 次，中位数 {com.minutes.median():.1f} 分钟。")

    CLEAN.mkdir(parents=True, exist_ok=True)
    out = CLEAN / "stops.csv"
    stops.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"\n6. 写出 {out.relative_to(ROOT)}，{len(stops)} 行。")
    print("   自检：与教材的 215 次 / 512.5 小时对得上再往下做；对不上先查第 1–4 步。")


if __name__ == "__main__":
    main()
