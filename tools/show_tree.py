"""打印复现包的目录树（跳过 .git / .idea / build / 缓存），供 M1 截图用。

用法（项目根目录）：
    python tools/show_tree.py

同时写出 submissions/m1_directory.txt，可以用记事本打开再截图。
"""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "submissions" / "m1_directory.txt"
SKIP = {".git", ".idea", ".venv", "__pycache__", ".mplcache", "build", "node_modules"}


def walk(directory: Path, prefix: str = "") -> list[str]:
    entries = sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    entries = [e for e in entries if e.name not in SKIP]
    lines = []
    for i, entry in enumerate(entries):
        last = i == len(entries) - 1
        branch = "`-- " if last else "|-- "
        if entry.is_dir():
            lines.append(f"{prefix}{branch}{entry.name}/")
            lines.extend(walk(entry, prefix + ("    " if last else "|   ")))
        else:
            size = entry.stat().st_size
            lines.append(f"{prefix}{branch}{entry.name}  ({size:,} B)")
    return lines


def main() -> None:
    lines = [f"{ROOT.name}/"] + walk(ROOT)
    text = "\n".join(lines)
    print(text)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(text + "\n", encoding="utf-8")
    print(f"\n共 {len(lines) - 1} 项；已写出 {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
