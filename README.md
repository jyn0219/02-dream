# 02 dream · B1 港口停留与拥堵：复现包

《航运与物流大数据分析》模块 C 结课项目，第 02 组（dream），B 轨任务包 B1。
用哥德堡港 2017 年 7 月 5 日一天的 AIS 船位，识别油轮与货船的停留，估计停留时长的分布，
给出一个拥堵指标，并说清它的口径与局限。

数据：丹麦海事局（DMA）AIS 开放数据（官），经 movingpandas-examples 整理为课程样本包；
84,702 行、100 艘船、8 个字段。免费使用，须署名。

**提交方式**：两个地址都提供，内容相同——

- GitHub：<https://github.com/jyn0219/02-dream>（Public，未登录可浏览）
- 百度网盘：<https://pan.baidu.com/s/1WxaMt8N6uSU3-MNC3MpNjA?pwd=j54x>（提取码 `j54x`）

每完成一个里程碑 push 一次并更新网盘；提交表单里两个地址都填。助教按下面的三条命令即可从头运行。
`data/raw/` 里已带原始数据，不需要另外下载。

## 快速开始（新电脑 / 教室电脑）

Windows 上克隆仓库后，双击（或在命令行运行）一键脚本：

```bat
git clone https://github.com/jyn0219/02-dream.git
cd 02-dream
tools\setup_windows.bat
```

脚本会依次：显示当前解释器 → 按 `requirements.txt` 装依赖 → 运行环境自检。
没有 Python 就先装 3.12（装到用户目录即可，不需要管理员权限）。

克隆下来的目录名是 `02-dream`（连字符），本地文件夹叫 `02_dream`（下划线）也不影响——
脚本和文档里全是相对路径，不依赖目录名。

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

**环境**：课程标准环境是 Python 3.12 的 conda 环境 `shipping`（`conda activate shipping`）。
不确定依赖齐不齐，先跑 `python tools\check_env.py`：它打印每个包的版本，缺包时给出安装命令。
本项目**不需要**虚拟环境；`.venv/`、`.idea/`、`build/` 都不进仓库。

**预期结果**（默认参数 v0=0.5 节、tau=30 分钟、gap=10 分钟）：

- 01：停留 215 次、56 艘船、合计 512.5 小时，时长中位数 75.8 分钟；
- 02：`figures/` 下四张 PNG（fig1 分布、fig2 关系、fig3 时间、main 主图）；
- 03：存量 21.35 艘、流量 8.96 次/小时、时长 2.38 小时，利特尔法则 21.35；
  商船在港船时 197.2 船·小时/天；两张敏感性表（九组 + 一次只改一个参数）。

对不上就先查 01 的第 1–4 步，不要往下做。

## 数据从哪里来

| 文件 | 来源 | 性质 | 下载日期 |
|---|---|---|---|
| `data/raw/ais_gothenburg_20170705.csv` | 丹麦海事局（DMA）AIS 开放数据，经 movingpandas-examples 整理为课程样本包 | 官 | 2026-10-29 |
| `data/raw/ais_gothenburg_20170705.zip` | 同上（同一文件，压缩版） | 官 | 2026-10-29 |

原始文件的 SHA-256 记在报告第 2.1 节；`analysis/01_clean.py` 会打印读入行数与缺口数，可与报告核对。

## 目录

```
.
├── README.md
├── STAGES.md              # 提交清单：每个文件属于哪个阶段（M0–M6）
├── MILESTONES.md          # M1–M6 交什么、现在到哪一步
├── SELFCHECK.md           # 提交前自检：复现包 / 报告 / AI / 路演
├── requirements.txt       # pandas、numpy、matplotlib、python-docx、python-pptx
├── .gitattributes         # 换行符规则（.bat 强制 CRLF）
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
│   ├── report.md          # 终稿正文（10 页，无占位）
│   ├── m1_proposal.md     # M1 选题书（两页）
│   ├── m2_eda.md          # M2 检查点报告（由 report.md 抽取拼装）
│   ├── key_numbers.md     # 03 自动生成的关键数字
│   ├── data_log.md        # 分析决策日志（占总成绩 10%）
│   ├── m3_checkin.md      # M3 当面检查的 8 分钟准备单
│   ├── m5_review_template.md  # M5 互评模板
│   ├── slides_outline.md  # M6 5 页路演大纲
│   └── ai_disclosure.md   # AI 使用披露表
├── tools/
│   ├── setup_windows.bat  # 一键装依赖 + 自检（新电脑先运行这个）
│   ├── check_env.py       # 检查依赖是否齐全
│   ├── build_report.py    # Markdown → Word → PDF
│   ├── build_m2.py        # 从 report.md 拼装 M2 检查点报告
│   ├── build_slides.py    # 生成 M6 路演 PPTX（读 sensitivity.csv 与三张图）
│   └── show_tree.py       # 打印目录树（M1 截图用）
├── build/                 # 导出的 docx/pdf/pptx（不进版本库）
└── submissions/           # 各次提交的 PDF：m1_proposal.pdf、m2_eda.pdf、m4_draft.pdf、m6_final.pdf、m6_slides.pdf
```

## 导出 PDF

课程要求文档一律交 PDF。不要手动排版，用 `tools/build_report.py` 从 Markdown 生成：

```bash
python tools\check_env.py        # 确认 python-docx 已装

python tools/build_report.py narrative/m1_proposal.md
python tools/build_report.py narrative/report.md

# 直接生成到 submissions/，文件名就是提交用的名字
python tools/build_report.py narrative/m1_proposal.md --out submissions/m1_proposal.docx
```

生成同名 `.docx` 与 `.pdf`。PDF 转换用的是本机的 LibreOffice Kit；换到没有它的电脑时，
加 `--no-pdf` 只生成 `.docx`，再用 Word 另存为 PDF。脚本开头的 `NODE` / `CLI` 是本机路径，
换机器用环境变量 `LO_NODE` / `LO_CLI` 覆盖即可；`analysis/` 下的分析脚本没有任何绝对路径。
默认排版：A4、宋体小四、1.5 倍行距、首行缩进两字、
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

## 已知的问题

这些限制在报告第 5 节逐条写成「因为……，所以不能回答……」，这里列成清单便于核对：

- **只覆盖港区水域**，没有码头、泊位和锚地边界：`在港停留`是代理指标，不等于等泊时间；
- **只有 2017-07-05 一天**：不能外推到季节、周内节律或长期趋势；
- **日界截断**：10 次停留贴近日界、共 76.0 船·小时，只能视为当日观测下界；
- **最短停留 30 分钟**：会漏掉渡轮、引航艇的短靠泊，主指标只覆盖油轮与货船；
- **关闭 AIS 或采样中断的船不在数据里**：不能据此推断全港真实船舶总量；
- **参数只在有限范围检验**：v0 0.2–1.0 节、tau 10–60 分钟、gap 10 分钟；
- **工具依赖**：`tools/build_report.py` 依赖本机 LibreOffice Kit，路径可用 `LO_NODE` / `LO_CLI` 覆盖。

## 使用 AI 的说明

`analysis/` 下的代码有模型参与生成，按课程第六节在 `narrative/ai_disclosure.md` 中披露，
并在代码里标出由模型生成的部分、附对话链接。报告正文的论点、解释与结论由本人撰写。
