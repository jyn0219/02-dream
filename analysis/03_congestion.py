"""03 拥堵指标与敏感性：把「停留」变成能写进报告的数字。

读 data/clean/stops.csv（由 01 生成），重新读原始数据做 3×3 参数敏感性，写出：

  figures/sensitivity.csv    M3 要带的参数敏感性表（v0 × tau 九组）
  narrative/key_numbers.md   报告里要用的全部数字，改参数后重跑就同步

运行：python analysis/03_congestion.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from b1core import CLEAN, COMMERCIAL, FIGS, NARRATIVE, find_stops, load_ais

DAY_MIN = 24 * 60


def read_stops() -> pd.DataFrame:
    return pd.read_csv(CLEAN / "stops.csv", parse_dates=["start", "end"])


def occupancy(stops: pd.DataFrame) -> tuple[float, int]:
    """存量：平均在停船数（按停留总时长／一天）与最大同时在停船数（事件扫描）。"""
    mean_l = stops.minutes.sum() / DAY_MIN
    events = pd.concat([
        pd.DataFrame({"t": stops.start, "d": 1}),
        pd.DataFrame({"t": stops.end, "d": -1}),
    ]).sort_values("t", kind="stable")
    max_l = int(events.d.cumsum().max())
    return mean_l, max_l


def sensitivity() -> pd.DataFrame:
    """两个门槛的 3×3 表：次数会随 tau 机械变化，商船在港船时才基本稳定。"""
    df = load_ais()
    rows = []
    for tau in (10, 30, 60):
        for v0 in (0.2, 0.5, 1.0):
            s = find_stops(df, v0=v0, tau=tau)
            com = s[s.shiptype.isin(COMMERCIAL)]
            rows.append({
                "v0_节": v0, "tau_分钟": tau,
                "全部停留次数": len(s),
                "商船停留次数": len(com),
                "商船在港船时": round(com.minutes.sum() / 60, 1),
                "平均在停商船数": round(com.minutes.sum() / DAY_MIN, 2),
            })
    return pd.DataFrame(rows)


def one_at_a_time(base_hours: float) -> pd.DataFrame:
    """一次只改一个参数（第 13 讲第 6.2 节的模板）：看结论对哪个参数最敏感。

    基准为 v0=0.5、tau=30；其余情形各改一个参数，记录商船在港船时相对基准的变化。
    """
    df = load_ais()
    rows = []

    def add(param: str, value: float, v0: float, tau: float, note: str = "") -> None:
        com = find_stops(df, v0=v0, tau=tau)
        com = com[com.shiptype.isin(COMMERCIAL)]
        hours = com.minutes.sum() / 60
        rows.append({
            "参数": param,
            "取值": value,
            "商船在港船时": round(hours, 1),
            "相对基准": f"{(hours / base_hours - 1) * 100:+.1f}%",
            "备注": note,
        })

    add("最短时长 tau（分钟）", 10, 0.5, 10, "停 10 分钟就算停留")
    add("最短时长 tau（分钟）", 60, 0.5, 60, "停 1 小时才算停留")
    add("航速门槛 v0（节）", 0.2, 0.2, 30, "更容易把漂航算成停")
    add("航速门槛 v0（节）", 1.0, 1.0, 30, "更容易把慢速航行排除")
    # 基准行放到最前面
    base = {"参数": "基准", "取值": "—", "商船在港船时": round(base_hours, 1),
            "相对基准": "+0.0%", "备注": "v0=0.5 节、tau=30 分钟、gap=10 分钟"}
    return pd.DataFrame([base] + rows)


def compare_reference(stops: pd.DataFrame, path: Path) -> None:
    """和教师给定的 3 次停留对照：起止时间误差都 ≤10 分钟才算过关（任务包 4 分档）。

    对照表格式（csv，表头固定）：mmsi,start,end；时间写成 2017-07-05 08:30:00。
    """
    ref = pd.read_csv(path, parse_dates=["start", "end"])
    print(f"\n与真值对照：{path.name}（{len(ref)} 次）")
    n_pass = 0
    for _, r in ref.iterrows():
        cand = stops[stops.mmsi == r.mmsi]
        if cand.empty:
            print(f"  MMSI {r.mmsi}：没有识别出停留 → 不通过")
            continue
        overlap = (np.minimum(cand.end, r.end) - np.maximum(cand.start, r.start)).dt.total_seconds()
        best = cand.loc[overlap.idxmax()]
        err_start = abs((best.start - r.start).total_seconds()) / 60
        err_end = abs((best.end - r.end).total_seconds()) / 60
        ok = max(err_start, err_end) <= 10
        n_pass += int(ok)
        print(f"  MMSI {r.mmsi}：起 {err_start:.1f} 分、止 {err_end:.1f} 分 → {'通过' if ok else '不通过'}")
    print(f"  合计 {n_pass}/{len(ref)} 通过（判据：起止误差 ≤10 分钟）")


def md_table(df: pd.DataFrame) -> str:
    """把 DataFrame 转成 Markdown 表格（不依赖 tabulate，环境里不一定装）。"""
    head = "| " + " | ".join(df.columns) + " |"
    sep = "|" + "|".join(["---"] * len(df.columns)) + "|"
    rows = ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join([head, sep, *rows])


def main() -> None:
    stops = read_stops()
    com = stops[stops.shiptype.isin(COMMERCIAL)]

    mean_l, max_l = occupancy(stops)
    com_mean_l, com_max_l = occupancy(com)
    lam = len(stops) / 24
    w = stops.minutes.mean() / 60

    print(f"读入 {len(stops)} 次停留，其中商船 {len(com)} 次\n")
    print("三种量法（默认参数，全部船型）")
    print(f"  存量：平均 {mean_l:.2f} 艘在停，最多 {max_l} 艘")
    print(f"  流量：每小时 {lam:.2f} 次（一天 {len(stops)} 次）")
    print(f"  时长：平均 {w:.2f} 小时／次，中位数 {stops.minutes.median() / 60:.2f} 小时")
    print(f"  利特尔法则：L = λW = {lam:.2f} × {w:.2f} = {lam * w:.2f}（存量 {mean_l:.2f}）")
    print(f"  只算商船：平均在停 {com_mean_l:.2f} 艘，最多 {com_max_l} 艘，"
          f"在港船时 {com.minutes.sum() / 60:.1f} 船·小时／天\n")

    grid = sensitivity()
    FIGS.mkdir(exist_ok=True)
    grid.to_csv(FIGS / "sensitivity.csv", index=False, encoding="utf-8-sig")

    fixed = grid[grid.v0_节 == 0.5]
    print("敏感性：tau 从 10 到 60 分钟，全部停留次数 "
          f"{int(fixed.iloc[0].全部停留次数)} → {int(fixed.iloc[-1].全部停留次数)}"
          "（机械截断，不是港口的变化）")
    print(f"  商船在港船时 {grid.商船在港船时.min():.0f}–{grid.商船在港船时.max():.0f} 船·小时／天，"
          f"波动 {(grid.商船在港船时.max() / grid.商船在港船时.min() - 1) * 100:.0f}%")
    print(f"  已写出 figures/sensitivity.csv（{len(grid)} 行）\n")

    oaat = one_at_a_time(com.minutes.sum() / 60)
    oaat.to_csv(FIGS / "sensitivity_one_at_a_time.csv", index=False, encoding="utf-8-sig")
    print("一次只改一个参数（M3 要带的敏感性表，看结论对谁敏感）")
    print(oaat.to_string(index=False))
    print("  已写出 figures/sensitivity_one_at_a_time.csv\n")

    NARRATIVE.mkdir(exist_ok=True)
    md = f"""# 关键数字（由 analysis/03_congestion.py 生成）

