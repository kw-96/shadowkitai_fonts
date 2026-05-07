# 线上字体收录与版权政策

本仓库通过 **公开 Git 与 jsDelivr** 分发 Web 字体（WOFF2），等同于向互联网公开提供文件副本。仅允许将 **已确认可嵌入网页或再分发** 的字体纳入 `sources/` 与构建产物 `dist/web/`。

## 收录原则

1. **白名单制**：`meta/whitelist.json` 中已登记家族，除 **`skipBuild: true`**（当前为 **仅含 `.fon` 位图、无法生成 WOFF2** 的少数项）外，均已 **`licenseId: project-approved`** 并参与 `build_web_fonts.py` 打包。若授权结论变化，须将对应项改回 **跳过** 或移出发布 tag。
2. **每家族建议**：`sources/<家族Id>/` 可补充 `LICENSE.txt` 或名称表版权信息，便于对外说明与审计。
3. **禁止**：在明知无权 Web 嵌字的情况下仍对公众提供对应 `dist` 内容；授权变化时须同步回退白名单与构建物。
4. **变更流程**：新增家族须由设计/法务确认后，再更新 `whitelist.json`、补充 LICENSE，并打新版本 tag。
5. **目录与体积**：`sources/<家族>/fonts/` 中仅放该家族源字体文件，**每目录文件数不多于 8 个**；`dist/web/<家族Id>/files/` 中仅放 WOFF2，**每目录同样不多于 8 个**；`index.css` 位于上一级的 `dist/web/<家族Id>/`，与 `files` 子目录通过相对 URL 引用。

## 当前白名单摘要

| 家族 ID | 许可证 | 说明 |
|---------|--------|------|
| `source-han-sans-cn` | SIL Open Font License 1.1 | Adobe + Google 思源黑体（简体） |
| `source-han-serif-cn` | SIL Open Font License 1.1 | 思源宋体（简体） |
| `source-code-pro` | SIL Open Font License 1.1 | Adobe 开源等宽体 |
| `harmonyos-sans-sc` | 华为字体软件许可协议 | 仅收录 HarmonyOS Sans **简体中文版（SC）** 子集文件，完整条款以华为官方为准 |

若需扩展 HarmonyOS 其他字重或地域变体，须在确认许可范围后单独增加家族 ID 与目录，并控制单目录文件数不超过 8 个。
