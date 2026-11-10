# 提交清单与阶段标注

**第 02 组 · dream · B 轨任务包 B1「港口停留与拥堵」**
当前阶段：**M1（选题书）准备中**——骨架与数据已就绪，等你补 4 处文字后导出 PDF。

## 一、本包怎么用

1. 复现包两个地址：GitHub <https://github.com/jyn0219/02-dream>（Public，未登录可打开）；
   百度网盘 <https://pan.baidu.com/s/1WxaMt8N6uSU3-MNC3MpNjA?pwd=j54x>（提取码 j54x）。
2. 助教拿到后按 `README.md` 的三条命令即可从头跑：
   `python analysis/01_clean.py` → `02_explore.py` → `03_congestion.py`。
3. `data/raw/` 里已带原始 AIS，不需要另外下载。

## 二、按阶段看文件

| 阶段 | 交付物 | 在包里的位置 | 状态 |
|---|---|---|---|
| M0 | 组队信息（不交文件） | 表单 | 已定：02 组 / dream / B 轨 |
| M1 | 选题书 PDF（两页） | `narrative/m1_proposal.md` → 导出 `build/m1_proposal.pdf` | 骨架完成，**待补 4 处**〔〕 |
| M1 | 复现包目录截图 | 自己运行 `tree /F` 截图 | 待做 |
| M1 | 网盘链接 | 表单「复现包」一栏 | 待上传后填 |
| M2 | 检查点报告 | `narrative/report.md` 第 2–5 节 + 附录 A、B | 骨架完成，正文待写 |
| M2 | 三张探索图 | `figures/fig1_duration.png`、`fig2_ship_profile.png`、`fig3_occupancy.png` | 已生成 |
| M2 | 关键数字表 | `narrative/key_numbers.md` | 已生成（脚本自动） |
| M3 | 主图 | `figures/main.png` | 已生成（由 02 脚本产出） |
| M3 | 参数敏感性表 | `figures/sensitivity.csv`、`sensitivity_one_at_a_time.csv` | 已生成 |
| M3 | 8 分钟准备单 | `narrative/m3_checkin.md` | 已备（口径五问已填） |
| M4 | 初稿 | `report.md` 第 1–6 节 | 骨架，空缺标〔待补〕 |
| M5 | 互评模板 | `narrative/m5_review_template.md` | 模板 |
| M6 | 终稿 | `report.md` 全文第 1–8 节 + 摘要 | 骨架 |
| M6 | 路演 PPT | `tools/build_slides.py` → `build/m6_slides.pptx`（6 页，含备注） | 模板完成 |
| M6 | AI 使用披露表 | `narrative/ai_disclosure.md` | 六项待填 |
| M6 | 数据日志全册 | `narrative/data_log.md`（占总成绩 10%） | 已填 10 条，待续写 |

## 三、哪些能直接交，哪些还不能

- **能交**：`figures/` 全部图与表、`narrative/key_numbers.md`、代码与 README（作为复现包的一部分）。
- **不能直接交**：`build/` 里的 PDF 都带〔 〕占位符，是排版预览；补完文字后重新导出，
  放到 `submissions/` 下再交。
- **不要交**：`.venv/`（如果本地建了虚拟环境）、`.idea/`（PyCharm 配置）、`.mplcache/`、`__pycache__/`。
  这些是本机环境，不是成果；仓库和压缩包都已排除。

## 四、复现包目录（手册第四节）

```
02_dream/
├── README.md              运行说明、预期结果、提交方式
├── MILESTONES.md          M0–M6 交什么、到哪一步
├── SELFCHECK.md           提交前逐项自检
├── data/raw/              原始 AIS（只读）
├── data/clean/            stops.csv（01 生成）
├── analysis/              b1core.py、01_clean.py、02_explore.py、03_congestion.py
├── figures/               图与敏感性表（全部由脚本生成）
├── narrative/             报告、选题书、关键数字、数据日志、M3/M5 模板、AI 披露
├── tools/                 排版工具（md→docx→pdf、路演 PPTX）
├── build/                 导出的 docx/pdf/pptx（预览用，不进版本库）
└── submissions/           最终提交的 PDF 放这里
```

## 五、复现与验证

- 干净目录演练通过：删掉全部生成物后 01→02→03 退出码为 0，
  `stops.csv`、三张图、两张敏感性表、`key_numbers.md` 与主目录逐字节一致。
- 基线数字：215 次停留、56 艘船、512.5 小时；商船 46 次、197.2 船·小时/天。
- 分析代码无绝对路径；仅 `tools/build_report.py` 内含本机 LibreOffice 路径，可用环境变量覆盖。
