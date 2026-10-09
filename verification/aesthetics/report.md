# 审美地图与第一单元：交付与验证

核查日期：2026-10-09。本次完成本地实现、浏览器验证和提交；未推送、未合并 main、未部署，未调用或修改 Sites。

## 基线与范围

- 远端 `learning/zero-scale-chinese-case`：`ad90936aa85c745aa2433a6a3e3cc42e3c1a356d`，包含 `39c85255b108e2aa9a00537bdc7e357482935c0e` 及 `df535c0` 的原子内容结构。远端 main 为 `324af413162d59f8ec1183f0d3479abc479f624d`，仍是较旧的连续课程。已刷新本地两条远端引用，未以初始缓存的 origin/main 作基线。
- 工作分支：`learning/aesthetics-map-unit-1`，从 ad90936 创建。核查时远端没有同名分支。新增本地提交的 SHA 见最终交付消息或 `git log -1`。
- 未发现仓库或工作区的 AGENTS.md / .agents/skills；按 `docs/authoring.md` 实施。
- 三层共 19 个审美节点：共通基础 9、跨领域研究 7、软件与游戏应用 3；五阶段建议节奏。仅第一单元 ready，18 个 stub。地图和首页从状态计算完成数量，未完成节点不能自评掌握。
- 首课约 40 分钟（阅读约 15、练习约 25），目标是证据描述、多种解释、条件与可检验预测；软件/游戏练习从首课存在，结课要求迁移至绘画、摄影或游戏镜头，保留待核实背景问题。

## 文件与实现

| 文件 | 作用 |
| --- | --- |
| `content/topics.json` | 三层、五阶段地图，历史调查问题及节点引用 |
| `content/nodes/observation-interpretation-preference.json` | 唯一首课正文：问题、原理、例证、边界、案例、练习与来源 |
| 其余新增 `content/nodes/*.json` | 18 个明确待补充的范围登记 |
| `content/paths/aesthetics-observation.json` | 首课目标、节点引用、过渡与迁移自检 |
| `content/sources.json` | LOC、Met、Reading 的出处与支持边界，新条目注明核查日期 |
| `assets/labs.html` / `assets/aesthetics.js` | 共用原创 SVG 实验与本地练习增强；仅含实验的页面加载审美脚本 |
| `assets/styles.css` | 复用阅读布局，增加地图、案例、练习和响应式样式 |
| `scripts/knowledge.py` / `scripts/build_site.py` | 兼容性扩展与生成；不增加库或框架 |
| `scripts/package_reader.py` | 离线包包含新脚本，保持资源白名单与链接校验 |
| `tests/aesthetics_*` / `tests/browser_test.py` | 新内容/浏览器检查；原测试适应第三个主题，可把证据输出到临时目录 |
| `.github/workflows/lesson-checks.yml` | 增加审美内容校验与 JS 语法检查；没有发布动作 |
| `topics/aesthetics/index.html` / `knowledge/*/index.html` / `lessons/aesthetics-observation/*` | 从单一源生成的读者页面、文字与 JSON 导出 |
| `README.md` / `docs/authoring.md` | 入口、维护、状态与记录机制说明 |

扩展为可选 question、boundaries、cases、context 和主题 learning_map；非数学路径可以没有 example。requires 仍只表示必要先修，related 仍为可选双向延伸，context 为有理由的定向语境关联，不加入先修图。没有给审美强造数学前置。

六矩形实验固定画布、矩形宽高颜色、基线、左右端点和总间隔 160；A 间隔为 32/32/32/32/32，B 为 8/68/8/68/8。展开不改变 A 的显示尺寸，桌面并排、窄屏上下比较。初看观察和预测先写，返回保留文字，重置可多次运行。另一实验固定四圆 SVG，只切换“独处”“被落下”等明确虚构的教学标题。它们是形式/语境的观察练习，不是群体心理研究。

