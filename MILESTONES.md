# 里程碑清单（M0–M6）

**第 02 组 · dream · 文件夹 `02_dream` · B 轨任务包 B1。** 老师允许交网盘，不必用 GitHub。

按《项目工作室手册》第二节整理。每交一次，把状态改成 ✅ 并把 PDF 放进 `submissions/`。

| 里程碑 | 截止 | 交什么 | 对应文件 | 状态 |
|---|---|---|---|---|
| M0 组队 | 第 11 讲上课前 | 02 / dream、组员、B 轨、两句话；不交文件 | 表单 | ☑ 信息已定，待提交 |
| M1 选题书 | 第 11 讲课后 48 小时 | `m1_proposal.pdf`（两页）+ 复现包目录截图 + 网盘链接 | `narrative/m1_proposal.md`（已排成两页） | ☐ |
| M2 数据与探索 | 第 12 讲课后 48 小时 | `m2_eda.pdf` + 网盘链接 | 报告第 2–5 节 + 附录 A、B、三张图、`key_numbers.md` | ☐ |
| M3 当面检查 | 第 13 讲起一周内预约 | 不交文件，带四样材料 | `narrative/m3_checkin.md`、`figures/main.png`、两张敏感性表 | ☐ |
| M4 初稿与代码 | 第 14 讲课后 72 小时，不延期 | `m4_draft.pdf` + 网盘链接 | 报告第 1–6 节，空缺标〔待补〕 | ☐ |
| M5 外部互评 | 第 15 讲课后一周 | 3 份评阅 PDF，每份 ≥12 条 | `narrative/m5_review_template.md` | ☐ |
| M6 终稿与路演 | 路演第 16 讲；终稿结课后一周 | `m6_final.pdf`、`m6_slides.pdf`、网盘链接、数据日志全册 | 报告全文 + `slides_outline.md` + `data_log.md` | ☐ |

## 现在到哪一步

- [x] 复现包骨架：`analysis/` 三个脚本 + `b1core.py`，01 → 02 → 03 从头跑通
- [x] 三张探索图、主图 `main.png`、两张敏感性表（九组 + 一次只改一个）
- [x] 关键数字自动汇总到 `narrative/key_numbers.md`
- [x] 报告骨架 `narrative/report.md`（〔 〕处待本人补写）
- [x] M3 准备单 `narrative/m3_checkin.md`（四样材料 + 2/2/2/2 + 口径五问）
- [x] M5 评阅模板 `narrative/m5_review_template.md`（六环节 × 优点/改进）
- [x] 数据日志 `narrative/data_log.md`（已填 7 条真实决策，待续写）
- [x] 提交自检 `SELFCHECK.md`（复现包 12 分 / 报告 20 分 / AI 8 分逐项）
- [x] M1 选题书骨架 `narrative/m1_proposal.md`，导出的 PDF 正好两页（已验证）
- [x] 排版工具 `tools/build_report.py`：Markdown → Word → PDF，A4/宋体小四/1.5 倍行距/图注/页码
- [x] 组号与组名定了：02 / dream，文件夹 `02_dream`；提交走网盘
- [x] M6 路演 PPTX 模板 `tools/build_slides.py` → `build/m6_slides.pptx`（6 页：正文 5 + 附页 1，含备注）
- [x] 干净目录演练：删掉全部生成物后 01→02→03 通过（退出码 0），`stops.csv`、三张图、两张敏感性表、`key_numbers.md` 与主目录**逐字节一致**
- [x] M2 专用附录：附录 A（对 M1 意见的回应）、附录 B（组内互评 1 记录）已并入 `report.md`
- [ ] 本人补写：`m1_proposal.md` 的问题与「最不确定的地方」，`report.md` 的 1.1–1.2、2.3 末尾、3.3、4.1–4.4、5、6
- [ ] 拿到教师给定的 3 次停留，跑 `python analysis/03_congestion.py <对照表>` 并记录误差
- [ ] 建网盘文件夹、上传 `02_dream`、拿到「未登录可打开」的链接，截目录图（M1）
- [ ] 导出 M1 / M2 / M4 / M6 的 PDF 到 `submissions/`
- [ ] 填 `narrative/ai_disclosure.md`
- [ ] M5：领 3 份别组初稿，按模板写优点与改进

## M5 评阅的固定要求

每份至少 12 条，覆盖**提出问题、获取数据、清洗、探索、分析、表达**六个环节，
每个环节至少一条优点、一条改进，句式只用三种：

- 我喜欢……，因为……
- 我希望……（要具体到可以执行）
- 如果……会怎样？

评之前先按对方的 `README.md` 跑一遍，第一个卡住的地方就是第一条「我希望……」。

## 交之前的三条硬规则

1. 文档一律 PDF；代码不打包 zip，交**网盘分享链接**（整个 `02_dream` 文件夹），确认未登录也能打开。
2. 每次的 PDF 同时以固定名存进 `submissions/`（`m2_eda.pdf` 等）。
3. 逾期 24 小时内 80%，超过不计分；**M4 不接受延期**。
