"""把 narrative/*.md 排版成 Word（.docx），再用 LibreOffice Kit 导出 PDF。

用法（在项目根目录）：
    python tools/build_report.py narrative/report.md
    python tools/build_report.py narrative/report.md --no-pdf

依赖：python-docx（`pip install python-docx`）；PDF 用本机的 LibreOffice Kit 命令行。

支持的 Markdown 子集：标题 #–####、段落、**粗体**、`代码`、[链接](url)、
无序/有序列表、表格、图片（下一行以「图」开头则当作图注）、引用块、代码围栏。
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

# LibreOffice Kit（本机 DSH 自带）；换机器时改这两行，或设环境变量 LO_NODE / LO_CLI
NODE = os.environ.get("LO_NODE", r"C:\Users\79201\AppData\Local\Programs\DeepSeek Harness\resources\runtime\primary-runtime\dependencies\node\bin\node.exe")
CLI = os.environ.get("LO_CLI", r"C:\Users\79201\AppData\Local\Programs\DeepSeek Harness\resources\app.asar.unpacked\dsh\node_modules\@deepseek-ai\libreoffice-kit\lib\cli.js")

BODY_EAST, BODY_ASCII = "宋体", "Times New Roman"
HEAD_EAST, HEAD_ASCII = "黑体", "Arial"


def set_font(run, east=BODY_EAST, ascii_=BODY_ASCII, size=None, bold=None):
    """中文字体必须写 w:eastAsia，只设 font.name 不管用。"""
    run.font.name = ascii_
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), ascii_)
    rfonts.set(qn("w:hAnsi"), ascii_)
    rfonts.set(qn("w:eastAsia"), east)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold


def body_para(doc, text="", indent=True, align=None, space_after=6):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing = 1.5
    pf.space_after = Pt(space_after)
    if indent:
        pf.first_line_indent = Pt(24)          # 首行缩进两字（12pt × 2）
    if align is not None:
        p.alignment = align
    add_inline(p, text)
    return p


INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")


def add_inline(p, text, size=12):
    """把 **粗体**、`代码`、[文字](链接) 拆成 run，逐段设置格式。"""
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            r = p.add_run(part[2:-2])
            set_font(r, size=size, bold=True)
        elif part.startswith("`") and part.endswith("`"):
            r = p.add_run(part[1:-1])
            r.font.name = "Consolas"
            r.font.size = Pt(size - 1.5)
            r.font.color.rgb = RGBColor(0x99, 0x33, 0x00)
        elif part.startswith("[") and "](" in part:
            label, url = part[1:-1].split("](", 1)
            r = p.add_run(f"{label}（{url}）" if url.startswith("http") else label)
            set_font(r, size=size)
        else:
            r = p.add_run(part)
            set_font(r, size=size)


def heading(doc, text, level):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(18 if level == 1 else 12)
    pf.space_after = Pt(8 if level == 1 else 6)
    pf.keep_with_next = True
    if level == 1:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        size = 18
    elif level == 2:
        size = 14
    else:
        size = 12
    r = p.add_run(text)
    set_font(r, east=HEAD_EAST, ascii_=HEAD_ASCII, size=size, bold=True)
    return p


def caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf = p.paragraph_format
    pf.space_before = Pt(3)
    pf.space_after = Pt(10)
    r = p.add_run(text)
    set_font(r, size=9)
    r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)


def add_table(doc, rows):
    header, body = rows[0], rows[1:]
    table = doc.add_table(rows=1, cols=len(header))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    # 表头跨页重复
    tr_pr = table.rows[0]._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)
    for i, cell in enumerate(table.rows[0].cells):
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_inline(p, header[i], size=9.5)
        for r in p.runs:
            r.font.bold = True
    for row in body:
        cells = table.add_row().cells
        for i, val in enumerate(row[: len(header)]):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(2)
            add_inline(p, val, size=9.5)
    # 行不跨页断开
    for row in table.rows:
        tr_pr = row._tr.get_or_add_trPr()
        cant = OxmlElement("w:cantSplit")
        tr_pr.append(cant)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_page_number(doc):
    footer = doc.sections[0].footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run("第 ")
    set_font(run, size=9)
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    r = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.text = "1"
    r.append(t)
    fld.append(r)
    footer._p.append(fld)
    run2 = footer.add_run(" 页")
    set_font(run2, size=9)


def split_table_row(line):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells


def is_separator(cells):
    return all(re.fullmatch(r":?-{2,}:?", c.strip()) for c in cells if c.strip() != "")


def build(md_path: Path, out_path: Path) -> Path:
    lines = md_path.read_text(encoding="utf-8").splitlines()
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.top_margin = sec.bottom_margin = Cm(2.54)
    sec.left_margin = sec.right_margin = Cm(2.8)
    add_page_number(doc)

    i, n = 0, len(lines)
    first_heading = True
    while i < n:
        line = lines[i]
        s = line.strip()

        if not s:
            i += 1
            continue

        if s.startswith("```"):                       # 代码围栏
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                p = doc.add_paragraph()
                p.paragraph_format.line_spacing = 1.0
                p.paragraph_format.space_after = Pt(0)
                r = p.add_run(lines[i].rstrip())
                r.font.name = "Consolas"
                r.font.size = Pt(9)
                i += 1
            i += 1
            continue

        if s.startswith("#"):                         # 标题
            level = len(s) - len(s.lstrip("#"))
            heading(doc, s[level:].strip(), min(level, 3))
            first_heading = False
            i += 1
            continue

        if s.startswith("|"):                         # 表格
            block = []
            while i < n and lines[i].strip().startswith("|"):
                block.append(lines[i].strip())
                i += 1
            rows = [split_table_row(b) for b in block]
            rows = [r for k, r in enumerate(rows) if not (k == 1 and is_separator(r))]
            if rows:
                add_table(doc, rows)
            continue

        m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", s)  # 图片
        if m:
            alt, src = m.group(1), m.group(2)
            img = (md_path.parent / src).resolve()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next = True
            if img.exists():
                p.add_run().add_picture(str(img))
            else:
                p.add_run(f"[缺图：{src}]")
            i += 1
            j = i
            while j < n and not lines[j].strip():      # 跳过空行，看下一段是不是图注
                j += 1
            if j < n and lines[j].strip().startswith("图"):
                caption(doc, lines[j].strip())
                i = j + 1
            continue

        if s.startswith(">"):                         # 引用块：连续多行合成一段
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            body_para(doc, "".join(buf), indent=False, space_after=10)
            for r in doc.paragraphs[-1].runs:
                r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
                r.font.size = Pt(10.5)
            continue

        if re.match(r"^[-*]\s+", s):                  # 无序列表
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.line_spacing = 1.4
            add_inline(p, re.sub(r"^[-*]\s+", "", s), size=11.5)
            i += 1
            continue

        if re.match(r"^\d+\.\s+", s):                 # 有序列表
            p = doc.add_paragraph(style="List Number")
            p.paragraph_format.line_spacing = 1.4
            add_inline(p, re.sub(r"^\d+\.\s+", "", s), size=11.5)
            i += 1
            continue

        if re.fullmatch(r"-{3,}", s):
            i += 1
            continue

        # 普通段落：合并连续的非空行
        buf = [s]
        i += 1
        while i < n and lines[i].strip() and not re.match(r"^(#|\||>|```|!\[|[-*]\s|\d+\.\s)", lines[i].strip()):
            buf.append(lines[i].strip())
            i += 1
        body_para(doc, "".join(buf))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out_path)
    return out_path


def to_pdf(docx_path: Path) -> Path:
    pdf = docx_path.with_suffix(".pdf")
    if not Path(NODE).exists() or not Path(CLI).exists():
        raise SystemExit("找不到 LibreOffice Kit；改脚本开头的 NODE / CLI，或先只生成 docx（--no-pdf）")
    if pdf.exists():                     # CLI 不覆盖已有文件
        pdf.unlink()
    res = subprocess.run([NODE, CLI, "convert", "--input", str(docx_path), "--output", str(pdf)],
                         capture_output=True, text=True)
    if res.returncode != 0 or not pdf.exists():
        print(res.stdout, res.stderr)
        raise SystemExit(f"PDF 导出失败：{pdf}")
    return pdf


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("md", nargs="?", default="narrative/report.md")
    ap.add_argument("--out", default=None, help="输出 docx 路径，默认 build/<名字>.docx")
    ap.add_argument("--no-pdf", action="store_true")
    args = ap.parse_args()

    md = Path(args.md)
    out = Path(args.out) if args.out else Path("build") / (md.stem + ".docx")
    docx = build(md, out)
    print(f"已生成 {docx}")
    if not args.no_pdf:
        pdf = to_pdf(docx)
        print(f"已生成 {pdf}（{pdf.stat().st_size // 1024} KB）")


if __name__ == "__main__":
    main()
