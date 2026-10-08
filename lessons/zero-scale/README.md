# 问题路径：零缩放与换父节点

[连续阅读](index.html) · [知识与主题首页](../../index.html) · [维护约定](../../docs/authoring.md)

这条路径现在引用九个共享知识节点。节点正文在 `content/nodes/`；本问题的顺序、过渡、应用边界与旧记录映射在 `content/paths/zero-scale.json`。四个交互实验和公共样式在根目录 `assets/`。

本目录的 `index.html`、`course.json`、`course.md` 和公共 JS/CSS/实验模板副本由生成器维护，请勿直接改这些兼容产物。旧入口、九节锚点与实验锚点保持可用。旧本地记录会映射到稳定节点 ID，并保留原始备份。

```bash
# 仓库根目录执行；旧命令仍然可用
python3 lessons/zero-scale/scripts/build_site.py
python3 lessons/zero-scale/tests/static_test.py
node --test lessons/zero-scale/tests/math.test.js
python3 lessons/zero-scale/tests/browser_test.py
```

当前模型仍采用列向量、x 右 y 上、右侧先执行。`F_s(x,y)=(3-y,2+s*x)`；旧父奇异与新父奇异、仅保持位置与完整矩阵、矩阵可解与 TRS 可表示性分别讨论。求解器针对受控教学输入，不是通用浮点秩判定器；Unity 奇异父级行为仍未实测。

[新迁移验证报告](../../verification/migration-report.md)记录节点、引用、交互和学习记录检查。[原始验证报告](verification/report.md)仅代表初版课程，不作为后续变更的实时结果。

## 历史辅助资料

[历史视频与字幕入口](history.html)保留初版 eSpeak 中文导读。`media/`、`video.json`、原始 TTS 来源及视频工具均保留，本次未改写或重渲染媒体。视频不再进入默认学习流程，不要求每个节点具备视频；Kokoro 配音任务已取消。

历史视频工具需要当时的本地 eSpeak、FFmpeg、Pillow 与字体环境；不属于本次网页构建的依赖。不要把初版视频讲稿当作当前知识节点的唯一正文源。
