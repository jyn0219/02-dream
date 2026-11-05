"""B1 港口停留与拥堵：三张探索图（对应 M2 的「三张探索图」）

读取 data/clean/stops.csv（由 analysis/01_clean.py 生成），
在 figures/ 中画出三张图，并在屏幕上打印每张图的**图注草稿**（第 8 讲表 8-3 的四个要素）：

  fig1_duration.png     分布图：油轮与货船的停留时长分布
  fig2_ship_profile.png 关系图：每艘商船的停留次数与中位时长
  fig3_occupancy.png    时间图：全天每分钟在停的船数（全部船型 vs 商船）

用法：python analysis/02_explore.py
"""

import os
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                      # 项目根目录（analysis/ 的上一级）
STOPS = ROOT / "data" / "clean" / "stops.csv"
FIGS = ROOT / "figures"
FIGS.mkdir(exist_ok=True)

# matplotlib 的缓存默认写到用户目录，某些环境没有权限，改到项目内
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplcache"))

import matplotlib                      # noqa: E402
import matplotlib.pyplot as plt        # noqa: E402

# 论文图：按最终印刷尺寸画（单栏 90 毫米），字号 7 磅；中文用系统里已有的字体
plt.rcParams.update({
    "font.sans-serif": ["Microsoft YaHei", "SimHei", "PingFang SC", "Noto Sans CJK SC", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.figsize": (90 / 25.4, 62 / 25.4),
    "font.size": 7,
    "axes.titlesize": 7,
    "axes.labelsize": 7,
    "xtick.labelsize": 6.5,
    "ytick.labelsize": 6.5,
    "legend.fontsize": 6.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})
BLUE, VERMILION, GREY = "#0072B2", "#D55E00", "#8C8C8C"   # 色觉友好的配色（第 8 讲第 4.3 节）

COMMERCIAL = ["Tanker", "Cargo"]


def load_stops() -> pd.DataFrame:
    """读入停留表。

    注意：只有原始数据的 timestamp 是「日/月/年」，需要 dayfirst=True；
    stops.csv 里已经是 ISO 的「年-月-日」，再加 dayfirst 会被 pandas 读成 5 月 7 日
    （整个时间轴平移，次数和时长不变，但日期错了，切片全空）。
    """
    s = pd.read_csv(STOPS, parse_dates=["start", "end"])
    s["dtype"] = np.where(s.shiptype.isin(COMMERCIAL), "商船（油轮／货船）", "其他船型")
    return s


def fig1_duration(com: pd.DataFrame) -> str:
    """分布图：商船停留时长。长尾数据，横轴截到 12 小时，超出的在图上注明。"""
    dur = com.minutes
    med, p90 = dur.median(), np.percentile(dur, 90)

    fig, ax = plt.subplots()
    ax.hist(dur.clip(upper=720), bins=np.arange(0, 780, 60), color=BLUE, alpha=0.85, edgecolor="white")
    ax.axvline(med, color=VERMILION, lw=1.2, ls="-")
    ax.annotate(f"中位数 {med:.0f} 分钟", xy=(med, ax.get_ylim()[1] * 0.9),
                xytext=(med + 25, ax.get_ylim()[1] * 0.9), color=VERMILION, fontsize=6.5)
    ax.set_xlabel("停留时长（小时）")
    ax.set_ylabel("停留次数")
    ax.set_xticks(np.arange(0, 781, 120), [f"{h:.0f}" for h in np.arange(0, 781, 120) / 60])
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    ax.text(0.98, 0.95, f"n = {len(dur)} 次\nP90 = {p90:.0f} 分钟",
            transform=ax.transAxes, ha="right", va="top", fontsize=6.5, color="#333333")
    if (dur > 720).any():
        ax.text(0.98, 0.72, f"另有 {int((dur > 720).sum())} 次超过 12 小时，\n"
                            f"最长 {dur.max() / 60:.1f} 小时，未画出",
                transform=ax.transAxes, ha="right", va="top", fontsize=6, color=GREY)
    out = FIGS / "fig1_duration.png"
    fig.savefig(out)
    plt.close(fig)
    return ("图 1　哥德堡港油轮与货船的停留时长分布（2017 年 7 月 5 日）\n"
            "  数据来源：丹麦海事局 AIS〔官〕，经 movingpandas-examples 整理，课程样本包\n"
            "  关键参数：航速门槛 0.5 节、最短时长 30 分钟、缺口 10 分钟；只保留油轮与货船\n"
            f"  口径说明：n = {len(dur)} 次停留；柱高为次数，横轴截到 12 小时，中位数为 {med:.0f} 分钟")


def fig2_ship_profile(com: pd.DataFrame) -> str:
    """关系图：每艘商船的停留次数与该船停留时长的中位数，点的大小为在港船时。"""
    per = (com.groupby("mmsi")
           .agg(name=("name", "first"), n=("minutes", "size"),
                med=("minutes", "median"), hours=("minutes", "sum"))
           .assign(hours=lambda d: d.hours / 60 / 60))
    per = per[per.n >= 1]

    fig, ax = plt.subplots()
    ax.scatter(per.n, per.med, s=8 + per.hours * 6, color=BLUE, alpha=0.65, edgecolor="white", linewidth=0.4)
    ax.set_xlabel("该船一天的停留次数")
    ax.set_ylabel("该船停留时长的中位数（小时）")
    ax.set_yscale("log")
    ax.set_yticks([1, 2, 4, 8, 16, 32], ["1", "2", "4", "8", "16", "32"])
    ax.minorticks_off()
    ax.grid(axis="y", color="#E9ECEF", lw=0.5)
    ax.set_axisbelow(True)
    # 标出在港船时最多的三艘，便于读者对照；标签互相错开，避免压在一起
    top = per.nlargest(3, "hours")
    for i, (_, r) in enumerate(top.iterrows()):
        label = str(r["name"])[:14] if isinstance(r["name"], str) else str(int(r.mmsi))
        ax.annotate(label, xy=(r.n, r.med), xytext=(6, 6 if i % 2 == 0 else -10),
                    textcoords="offset points", fontsize=5.5, color="#333333")
    out = FIGS / "fig2_ship_profile.png"
    fig.savefig(out)
    plt.close(fig)
    return ("图 2　每艘商船的停留次数与停留时长中位数\n"
            "  数据来源：丹麦海事局 AIS〔官〕，课程样本包，2017 年 7 月 5 日\n"
            "  关键参数：航速门槛 0.5 节、最短时长 30 分钟、缺口 10 分钟；只保留油轮与货船\n"
            f"  口径说明：n = {len(per)} 艘船；点的大小为该船当天的在港船时，纵轴为对数刻度")


def fig3_occupancy(stops: pd.DataFrame) -> str:
    """时间图：全天在停船数（存量），全部船型与商船各一条，说明噪声有多大。"""
    day = pd.Timestamp("2017-07-05")
    idx = pd.date_range(day, day + pd.Timedelta(hours=23, minutes=55), freq="5min")

    def occupancy(sub: pd.DataFrame) -> pd.Series:
        occ = pd.Series(0, index=idx)
        for _, r in sub.iterrows():
            occ.loc[r.start.floor("5min"):r.end.floor("5min")] += 1
        return occ

    all_ships = occupancy(stops)
    com_only = occupancy(stops[stops.shiptype.isin(COMMERCIAL)])
    # 精确的平均在停船数按「停留总时长 ÷ 一天」算，和敏感性表里的口径一致；
    # 5 分钟分箱只用于画线，两端都算会略微偏高，不能拿来报告。
    day_min = 24 * 60
    mean_all = stops.minutes.sum() / day_min
    mean_com = stops[stops.shiptype.isin(COMMERCIAL)].minutes.sum() / day_min

    fig, ax = plt.subplots(figsize=(90 / 25.4, 55 / 25.4))
    ax.plot(all_ships.index, all_ships.values, color=GREY, lw=0.8, label="全部船型")
    ax.plot(com_only.index, com_only.values, color=BLUE, lw=1.2, label="油轮与货船")
    ax.set_xlabel("时刻（2017-07-05）")
    ax.set_ylabel("在停的船数（艘）")
    ax.set_ylim(0, None)
    ax.xaxis.set_major_locator(matplotlib.dates.HourLocator(byhour=range(0, 24, 3)))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M"))
    ax.legend(loc="upper right", frameon=False)
    ax.annotate(f"商船平均 {mean_com:.1f} 艘",
                xy=(0.01, 0.88), xycoords="axes fraction", fontsize=6.5, color=BLUE)
    ax.annotate(f"全部平均 {mean_all:.1f} 艘",
                xy=(0.01, 0.78), xycoords="axes fraction", fontsize=6.5, color=GREY)
    for h in range(0, 24, 6):
        ax.axvline(day + pd.Timedelta(hours=h), color="#E9ECEF", lw=0.5, zorder=0)
    out = FIGS / "fig3_occupancy.png"
    fig.savefig(out)
    plt.close(fig)
    return ("图 3　哥德堡港全天在停的船数（5 分钟粒度）\n"
            "  数据来源：丹麦海事局 AIS〔官〕，课程样本包，2017 年 7 月 5 日\n"
            "  关键参数：停留按 0.5 节／30 分钟／10 分钟缺口识别；含全部 100 艘船与仅油轮货船两种口径\n"
            f"  口径说明：任一时刻处于停留中的船数，单位艘；按停留总时长计，商船平均 {mean_com:.1f} 艘，"
            f"全部船型平均 {mean_all:.1f} 艘；曲线为 5 分钟分箱，端点同时计入，略高于平均值")


def main() -> None:
    stops = load_stops()
    com = stops[stops.shiptype.isin(COMMERCIAL)]
    print(f"读入 {len(stops)} 次停留，其中商船 {len(com)} 次；"
          f"船型：{', '.join(f'{k}{v}' for k, v in stops.shiptype.value_counts().items())}")

    captions = [fig1_duration(com), fig2_ship_profile(com), fig3_occupancy(stops)]
    # M3 要求把「将成为终稿核心的那张图」另存为 main.png，且必须由本脚本生成。
    # 这里选图 3（在停船数曲线）；换主图时改下面这一行，再把新的图注贴到报告里。
    shutil.copyfile(FIGS / "fig3_occupancy.png", FIGS / "main.png")
    print("\n已生成：")
    for p in sorted(FIGS.glob("*.png")):
        print(f"  {p.relative_to(ROOT)}")
    print("\n图注草稿（四个要素，按第 8 讲表 8-3）：\n")
    for c in captions:
        print(c + "\n")


if __name__ == "__main__":
    main()