> 改参数后重跑本脚本即可同步；正文引用数字时以此表为准。

## 数据与基线

| 项目 | 数值 |
|---|---|
| 原始记录 | 84,702 行（有效 84,699 行） |
| 船舶 | 100 艘（97 个船名） |
| 记录间隔中位数 | 10 秒；超过 10 分钟的缺口 797 处 |
| 停留（默认参数） | {len(stops)} 次，{stops.mmsi.nunique()} 艘船，{stops.minutes.sum() / 60:.1f} 小时 |
| 时长中位数 / 平均数 / P90 | {stops.minutes.median():.1f} / {stops.minutes.mean():.1f} / {stops.minutes.quantile(0.9):.1f} 分钟 |
| 商船停留 | {len(com)} 次，中位数 {com.minutes.median():.1f}，平均数 {com.minutes.mean():.1f} 分钟 |

## 三种量法（默认参数）

| 量法 | 全部船型 | 仅油轮与货船 |
|---|---|---|
| 存量：平均在停船数 | {mean_l:.2f} 艘 | {com_mean_l:.2f} 艘 |
| 存量：最大同时在停 | {max_l} 艘 | {com_max_l} 艘 |
| 流量：每小时开始停留 | {lam:.2f} 次 | {len(com) / 24:.2f} 次 |
| 时长：平均 | {w:.2f} 小时 | {com.minutes.mean() / 60:.2f} 小时 |
| 时长：中位数 | {stops.minutes.median() / 60:.2f} 小时 | {com.minutes.median() / 60:.2f} 小时 |
| 利特尔法则 λW | {lam * w:.2f}（存量 {mean_l:.2f}） | {len(com) / 24 * com.minutes.mean() / 60:.2f}（存量 {com_mean_l:.2f}） |

## 参数敏感性

### 九组组合（v0 × tau）

{md_table(grid)}

### 一次只改一个参数

{md_table(oaat)}

- 全部停留次数：{int(fixed.iloc[0].全部停留次数)}（tau=10）→ {int(fixed.iloc[-1].全部停留次数)}（tau=60）
- 商船在港船时：{grid.商船在港船时.min():.0f}–{grid.商船在港船时.max():.0f} 船·小时／天，
  波动 {(grid.商船在港船时.max() / grid.商船在港船时.min() - 1) * 100:.0f}%
"""
    (NARRATIVE / "key_numbers.md").write_text(md, encoding="utf-8")
    print("  已写出 narrative/key_numbers.md")

    if len(sys.argv) > 1:
        compare_reference(stops, Path(sys.argv[1]))
    else:
        print("\n拿到教师给定的 3 次停留后，用下面的命令做对照：")
        print("  python analysis/03_congestion.py data/raw/reference_stops.csv")


if __name__ == "__main__":
    main()
