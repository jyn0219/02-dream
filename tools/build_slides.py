"""生成 M6 的 5 页路演 PPTX（另加 1 页附页）。

用法（在项目根目录）：
    python tools/build_slides.py

读 figures/sensitivity.csv 和 figures/main.png、fig1、fig2，
写出 build/m6_slides.pptx。文字里的〔 〕由本人补写。
"""

import csv
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml import parse_xml
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
OUT = ROOT / "build" / "m6_slides.pptx"

CN = "微软雅黑"
INK = RGBColor(0x22, 0x22, 0x22)
BLUE = RGBColor(0x1F, 0x4E, 0x79)
ORANGE = RGBColor(0xD5, 0x5E, 0x00)
GREY = RGBColor(0x77, 0x77, 0x77)
LIGHT = RGBColor(0xEE, 0xF3, 0xF8)

W, H = 13.333, 7.5


def set_run(run, size, bold=False, color=INK, italic=False):
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.italic = italic
    f.color.rgb = color
    f.name = CN
    # 中文字体要另外写 a:ea，否则 PowerPoint 会用默认宋体
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        el = rpr.find("{http://schemas.openxmlformats.org/drawingml/2006/main}" + tag.split(":")[1])
        if el is None:
            el = parse_xml(
                f'<a:{tag.split(":")[1]} xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
                f' typeface="{CN}"/>')
            rpr.append(el)


def textbox(slide, x, y, w, h, lines, align=PP_ALIGN.LEFT, spacing=1.15):
    """lines: [(text, size, bold, color, space_after_pt), ...]"""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    for i, (text, size, bold, color, gap) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        p.space_after = Pt(gap)
        r = p.add_run()
        r.text = text
        set_run(r, size, bold, color)
    return box


