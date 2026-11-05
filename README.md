# 02 dream · B1 港口停留与拥堵：复现包

《航运与物流大数据分析》模块 C 结课项目，第 02 组（dream），B 轨任务包 B1。
用哥德堡港 2017 年 7 月 5 日一天的 AIS 船位，识别油轮与货船的停留，估计停留时长的分布，
给出一个拥堵指标，并说清它的口径与局限。

数据：丹麦海事局（DMA）AIS 开放数据〔官〕，经 movingpandas-examples 整理为课程样本包；
84,702 行、100 艘船、8 个字段。免费使用，须署名。

**提交方式**：代码与文档在 GitHub —— <https://github.com/jyn0219/02-dream>（Public，未登录可浏览）。
每完成一个里程碑 push 一次，提交表单里填这个地址；助教按下面的三条命令即可从头运行。
网盘可作为备份，但不是必需。`data/raw/` 里已带原始数据，不需要另外下载。

## 怎样运行

```bash
conda activate shipping
python analysis/01_clean.py       # 清洗 + 识别停留 → data/clean/stops.csv，并打印清洗日志
python analysis/02_explore.py     # 三张探索图 + 主图 → figures/
python analysis/03_congestion.py  # 三种量法 + 敏感性 → figures/sensitivity.csv、narrative/key_numbers.md

# 拿到教师给定的 3 次停留后（M1 的 4 分档），加一个参数做对照：
python analysis/03_congestion.py data/raw/reference_stops.csv
```

按 01 → 02 → 03 的顺序跑，不要跳。全程相对路径，换一台电脑也能跑。

**关于 `.venv/`**：项目里有一个 PyCharm 建的虚拟环境（`.venv/`，Python 3.14、pandas 3.1.1、
matplotlib 3.11.2），日常用它跑也可以，三个脚本的结果与 `shipping` 环境**逐字节一致**（已验证）。
但课程要求的复现环境是 Python 3.12 的 `shipping`，交之前用 `conda activate shipping` 再跑一遍。
`.venv/` 和 `.idea/` 不要上传、不进压缩包。

**预期结果**（默认参数 v0=0.5 节、tau=30 分钟、gap=10 分钟）：

- 01：停留 215 次、56 艘船、合计 512.5 小时，时长中位数 75.8 分钟；
- 02：`figures/` 下四张 PNG（fig1 分布、fig2 关系、fig3 时间、main 主图）；
- 03：存量 21.35 艘、流量 8.96 次/小时、时长 2.38 小时，利特尔法则 21.35；
  商船在港船时 197.2 船·小时/天；两张敏感性表（九组 + 一次只改一个参数）。

对不上就先查 01 的第 1–4 步，不要往下做。

## 目录

```
.
├── README.md
├── STAGES.md              # 提交清单：每个文件属于哪个阶段（M0–M6）
├── MILESTONES.md          # M1–M6 交什么、现在到哪一步
├── SELFCHECK.md           # 提交前自检：复现包 / 报告 / AI / 路演
├── requirements.txt
├── data/
│   ├── raw/               # 原始 AIS，只读
│   └── clean/             # stops.csv，由 01 生成
├── analysis/
│   ├── b1core.py          # 公共函数：读数据、识别停留
│   ├── 01_clean.py
│   ├── 02_explore.py
│   └── 03_congestion.py
├── figures/               # 图与两张敏感性表，全部由脚本生成
├── narrative/
│   ├── report.md          # 终稿正文（骨架，〔 〕处由本人补写）
│   ├── key_numbers.md     # 03 自动生成的关键数字
│   ├── data_log.md        # 分析决策日志（占总成绩 10%）
│   ├── m3_checkin.md      # M3 当面检查的 8 分钟准备单
│   ├── m5_review_template.md  # M5 互评模板
│   ├── slides_outline.md  # M6 5 页路演大纲
│   └── ai_disclosure.md   # AI 使用披露表
├── tools/
│   ├── build_report.py    # Markdown → Word → PDF
│   └── build_slides.py    # 生成 M6 路演 PPTX（读 sensitivity.csv 与三张图）
├── build/                 # 导出的 docx/pdf（不进版本库）
└── submissions/           # 各次提交的 PDF：m1_proposal.pdf、m2_eda.pdf、m4_draft.pdf、m6_final.pdf、m6_slides.pdf
```

## 导出 PDF

课程要求文档一律交 PDF。不要手动排版，用 `tools/build_report.py` 从 Markdown 生成：

```bash
pip install python-docx          # 只需一次

python tools/build_report.py narrative/m1_proposal.md
python tools/build_report.py narrative/report.md

# 直接生成到 submissions/，文件名就是提交用的名字
python tools/build_report.py narrative/m1_proposal.md --out submissions/m1_proposal.docx
```

生成同名 `.docx` 与 `.pdf`。默认排版：A4、宋体小四、1.5 倍行距、首行缩进两字、
标题黑体、表格带框线且表头跨页重复、图注小五居中、页脚页码。
想微调（字号、页边距、单位名称）改脚本开头的常量，或直接改 `.docx` 后另存为 PDF。

## 路演 PPT

```bash
python tools/build_slides.py            # → build/m6_slides.pptx（6 页）
```

5 页正文 + 1 页附页，16:9，字体微软雅黑，已嵌入主图与九组敏感性表；
每页的演讲提示（说什么、用多少秒）写在 PPT 的备注栏里。〔 〕处填你自己的话。

## 参数

三个参数集中在 `analysis/b1core.py` 开头，改动要在报告里写明理由（第 15 讲第 3 节）：

| 参数 | 默认 | 含义 |
|---|---|---|
| v0 | 0.5 节 | 低于它算停着 |
| tau | 30 分钟 | 停不满这么久不算一次停留 |
| gap | 10 分钟 | 相邻记录断开超过它就结束停留，缺口里的时间不算 |

## 三个容易踩的坑

1. **时间格式**：原始 `timestamp` 是「日/月/年」，读的时候必须 `dayfirst=True`；
   而 `stops.csv` 里已经是 ISO 的「年-月-日」，再传 `dayfirst=True` 会被读成 5 月 7 日——
   次数和时长都不变，但日期错了、按时间切片全空。
2. **缺口规则**：省略它会把缺口中的几小时算进停留，次数变少、时长多出约七成（第 15 讲第 5.1 节）。
3. **别用 Excel 打开再保存 `data/clean/` 里的 CSV**：会把 `2017-07-05 17:53:28` 改成
   `2017/7/5 17:53`（丢秒），浮点数也会被四舍五入。文件一旦被改过，就与脚本输出对不上，
   违反「中间文件必须由脚本生成」。不小心保存了，重跑 `python analysis/01_clean.py` 即可恢复。

## 使用 AI 的说明

`analysis/` 下的代码有模型参与生成，按课程第六节在 `narrative/ai_disclosure.md` 中披露，
并在代码里标出由模型生成的部分、附对话链接。报告正文的论点、解释与结论由本人撰写。