陈述可拆分或注明“需补充条件”。“我觉得拥挤”保留为个体感知；“红色更醒目”不无条件视为事实。自检关注证据、替代解释、目的与可检验性；程序仅提示记录遗漏，不能自动判定解释正确，不奖励选中某种风格。功能、表达与偏好各有独立记录。

所有页面图形为原创 SVG/CSS；历史图像只提供馆藏/研究链接，未下载、复制或嵌入外部图片。没有加入 Z1 私人报告、缓存、提示词、测试数据，也未新增音视频。

## 保存机制

13 个练习字段、4 个自查项默认暂存当前页面。主动保存才写入 localStorage 键 `mine-wiki.aesthetics.observation.v1`；节点与首课共用。返回 A 保留文字，重置清当前页面并保留已保存副本，删除只移除这个专用键且保留当前文字。保存失败或格式/版本不兼容时不覆盖原值，当前练习仍可导出。另一标签页变更时提示，保留本页未保存文字。没有上传、网络请求、跨设备同步或自动导入。

全站自评与疑问仍使用 `mine-wiki.learning.v1` 的既有机制。旧 `mine-wiki.zero-scale.v1` 的迁移、备份和清除语义不变；练习与全站记录独立。浏览器、域名、端口改变后不能自动拿到旧来源的记录。

## 实测结果

| 检查 | 结果 | 证据/边界 |
| --- | --- | --- |
| `python3 scripts/build_site.py --check` | 通过 | 28 节点、2 路径、3 主题、10 先修边、43 个生成文件与源一致 |
| `python3 tests/content_test.py` | 28 项通过 | 原引用、稳定 ID、锚点、状态、循环、单一源和旧 URL 检查 |
| `python3 tests/aesthetics_content_test.py` | 9 项通过 | 地图覆盖、真实状态、context 独立、案例来源、可选锚点和无公式路径 |
| `node --check assets/aesthetics.js` | 通过 | JS 语法 |
| `node --test lessons/zero-scale/tests/math.test.js` | 20 项通过 | 原数学分支与算例 |
| `python3 lessons/zero-scale/tests/numpy_oracle.py` | 240 算例通过 | 独立 NumPy；最大回代残差约 3.55e−15 |
| `python3 tests/aesthetics_browser_test.py` | 73 项通过 | Chromium 实际加载、键盘、触屏、重复操作、几何不变量、存储/导出、离线、本地资源 |
| `MINE_WIKI_BROWSER_OUT=/tmp/mine-wiki-zero-regression python3 tests/browser_test.py` | 131 项通过 | 原 9 单元/4 实验、旧锚点、数学互动、存储迁移及共享自评 |
| `python3 lessons/zero-scale/tests/static_test.py` | 通过 | 旧入口调用当前内容校验 |
| `python3 lessons/zero-scale/tests/media_test.py` | 已执行项目通过 | 旧视频解码、时长、字幕时间与 7 个代表帧；原渲染缓存不存在，字幕截图与缓存比对未测试 |
| `python3 scripts/package_reader.py --output /tmp/mine-wiki-aesthetics-reader.zip` | 通过 | 50 文件、35 HTML；ZIP CRC 与所有本地链接/锚点；最终包在提交后重新生成 |
| `git diff --check` | 通过 | 无空白错误 |

审美浏览器检查覆盖 320、390、768px 的地图/单页/路径/stub，展开前后固定显示尺寸、返回/多次展开/重置、键盘切换标题与触屏操作、无 JS 的静态对比和答案、专用键保存/删除/导出、与旧记录隔离、损坏/未来版本/存储拒绝/配额耗尽、回环加载后断网运行。额外模拟 `/Mine-Wiki/` 项目 URL 前缀，确认相对链接与脚本不丢失。学习页面无 JavaScript 错误，无远程资源请求或答案上传。

已实际查看 [桌面地图](map-desktop.png)、[手机地图](map-mobile.png)、[首课桌面](unit-desktop.png)、[桌面对比](comparison-desktop.png)和[手机实验](experiment-mobile.png)截图：字体与对比可读、长中文换行正常、按钮和图形未被裁切。完整清单见 [首课结果](browser-results.json)、[零缩放回归](zero-scale-regression-results.json)与[历史媒体检查](media-regression-results.json)。测试所用文字为公开的固定教学用句，不含私人资料。