def slide_base(prs, kicker, title, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    # 顶部细条
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(W), Inches(0.12))
    bar.fill.solid()
    bar.fill.fore_color.rgb = BLUE
    bar.line.fill.background()
    textbox(s, 0.6, 0.35, 12, 0.35, [(kicker, 12, False, ORANGE, 2)])
    textbox(s, 0.6, 0.72, 12, 0.85, [(title, 30, True, BLUE, 0)])
    textbox(s, 11.6, 7.02, 1.2, 0.3, [(f"{page}/6", 10, False, GREY, 0)], align=PP_ALIGN.RIGHT)
    return s


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def build():
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)

    # 1 问题
    s = slide_base(prs, "02 组 · dream · B1 任务包", "哥德堡港的船舶停留与港口拥堵", 1)
    textbox(s, 0.6, 1.9, 12, 0.5, [("研究问题", 16, True, GREY, 6)])
    textbox(s, 0.6, 2.35, 12, 1.2, [
        ("〔一句话：2017 年 7 月 5 日，哥德堡港区内油轮与货船的停留时长分布如何？"
         "以商船在港船时作为拥堵的代理指标，它在什么参数范围内稳定、何时失效？〕", 22, False, INK, 8)])
    textbox(s, 0.6, 3.9, 5.6, 2.2, [
        ("分析层次", 14, True, GREY, 4),
        ("〔描述 + 方法评估，不是因果〕", 18, False, INK, 14),
        ("答案改变谁的决定", 14, True, GREY, 4),
        ("〔写 2 句：港口调度看「在港多久」，货主看「等了多久」，本数据只回答前者〕", 18, False, INK, 0)])
    s.shapes.add_picture(str(FIG / "main.png"), Inches(7.1), Inches(3.6), height=Inches(3.1))
    notes(s, "30 秒。第一句说问题，第二句说它属于哪一层，第三句说谁会因此改变什么。不要念背景。")

    # 2 数据与方法
    s = slide_base(prs, "数据与方法", "一天、一百艘船、三个参数", 2)
    blocks = [
        ("数据", ["DMA AIS〔官〕，2017-07-05 全天", "84,702 行 × 8 列，100 艘船",
                  "间隔中位数 10 秒；797 处缺口"]),
        ("停留", ["航速 < 0.5 节，持续 ≥ 30 分钟", "记录断开 > 10 分钟即结束",
                  "→ 215 次，56 艘，512.5 小时"]),
        ("指标", ["只保留油轮与货船：46 次", "平均在停 8.2 艘",
                  "中位数 120 分钟；利特尔法则验证"]),
    ]
    for i, (head, items) in enumerate(blocks):
        x = 0.6 + i * 4.15
        card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.95), Inches(3.9), Inches(3.3))
        card.fill.solid()
        card.fill.fore_color.rgb = LIGHT
        card.line.fill.background()
        lines = [(head, 18, True, BLUE, 10)] + [(t, 14, False, INK, 10) for t in items]
        textbox(s, x + 0.28, 2.18, 3.4, 2.9, lines)
    textbox(s, 0.6, 5.55, 12, 0.9, [
        ("口径：只统计港区内的停留，没有锚地与码头边界；「在港时长」不等于「等泊时长」",
         15, False, GREY, 0)])
    notes(s, "60 秒。三个参数各说一句，重点说缺口规则——没有它，停留时长会多算七成。")

    # 3 核心结论
    s = slide_base(prs, "核心结论", "〔结论式标题：谁、在什么口径下、得到什么数〕", 3)
    textbox(s, 0.6, 1.85, 6.0, 1.3, [
        ("〔一句话结论：在什么口径下、对哪类船、得到什么数〕", 22, False, INK, 0)])
    stats = [("197.2", "船·小时/天\n商船在港船时"), ("8.2", "艘\n平均在停商船"), ("120", "分钟\n停留时长中位数")]
    for i, (num, label) in enumerate(stats):
        x = 0.6 + i * 2.0
        textbox(s, x, 3.3, 1.9, 0.8, [(num, 40, True, ORANGE, 0)])
        textbox(s, x, 4.1, 1.9, 0.9, [(label, 12, False, GREY, 0)])
    s.shapes.add_picture(str(FIG / "main.png"), Inches(6.7), Inches(1.9), width=Inches(6.1))
    textbox(s, 0.6, 5.6, 5.9, 1.0, [
        ("〔一句解释：为什么这条曲线能代表拥堵；峰值时段与商船/全部船型的差距说明什么〕",
         14, False, GREY, 0)])
    notes(s, "90 秒。先指数字，再指图，最后说一句边界。数字只念三个，不要念表。")

    # 4 敏感性
    s = slide_base(prs, "参数敏感性", "换一个参数，结论会不会翻盘？", 4)
    rows = list(csv.reader((FIG / "sensitivity.csv").open(encoding="utf-8-sig")))
    head, body = rows[0], rows[1:]
    tbl_shape = s.shapes.add_table(len(body) + 1, len(head), Inches(0.6), Inches(1.95),
                                   Inches(7.4), Inches(4.2))
    table = tbl_shape.table
    widths = [0.9, 1.0, 1.5, 1.4, 1.3, 1.3]
    for i, wd in enumerate(widths):
        table.columns[i].width = Inches(wd)
    for j, h in enumerate(head):
        cell = table.cell(0, j)
        cell.text = ""
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = h
        set_run(r, 10, True, RGBColor(0xFF, 0xFF, 0xFF))
        cell.fill.solid()
        cell.fill.fore_color.rgb = BLUE
    for i, row in enumerate(body, start=1):
        for j, val in enumerate(row):
            cell = table.cell(i, j)
            cell.text = ""
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = val
            set_run(r, 10, False, INK)
    textbox(s, 8.3, 2.0, 4.5, 4.0, [
        ("看懂这张表", 14, True, GREY, 6),
        ("次数 386 → 133：是港口变了，还是 tau 在删短停留？", 14, False, INK, 8),
        ("在港船时 185–203，波动约 10%：这算稳吗？", 14, False, INK, 14),
        ("〔你的判断：头条指标选哪个，为什么〕", 14, False, GREY, 0)])
    notes(s, "60 秒。只讲一件事：为什么用总量而不是次数。这是 5 分档的考点。")

    # 5 最不确定
    s = slide_base(prs, "最不确定的结论", "证据链最薄的一环", 5)
    boxes = [
        ("薄在哪里", "〔没有锚地与码头边界：\n「在港时长」只是等泊时长的代理，\n不是等泊时长本身〕"),
        ("什么会推翻它", "〔带泊位/锚地边界的 AIS，\n或港口公布的靠离泊记录；\n若等待集中在锚地，结论要改〕"),
    ]
    for i, (head, body) in enumerate(boxes):
        x = 0.6 + i * 6.2
        card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(2.0), Inches(5.9), Inches(3.4))
        card.fill.solid()
        card.fill.fore_color.rgb = LIGHT
        card.line.fill.background()
        textbox(s, x + 0.35, 2.25, 5.2, 0.5, [(head, 16, True, ORANGE, 12)])
        textbox(s, x + 0.35, 2.9, 5.2, 2.3, [(body, 16, False, INK, 0)])
    notes(s, "60 秒。诚实说局限，给出可验证的推翻条件。不要用「数据有限」这种空话。")

    # 附页
    s = slide_base(prs, "附页（被问到再翻）", "两张备查图", 6)
    s.shapes.add_picture(str(FIG / "fig1_duration.png"), Inches(0.6), Inches(2.0), height=Inches(3.6))
    s.shapes.add_picture(str(FIG / "fig2_ship_profile.png"), Inches(5.3), Inches(2.0), height=Inches(3.6))
    textbox(s, 10.1, 2.1, 2.7, 3.5, [
        ("停留时长分布", 12, True, BLUE, 6),
        ("〔一句话：长尾，用中位数〕", 12, False, GREY, 16),
        ("每艘商船", 12, True, BLUE, 6),
        ("〔一句话：谁贡献了船时〕", 12, False, GREY, 0)])

    OUT.parent.mkdir(exist_ok=True)
    prs.save(OUT)
    print(f"已生成 {OUT.relative_to(ROOT)}（{len(prs.slides._sldIdLst)} 页）")


if __name__ == "__main__":
    build()
