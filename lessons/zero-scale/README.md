# 案例 001：零缩放与换父节点

主入口：[index.html](index.html)。9 节完整课程、4 个 SVG 图解、4 个交互实验，以及 13 段图解讲解组成的中文视频。文字课程约 90 分钟精读；视频约 8 分 10 秒，作为导读/复习，不代替逐步练习。

## 文件结构与共同事实

| 文件 | 用途 |
| --- | --- |
| `course.json` | 九节正文、例题、练习答案、数值事实与官方引用的源数据 |
| `scripts/build_site.py` | 标准库生成完整静态 HTML、Markdown 与原创 SVG |
| `index.html` / `course.md` | 可离线阅读的课程成品；改正文应先改源数据，再生成 |
| `assets/*.svg` | 点与位移、父子链、坍缩、贯穿算例四幅图解 |
| `math.js` | 列向量模型的纯数学函数，供交互与测试共用 |
| `app.js` / `labs.html` / `styles.css` | 四个实验、键盘/触控、响应式布局、本地学习记录 |
| `video.json` | 逐场讲解、图板文字；对应同一章与贯穿算例 |
| `scripts/build_video.py` | 本地 TTS、原创图板、字幕时间码、H.264/AAC 编码 |
| `media/lesson-zh.mp4` | 1280×720、12fps，真实中文声轨，烧录字幕及内嵌字幕轨 |
| `media/lesson-zh.srt` / `.vtt` | 与实际合成语音段落对应的 76 条字幕 |
| `media/transcript.md` / `timing.json` | 完整逐字稿、画面提要与实际时间码 |
| `tests/` / `verification/` | 可重复检查及本次结果与截图 |

统一使用列向量、x 右 y 上、右侧先执行。`F_s(x,y)=(3-y,2+s*x)`；`s=2` 时 `(1,1)→(2,4)`；精确零直接进入可达性/解集分支，没有 epsilon 代换。数组按行存储不改变列向量的数学约定。

求解器面向本课受控数字，精确检查行列式和共线性，不是通用生产级浮点秩判定器。回代残差独立显示；数值测试中的容差仅用于验算，不会改输入或把零替换成小数。三维推广使用同样方程，但实验只演示二维。

## 阅读、交互与本地记录

建议依次阅读 01–09，先预测再操作。每个实验有重置、键盘输入和静态后备；基向量端点还支持鼠标和触控拖动。HTML 正文不依赖 JavaScript，原生 `details` 可展开练习答案。页面可打印。

学习勾选和疑问使用单一 `localStorage` 键 `mine-wiki.zero-scale.v1`。不上传、不分析、不自动请求外部资料。记录可清除或导出为 JSON；浏览器禁用存储时会明确提示。外部引用只在主动打开链接时联网。

```bash
python3 lessons/zero-scale/scripts/preview.py --port 8765
```

预览只绑定 `127.0.0.1`，并支持视频 HTTP Range 拖播。入口 `http://127.0.0.1:8765/lessons/zero-scale/`。也可以在允许本地文件的浏览器中打开 `index.html`；本次受管 Chromium 的 `file://` 被管理员策略禁用，因此不声称已验证直接双击。

## 重建课程与运行检查

以下命令在仓库根目录执行。阅读成品无需任何依赖。生成页面仅需 Python 3 标准库；数学测试需要 Node 22 或更新版本。

```bash
python3 lessons/zero-scale/scripts/build_site.py
node --test --test-reporter=tap lessons/zero-scale/tests/math.test.js
python3 lessons/zero-scale/tests/static_test.py
```

本次环境另有 NumPy、Pillow、Playwright、Chromium 和 FFmpeg，用于独立数值、真实浏览器与视频检查：

```bash
python3 lessons/zero-scale/tests/numpy_oracle.py
python3 lessons/zero-scale/tests/browser_test.py
python3 lessons/zero-scale/tests/media_test.py
```

`browser_test.py` 自带临时回环服务器，执行后关闭；`media_test.py` 在本次渲染工作目录仍可用时，还将抽取的成片字幕画面与原始渲染帧比较。换一台机器未保留中间帧时，仍执行全片解码、声轨、时间轴与抽帧检查，但不会虚报原始帧比对。

## 重建中文视频

声音使用 **eSpeak NG 1.52.0 / cmn**，165 字速参数，离线合成，机械音色。没有调用收费语音服务、配置凭据或上传文稿。工具只解压在工作区目录；源码、依赖包和临时 WAV/PNG 未纳入仓库。

原始来源为 Debian 官方包，版本、下载地址及 SHA-256 见 [tts-provenance.json](tts-provenance.json)。可使用系统已有 eSpeak NG，或将已知官方包按锁定哈希解压到指定工具目录：

```bash
# 此步需联网下载锁定的 Debian 包；不安装到系统、不执行包安装脚本。
python3 lessons/zero-scale/scripts/prepare_tts.py --destination /tmp/mine-wiki-tts
# 以下合成完全离线。--tts-root 指向含 usr/bin/espeak-ng 的根。
python3 lessons/zero-scale/scripts/build_video.py \
  --tts-root /tmp/mine-wiki-tts/root \
  --work /tmp/mine-wiki-video
python3 lessons/zero-scale/tests/media_test.py --render-work /tmp/mine-wiki-video
```

渲染依赖 Pillow、FFmpeg 的 libx264/AAC 编码器以及 `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`。若路径不同，调整脚本顶部 `FONT`。画板将部分上下标转为 ASCII（如 `10^-6`），避免字体缺字；正文仍保留标准排版。

每条字幕独立合成中文音频，段落加短暂停顿并对齐到 12fps；画板、声轨、SRT、VTT 使用同一时间轴。成片码率控制在约 10 MiB 以内。本次视频约 5.8 MiB；无需 Git LFS。视频是带配音的分段图解讲解，不是交互录屏，也不冒充真人讲师。

## 边界

- 数学模型不替项目决定零缩放处理策略，不实施旧讨论中未批准的方案。
- Unity 引用固定在 6.0。`Matrix4x4.inverse` 的零行列式返回 `Matrix4x4.zero` 属于文档契约；`SetParent` 奇异父级行为未经本环境实测。
- 一般仿射可解性、世界原点可达性、TRS 可表示性、数值精度分别讨论，不能互相替代。
- 本次音频有全片解码、非静音、截幅及字幕对齐检查；尚未进行真人逐句听审，不能把这些自动检查说成自然度或每个读音都经人工确认。
