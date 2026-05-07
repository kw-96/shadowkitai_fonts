# shadowkitai_fonts 主项目集成指南

本字体库通过 jsDelivr CDN 按版本分发 WOFF2 字体与分家族 CSS，主项目只需在需要的页面按需加载对应家族的样式表即可。

## 当前版本

| 项目 | 值 |
|------|------|
| Tag | `v0.2.0` |
| CDN 基址 | `https://cdn.jsdelivr.net/gh/Finjix/shadowkitai_fonts@v0.2.0/dist/web` |
| Manifest | `https://cdn.jsdelivr.net/gh/Finjix/shadowkitai_fonts@v0.2.0/meta/manifest.json` |

## 可用字体家族

| 家族 ID | font-family 名称 | 字重 | 说明 |
|---------|------------------|------|------|
| `source-han-sans-cn` | `'Source Han Sans CN'` | 200, 300, 350, 400, 500, 700, 900, 100‑900(VF) | 思源黑体 简体 |
| `source-han-serif-cn` | `'Source Han Serif CN'` | 200, 300, 400, 500, 600, 700, 900 | 思源宋体 简体 |
| `source-code-pro` | `'Source Code Pro'` | 200, 300, 400, 500, 600, 700, 900 | 等宽西文字体 |
| `harmonyos-sans-sc` | `'HarmonyOS Sans SC'` | 100, 300, 400, 500, 700, 900 | HarmonyOS Sans 简体 |
| `root-misans-p1` + `root-misans-p2` | `'MiSans'` | 200, 300, 350, 400, 500, 600, 700, 900 | 小米 MiSans 中文（需加载两个桶） |
| `root-misans-latin-p1` + `root-misans-latin-p2` | `'MiSans Latin'` | 200, 300, 350, 400, 500, 600, 700, 900 | 小米 MiSans 拉丁（需加载两个桶） |

## 快速开始

### 1. 复制加载工具函数

将 [`shadowkitaiFontLoader.example.ts`](shadowkitaiFontLoader.example.ts) 中的函数复制到主项目，核心代码：

```ts
const CDN_BASE = 'https://cdn.jsdelivr.net/gh/Finjix/shadowkitai_fonts@v0.2.0/dist/web';

function getFamilyStylesheetUrl(familyId: string): string {
  return `${CDN_BASE}/${familyId}/index.css`;
}

function loadFontFamilyStylesheet(familyId: string): void {
  const id = `shadowkitai-font-${familyId}`;
  if (document.getElementById(id)) return; // 避免重复加载

  const link = document.createElement('link');
  link.id = id;
  link.rel = 'stylesheet';
  link.href = getFamilyStylesheetUrl(familyId);
  document.head.appendChild(link);
}
```

### 2. 在需要的页面按需加载

**不要**在根 layout 中一次性引入全部家族，只在用到该字体的页面加载：

```ts
// 例如某篇文章页需要思源宋体
loadFontFamilyStylesheet('source-han-serif-cn');

// MiSans 中文需加载 p1 + p2 两个桶以获得全部字重
loadFontFamilyStylesheet('root-misans-p1');
loadFontFamilyStylesheet('root-misans-p2');
```

### 3. 在 CSS 中使用字体

`font-family` 名称必须与 `index.css` 中声明的一致：

```css
.sans-cn {
  font-family: 'Source Han Sans CN', sans-serif;
}

.serif-article {
  font-family: 'Source Han Serif CN', serif;
}

.code-block {
  font-family: 'Source Code Pro', monospace;
}

.sans-body {
  font-family: 'HarmonyOS Sans SC', sans-serif;
}

.misans {
  font-family: 'MiSans', sans-serif;
}
```

也可结合字重使用：

```css
.title {
  font-family: 'Source Han Serif CN', serif;
  font-weight: 700; /* Bold */
}

.caption {
  font-family: 'Source Han Serif CN', serif;
  font-weight: 300; /* Light */
}
```

## 集成方式

### Vue

```vue
<script setup>
import { loadFontFamilyStylesheet } from '@/utils/fontLoader';

onMounted(() => {
  loadFontFamilyStylesheet('source-han-serif-cn');
});
</script>
```

### 纯 HTML

```html
<!-- 在 <head> 中按需引入 -->
<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/gh/Finjix/shadowkitai_fonts@v0.2.0/dist/web/source-han-serif-cn/index.css" />
```

## 版本更新

1. 字体库发布新版本时打新 tag（如 `v0.3.0`）。
2. 主项目中将 `CDN_BASE` 中的 `@v0.2.0` 替换为 `@v0.3.0`。
3. **生产环境必须固定 tag**，不要使用分支名（如 `@main`），因为分支是可移动的，可能导致线上字体加载失败。