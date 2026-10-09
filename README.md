# Mine-Wiki

**在线阅读 / 网页首页：** [https://zhao-wl.github.io/Mine-Wiki/](https://zhao-wl.github.io/Mine-Wiki/)

从实际问题出发，按前置知识循序补习的中文学习案例。页面为静态文件，无账户、无统计、无远程运行依赖。

## 学习案例

### 001 · 缩放为零之后，坐标去了哪里？

围绕父节点某轴零缩放时的换父/挂点问题，从点、向量、基与矩阵开始，走到逆、核、秩、数值误差和完整世界变换。

- [课程主入口：交互 HTML](lessons/zero-scale/index.html)
- [完整文字课程](lessons/zero-scale/course.md)
- [中文讲解视频 MP4](lessons/zero-scale/media/lesson-zh.mp4)（约 8 分 10 秒，约 5.8 MiB）
- [字幕与逐字稿](lessons/zero-scale/media/transcript.md)
- [验证报告](lessons/zero-scale/verification/report.md)
- [实现结构与复现](lessons/zero-scale/README.md)

下载或克隆后，可打开根目录 `index.html`。若浏览器禁止 `file://` 或需要视频分段拖播，使用只监听本机的预览：

```bash
python3 lessons/zero-scale/scripts/preview.py --port 8765
```

随后打开 `http://127.0.0.1:8765/lessons/zero-scale/`。这不构成公开部署。受管 Chromium 对 `file://` 的限制已记录在验证报告中。

目录以 `lessons/<case-slug>/` 扩展；已有案例独立维护，不覆盖历史内容。
