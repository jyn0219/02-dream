"""B1 港口停留与拥堵：01/02/03 共用的函数与参数。

只放两件事：读原始 AIS、识别停留。三个脚本都从这里 import，
同一段代码不复制三份（表 C-20「代码质量」一项看的就是这个）。
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent          # 项目根目录（analysis/ 的上一级）
RAW = ROOT / "data" / "raw" / "ais_gothenburg_20170705.csv"
CLEAN = ROOT / "data" / "clean"
FIGS = ROOT / "figures"
NARRATIVE = ROOT / "narrative"

# 三个参数集中写在开头（第 15 讲第 3 节：参数即立场，改了要在报告里写明理由）
V0 = 0.5     # 航速门槛，节：低于它算「停着」
TAU = 30     # 最短时长，分钟：停不满这么久不算一次停留
GAP = 10     # 缺口规则，分钟：相邻记录间隔超过它就切断，缺口里的时间不算停留

COMMERCIAL = ("Tanker", "Cargo")   # 研究港口拥堵只看油轮与货船，其余是噪声


def load_ais(path: Path = RAW) -> pd.DataFrame:
    """读原始 AIS：去空值、按「日/月/年」解析时间、按船和时间排序、算相邻记录的间隔。"""
    df = pd.read_csv(path, parse_dates=["timestamp"], dayfirst=True)   # 日/月/年，不能省
    df = df.dropna(subset=["mmsi", "timestamp", "lat", "lon", "sog"]).copy()
    df = df.sort_values(["mmsi", "timestamp"]).reset_index(drop=True)
    df["dt"] = df.groupby("mmsi")["timestamp"].diff().dt.total_seconds()
    return df


def ship_type(df: pd.DataFrame) -> pd.Series:
    """每艘船只留一个船型：取该船出现次数最多的那一类（原始数据里同船会有 Undefined）。"""
    return df.groupby("mmsi")["shiptype"].agg(lambda s: s.mode().iat[0])


def find_stops(df: pd.DataFrame, v0: float = V0, tau: float = TAU,
               gap: float = GAP) -> pd.DataFrame:
    """识别停留，返回每次停留一行：mmsi、name、start、end、lat、lon、minutes、shiptype、hours。

    规则：连续的「航速 < v0」记录合成一段；遇到提速、换船，或相邻记录间隔 > gap 分钟，
    就结束当前这一段；段长 ≥ tau 分钟的才算一次停留。缺口里的时间不计入停留。
    """
    slow = df["sog"] < v0
    new_segment = (
        slow
        & (~slow.shift(1, fill_value=False)          # 上一条不是低速 → 新的一段
           | (df["dt"] > gap * 60)                   # 缺口 → 停留在此结束
           | (df["mmsi"] != df["mmsi"].shift(1)))    # 换船
    )
    stops = df[slow].groupby(new_segment.cumsum()).agg(
        mmsi=("mmsi", "first"),
        name=("name", "first"),
        start=("timestamp", "min"),
        end=("timestamp", "max"),
        lat=("lat", "mean"),
        lon=("lon", "mean"),
    )
    stops["minutes"] = (stops["end"] - stops["start"]).dt.total_seconds() / 60
    stops = stops[stops["minutes"] >= tau].reset_index(drop=True)
    stops["shiptype"] = stops["mmsi"].map(ship_type(df))
    stops["hours"] = stops["minutes"] / 60
    return stops
