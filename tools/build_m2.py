"""从 narrative/report.md 抽取 M2 检查点报告，导出 submissions/m2_eda.pdf。

M2 的要求（手册表 C-6）：对 M1 意见的回应、数据获取说明、清洗日志、三张探索图、
「这份数据不能回答什么」，文末附组内互评 1；回应要放在报告开头。

用法（项目根目录）：
    python tools/build_m2.py
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "narrative" / "report.md"
OUT_MD = ROOT / "narrative" / "m2_eda.md"


def split_sections(text: str) -> dict[str, str]:
    """按二级标题切分，返回 {标题: 正文}。"""
    parts = re.split(r"(?m)^## ", text)
    sections = {}
    for part in parts[1:]:
        lines = part.splitlines()
        sections[lines[0].strip()] = "\n".join(lines[1:]).strip()
    return sections


def main() -> None:
    text = SRC.read_text(encoding="utf-8")
    sec = split_sections(text)

    def body(prefix: str) -> str:
        for key, val in sec.items():
            if key.startswith(prefix):
                return val
        raise SystemExit(f"找不到小节：{prefix}")

    title = text.splitlines()[0].lstrip("# ").strip()
    members = "组员：王国梁、景亚宁"

    parts = [
        "# 02 dream · B1 港口停留与拥堵：M2 检查点报告",
        members,
        "> 第 12 讲 M2 提交件。以下内容取自终稿 `narrative/report.md`，"
        "按手册表 C-6 的要求组织：对 M1 意见的回应置于开头，文末附组内互评 1 记录。",
        "## 对 M1 意见的回应",
        body("附录A"),
        "## 1 问题",
        body("1 问题"),
        "## 2 数据",
        body("2 数据"),
        "## 3 方法",
        body("3 方法"),
        "## 4 结果",
        body("4 结果"),
        "## 5 局限：这份数据不能回答什么",
        body("5 局限"),
        "## 附录 B　组内互评 1 记录",
        body("附录B"),
    ]
    OUT_MD.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    print(f"已写出 {OUT_MD.relative_to(ROOT)}")

    subprocess.run([sys.executable, str(ROOT / "tools" / "build_report.py"),
                    str(OUT_MD), "--out", str(ROOT / "build" / "m2_eda.docx")], check=True)
    src_pdf = ROOT / "build" / "m2_eda.pdf"
    dst_pdf = ROOT / "submissions" / "m2_eda.pdf"
    shutil.copyfile(src_pdf, dst_pdf)
    print(f"已写出 {dst_pdf.relative_to(ROOT)}（{dst_pdf.stat().st_size // 1024} KB）")


if __name__ == "__main__":
    main()
