# Mine-Wiki

**在线阅读 / 网页首页：** [https://zhao-wl.github.io/Mine-Wiki/](https://zhao-wl.github.io/Mine-Wiki/)

从问题出发，把一个知识点的前提、原理、算例与应用逐步讲清。以静态交互网页为主；知识节点独立维护，主题帮助查找，问题路径把节点串成连贯的学习过程。

- [学习首页](index.html)
- [线性代数](topics/linear-algebra/index.html)
- [图形学与坐标变换](topics/graphics-transforms/index.html)
- [审美系统化学习地图](topics/aesthetics/index.html)
- [审美第一单元：观察、解释与偏好](lessons/aesthetics-observation/index.html)
- [问题路径：缩放为零之后，坐标去了哪里？](lessons/zero-scale/index.html)
- [从一个节点开始：基与坐标](knowledge/basis-coordinates/index.html)

保留首批 9 个数学知识节点、零缩放问题路径与 4 个数学实验。新增审美地图的三层、五阶段共 19 个规划节点：第一单元可学习，其余 18 个明确标为待补充。全站共 3 个主题、2 条可学习路径；节点正文与路径由同一源生成，旧入口及章节锚点继续可用。

审美第一单元约 40 分钟，包含证据与判断的短阅读、两个原创 SVG 实验、历史与跨媒介案例、开放练习和自检。一个实验只改间隔分配，另一个只改虚构标题。功能、表达和偏好分开讨论，不评美丑分数。练习默认暂存当前页，点击保存才写入当前浏览器，不上传；与全站自评/疑问独立。详见[交付与验证记录](verification/aesthetics/report.md)。

## 本地阅读

```bash
python3 scripts/preview.py --port 8765
```

打开 `http://127.0.0.1:8765/index.html`。服务器只监听本机，不构成公开部署。页面没有远程脚本、账户或统计；正文和练习答案不依赖 JavaScript，实验提供静态后备。浏览器允许时也可直接打开 HTML；当前受管 Chromium 禁止 `file://`，已验证回环加载后的断网交互。

节点自评跨页面共享，疑问按节点或问题路径分别保存在当前浏览器。旧课程记录会一次性迁入，原记录保留作备份。没有跨设备同步；更换浏览器或域名也不会自动迁移，可先导出 JSON 留底。

## 内容与维护

| 位置 | 作用 |
| --- | --- |
| `content/nodes/*.json` | 独立知识节点的唯一正文源、必要前置、相关节点和状态 |
| `content/paths/*.json` | 问题情境、节点顺序、串讲过渡、案例附录与兼容映射 |
| `content/topics.json` | 主题导航，只引用节点和路径 |
| `content/examples/*.json` / `content/sources.json` | 共享算例、约定和引用资料 |
| `assets/` | 共享数学函数、实验模板、交互和样式 |
| `scripts/` | 标准库生成、关系校验和本地预览 |
| `knowledge/` / `topics/` / `lessons/*/index.html` | 由单一内容源生成的阅读页面 |
| `tests/` / `verification/` | 构建、引用、状态、浏览器与存储迁移检查 |

[内容维护约定](docs/authoring.md)包含稳定 ID、引用、缺失节点、增量修改及旧 URL 兼容规则。[本次迁移验证](verification/migration-report.md)记录具体结果和限制。

```bash
python3 scripts/build_site.py
python3 scripts/build_site.py --check
python3 tests/content_test.py
python3 tests/aesthetics_content_test.py
node --check assets/aesthetics.js
node --test lessons/zero-scale/tests/math.test.js
# 已安装 NumPy、Playwright 和 Chromium 的环境中：
python3 lessons/zero-scale/tests/numpy_oracle.py
python3 tests/browser_test.py
python3 tests/aesthetics_browser_test.py
```

生成和基础校验只需 Python 标准库；数学测试使用 Node。阅读网页不需要这些构建依赖。旧目录下的构建、静态检查、浏览器检查命令仍会调用新入口。

## 离线读者包

```bash
python3 scripts/package_reader.py --output /tmp/mine-wiki-knowledge-reader.zip
```

包内只含阅读页面、所需静态资源和可选历史媒体，会校验本地链接与 ZIP 完整性。这是文件交付，不是网站部署。

## 历史辅助资料

[早期视频、字幕和讲稿](lessons/zero-scale/history.html)保留作回看，不再随知识节点持续维护，也不是每个节点的必配资产。本次没有重渲染视频、下载模型或删除历史媒体。文字导出 `lessons/zero-scale/course.md` 仍由当前问题路径生成，供旧链接和离线阅读使用。
