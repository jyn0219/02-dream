"""导出本机会话记录为附录（不含内部推理），用于 AI 使用披露的“对话记录”。

工具没有公开分享链接，所以把用户提问与助手可见回复导出成 PDF，附在终稿后面。
仅在本机可用：路径写死为当前会话的日志文件。

用法：python tools/export_dialog.py
产出：narrative/ai_dialog.md、build/ai_dialog.pdf、submissions/ai_dialog.pdf
"""

import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from compression import zstd  # Python 3.14+

ROOT = Path(__file__).resolve().parent.parent
LOG = Path(
    r"C:\Users\79201\.dsh\sessions\--C-Users-79201-Documents-deepseek-harness-default-workspace--"
    r"\session-04e83132-05f1-4b26-9af2-c905891e4133\session.v4.jsonl.zstd"
)
OUT_MD = ROOT / "narrative" / "ai_dialog.md"

# 本脚本用 Python 3.14 解 zstd；排版要走装了 python-docx 的解释器
BUILD_PY = Path(
    r"C:\Users\79201\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
)

USER_LIMIT = 900
ASSIST_LIMIT = 700


def ts(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000).strftime("%m-%d %H:%M")


def text_of(message: dict) -> str:
    parts = []
    for item in message.get("content", []):
        if item.get("type") == "text":
            parts.append(item.get("text", ""))
    return "\n".join(parts).strip()


def main() -> None:
    raw = zstd.decompress(LOG.read_bytes()).decode("utf-8")
    events = [json.loads(line) for line in raw.splitlines() if line.strip()]

    exchanges = []
    current = None
    for event in events:
        kind = event.get("type")
        data = event.get("data", {})
        if kind == "user/message":
            if data.get("source", {}).get("kind") != "user":
                continue
            body = text_of(data).strip()
            if not body:
                continue
            current = {"time": event["time"], "user": body, "assistant": []}
            exchanges.append(current)
        elif kind == "assistant/message" and current is not None:
            body = text_of(data.get("message", {})).strip()
            if body:
                current["assistant"].append(body)

    lines = [
        "# 对话记录（导出）",
        "",
        "工具：DeepSeek Harness（本机 Web 界面，会话无公开分享链接）",
        f"会话 ID：`{LOG.parent.name}`",
        f"导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"消息数：{len(exchanges)} 轮",
        "",
        "> 本文件只保留用户输入与助手对用户可见的回复，不含内部推理、工具调用参数与文件内容；"
        "完整日志保存在本机会话目录，可在 DSH 界面中打开。",
        "",
    ]

    for i, ex in enumerate(exchanges, 1):
        user = ex["user"].replace("\n", " ")
        if len(user) > USER_LIMIT:
            user = user[:USER_LIMIT] + "……"
        reply = "\n".join(ex["assistant"]).strip()
        if len(reply) > ASSIST_LIMIT:
            reply = reply[:ASSIST_LIMIT] + "……"
        lines += [f"## 第 {i} 轮 · {ts(ex['time'])}", "", f"**用户**：{user}", "", f"**助手**：{reply or '（无文字回复）'}", ""]

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"已写出 {OUT_MD.relative_to(ROOT)}（{len(exchanges)} 轮）")

    subprocess.run(
        [str(BUILD_PY if BUILD_PY.exists() else sys.executable),
         str(ROOT / "tools" / "build_report.py"), str(OUT_MD),
         "--out", str(ROOT / "build" / "ai_dialog.docx")],
        check=True,
    )
    shutil.copyfile(ROOT / "build" / "ai_dialog.pdf", ROOT / "submissions" / "ai_dialog.pdf")
    print("已写出 submissions/ai_dialog.pdf")


if __name__ == "__main__":
    main()
