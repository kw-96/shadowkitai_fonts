# shadowkitai_fonts

shadowkitai 网页项目的设计字库仓：白名单内的源字体经构建得到 `dist/web` 下的 WOFF2 与分家族 `index.css`，通过 **jsDelivr**（公开 Git 源）按 **tag** 固定版本后供主站 **选择性加载**（只引用当前页面需要的家族样式表）。

## 目录说明

| 路径 | 说明 |
|------|------|
| [meta/FONT_POLICY.md](meta/FONT_POLICY.md) | 线上收录与版权原则 |
| [meta/whitelist.json](meta/whitelist.json) | 参与构建的家族白名单 |
| [meta/manifest.json](meta/manifest.json) | 构建生成的机器可读清单（**提交前需已执行构建**） |
| `sources/<家族>/fonts/` | 白名单内源字体与 `LICENSE.txt`（每家族父目录仅许可证 + 子目录字体，单目录文件数受控） |
| `dist/web/<家族Id>/` | 发布用：`index.css` + `files/*.woff2`（CSS 内为相对路径，可挂在任意 `dist/web` 根下） |
| [tools/build_web_fonts.py](tools/build_web_fonts.py) | 从白名单构建 WOFF2、分家族 CSS、manifest |
| [tools/organize_root_fonts.py](tools/organize_root_fonts.py) | 将根目录散落的字体按名称表族名归入 `sources/`，并合并进 `whitelist.json` |
| [integration/shadowkitaiFontLoader.example.ts](integration/shadowkitaiFontLoader.example.ts) | 主项目按需 `link` 引入的 TypeScript 示例（可复制到 shadowkitai） |

## 根目录整理与 `root-*` 条目

若根目录有新放入的字体，可执行：

```text
python tools/organize_root_fonts.py
```

脚本会读取各文件名称表中的 **族名** 聚类，每族每目录最多 8 个文件，移入 `sources/root-<slug>/fonts/`，并在 [meta/whitelist.json](meta/whitelist.json) 中追加条目。新追加条默认可为待审；当前库内多数家族已标记为 **`licenseId: project-approved`** 且 **`skipBuild: false`**（**仅 `.fon` 位图、无法转 WOFF2** 的家族保持 `skipBuild: true`）。全量构建 **耗时长、产物体积大**，建议在 CI 或本地夜间跑 `python tools/build_web_fonts.py` 并提交 `dist/`。

已审录的四个家族（思源、Source Code Pro、HarmonyOS SC）**不要** 写 `cssName` 字段，以便构建使用与字体文件一致的英文 `font-family`（见 [tools/font_weight_rules.py](tools/font_weight_rules.py) 中的映射）。

## 构建

```text
python -m pip install -r requirements.txt
python tools/build_web_fonts.py
```

说明：

- 构建耗时与磁盘性能相关，大体积中文源字体可能需等待十余分钟属正常现象。
- 若需在 `meta/manifest.json` 中写入可读的 CDN 根路径（供工具链拼接），可附加参数，例如：  
  `python tools/build_web_fonts.py --cdn-base "https://cdn.jsdelivr.net/gh/<你的GitHub用户或组织>/shadowkitai_fonts@<tag>/dist/web"`
- 分家族 `index.css` 内为 **相对路径**（`files/*.woff2`），换 GitHub 账户或 **tag** 时通常 **无需** 重新构建，除非字体文件有变更。

## 发布与 jsDelivr 地址

1. 将含 `dist/web` 与 `meta/manifest.json` 的提交推送到 GitHub 公开库。
2. 打带版本号的 **annotated 或 light tag**（如 `v0.1.0`），与文档、主项目配置保持一致。
3. 各家族样式表 URL 模板为：

   `https://cdn.jsdelivr.net/gh/<GitHub用户或组织名>/<仓库名>@<tag>/dist/web/<家族Id>/index.css`

4. 清单 `manifest` 的完整 URL 示例：

   `https://cdn.jsdelivr.net/gh/<GitHub用户或组织名>/<仓库名>@<tag>/meta/manifest.json`

请将 `<...>` 替换为实际值；生产环境应 **固定 tag**，避免使用会移动的 `main` 分支名作为线上引用。

## 在 shadowkitai 中选择性加载

- **推荐**：仅在需要该字体的页面或布局中注入对应 `index.css`（`link rel="stylesheet"` 或构建工具按需 `import` 远程 URL，依主项目栈而定），勿在根 layout 中一次性引入全部家族。
- 可参考 [integration/shadowkitaiFontLoader.example.ts](integration/shadowkitaiFontLoader.example.ts) 中 `loadFontFamilyStylesheet(cdnBase, familyId)`，先判断是否已注入再插入 `link`，避免重复。
- 使用 `font-family` 时请与分家族 `index.css` 中 `font-family` 名称一致（如「Source Han Sans CN」等）。

## 根目录与未跟踪文件

当前环境若大量字体为未 `git add` 状态，在纳入版本前请通过 `.gitignore` 与 Git LFS 等策略控制体积，并**仅**将已授权、已列入白名单的 `sources/**` 与 `dist/**` 提交为线上分发内容。