开发时首轮导出断言把 13 个字段误写为 14，测试中断；已修正断言并完整重跑通过。最终没有未解决的失败。

未测试：真实读者学习效果、群体知觉实验、屏幕阅读器真人会话、Safari/Firefox/真实手机、Unity 运行时。受管 Chromium 的 file:// 打开仍被策略阻止，已使用既有回环预览与加载后断网验证，没有绕过策略。未取得仓库 Pages 设置或线上页面的可访问结果：公开 API 的终端代理返回 403，浏览工具也无法读取现有站点。发布源设置与发布后的线上效果尚未验证；这不影响本地交付。

## 保留与复核

相对于 ad90936，原 9 个数学节点 JSON、zero-scale 路径 JSON、数学/记录 app.js、math.js、课程 Markdown/JSON 及历史媒体均无差异。原知识页与零缩放页面重新生成，只增加审美主题导航；原主题页的卡片另增加状态属性以共用样式，正文与引用未改变。旧 labs/styles URL 同步共享资产。旧全部章节/实验锚点保留，原页面没有加载审美 JS。

## 本地预览与 GitHub Pages 后续步骤

在仓库根目录运行：

```bash
python3 scripts/preview.py --port 8765
```

- 首页：`http://127.0.0.1:8765/index.html`
- 地图：`http://127.0.0.1:8765/topics/aesthetics/index.html`
- 首课：`http://127.0.0.1:8765/lessons/aesthetics-observation/index.html`
- 单节点：`http://127.0.0.1:8765/knowledge/observation-interpretation-preference/index.html`
- 旧路径：`http://127.0.0.1:8765/lessons/zero-scale/index.html`

服务器仅监听回环，不构成部署。停止按 Ctrl+C。离线包可解压后在目录内运行 `python3 -m http.server 8765 --bind 127.0.0.1`。Git bundle 与读者 ZIP 在 /tmp，最终交付消息提供路径。

**以下属于后续外部操作，本次未执行。** 推送目标为 `Zhao-wl/Mine-Wiki` 的 `learning/aesthetics-map-unit-1`，内容是地图、首课及其校验、文档、生成页面，且保留该基线已有的原子迁移。发布目标只有现有 GitHub Pages 站点 `https://zhao-wl.github.io/Mine-Wiki/`。

1. 取得推送授权后，在仓库执行 `git push --set-upstream origin learning/aesthetics-map-unit-1`，不 force push。用 GitHub 的比较页面创建以 main 为 base、该分支为 head 的 PR。PR 相对 main 还会包含基线的原子结构迁移，不能只 cherry-pick 本次提交到旧 main 后直接发布。
2. 在合并前确认 Settings → Pages 当前 source；如果已经从 main 发布，合并即可能启动发布，所以合并与发布须有相应授权。审阅完整差异，等待 Lesson checks 成功，并再次确认原零缩放路径。
3. 经批准合并后，用仓库 Settings → Pages → Build and deployment → Source 选择 **Deploy from a branch**，Branch 选 **main**，Folder 选 **/(root)**，Save；若当前已经如此则保留设置。仓库现有 Lesson checks 只校验，不能当成 Pages 部署工作流。页面已由脚本生成并随提交保存，无须引入新构建平台。操作依据：[GitHub 官方发布源说明](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。
4. 在 Actions 检查 Pages build/deployment 对应合并提交成功；再打开现有首页、`/Mine-Wiki/topics/aesthetics/index.html`、`/Mine-Wiki/lessons/aesthetics-observation/index.html` 和旧零缩放链接，实际核对交互、窄屏与 localStorage 来源边界。当前没有声称这些新 URL 已上线。

若授权尚未给出，停在本地提交和这些可审阅成果即可；不要变更 main、Pages 设置或其他托管平台。
