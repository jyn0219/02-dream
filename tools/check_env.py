"""检查当前解释器是否装齐了项目依赖。

用法（在项目根目录）：
    python tools/check_env.py
退出码 0 表示核心三件套齐全，1 表示缺包。
"""

import importlib
import sys

CORE = ("pandas", "numpy", "matplotlib")
TOOLS = ("docx", "pptx")          # python-docx、python-pptx，只在导出 PDF / 重做 PPT 时用

print(f"Python {sys.version.split()[0]}  ({sys.executable})")

missing_core = []
for name in CORE + TOOLS:
    try:
        mod = importlib.import_module(name)
        version = getattr(mod, "__version__", "")
        print(f"  {name:12s} OK   {version}")
    except Exception:
        print(f"  {name:12s} 缺失")
        if name in CORE:
            missing_core.append(name)

if missing_core:
    print("\n缺核心包：", ", ".join(missing_core))
    print("装法：python -m pip install -r requirements.txt")
    sys.exit(1)

print("\n核心依赖齐全，可以运行 analysis/01_clean.py")
