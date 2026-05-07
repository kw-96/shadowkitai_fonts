/**
 * 本文件为 shadowkitai 主仓库集成示例：按家族从 jsDelivr 拉取分家族 CSS，实现选择性加载。
 * 将所需函数复制到主项目后，把 CDN 基址与 tag 与发布流程对齐即可。
 */

export interface IFontFamilyManifestEntry {
  id: string;
  displayName: string;
  licenseId: string;
  stylesheet: string;
  weights: Array<{
    sourceFile: string;
    woff2: string;
    fontWeight: string;
    fontStyle: string;
    variable: boolean;
  }>;
}

export interface IFontsManifest {
  version: number;
  generatedAt?: string;
  cdnBase?: string;
  families: IFontFamilyManifestEntry[];
}

/**
 * 生成分家族样式表在 CDN 上的绝对 URL
 * @param cdnBase 不含尾斜杠，如 https://cdn.jsdelivr.net/gh/ORG/shadowkitai_fonts@v0.1.0/dist/web
 * @param familyId 与 manifest 中 id 相同
 * @returns 可赋给 link.href 的地址
 */
export function getFamilyStylesheetUrl(cdnBase: string, familyId: string): string {
  const base = cdnBase.replace(/\/+$/, "");
  return `${base}/${familyId}/index.css`;
}

/**
 * 在页面中按需注入 link[rel=stylesheet]，避免在 layout 中全量引入
 * @param cdnBase CDN 根路径（同 tag 的 dist/web 根）
 * @param familyId 家族 id
 * @param doc 可选，默认 document（便于测试）
 */
export function loadFontFamilyStylesheet(
  cdnBase: string,
  familyId: string,
  doc: Document = typeof document !== "undefined" ? document : (null as unknown as Document)
): void {
  if (!doc) return;
  const id = `shadowkitai-font-${familyId}`;
  if (doc.getElementById(id)) {
    return;
  }
  const link = doc.createElement("link");
  link.id = id;
  link.rel = "stylesheet";
  link.href = getFamilyStylesheetUrl(cdnBase, familyId);
  doc.head.appendChild(link);
}

/**
 * 从 manifest 地址拉取清单元数据（可用于路由级预加载前校验 id）
 * @param manifestUrl 完整 URL，如 .../meta/manifest.json
 */
export async function fetchManifest(
  manifestUrl: string
): Promise<IFontsManifest> {
  const res = await fetch(manifestUrl, { cache: "force-cache" });
  if (!res.ok) {
    throw new Error("无法拉取字库清单");
  }
  return res.json() as Promise<IFontsManifest>;
}
