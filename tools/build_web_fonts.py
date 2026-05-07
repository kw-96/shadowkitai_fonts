#!/usr/bin/env python3
"""
从 meta/whitelist.json 读取白名单，将 sources 下字体转为 dist/web/<familyId>/*.woff2，
并生成分家族 index.css 与 meta/manifest.json（供 jsDelivr 与 shadowkitai 按需加载）。
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from fontTools.ttLib import TTFont

from font_weight_rules import css_family_name, infer_face


def _css_string(value: str) -> str:
    """将字体族名写进 CSS font-family 时的引号转义。"""
    if '"' in value and "'" in value:
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if "'" in value:
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return "'" + value + "'"


def _use_cjk_range(fam: dict) -> bool:
    s = fam.get("script")
    if s == "cjk":
        return True
    if s == "none":
        return False
    fid = fam.get("id", "")
    if fid in ("source-han-sans-cn", "source-han-serif-cn", "harmonyos-sans-sc"):
        return True
    if fid == "source-code-pro":
        return False
    return False


def _css_family(fam: dict) -> str:
    fid = fam.get("id", "")
    if fam.get("cssName"):
        return fam["cssName"]
    return css_family_name(fid)

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCES = REPO_ROOT / "sources"
META = REPO_ROOT / "meta"
DIST_WEB = REPO_ROOT / "dist" / "web"


def load_whitelist() -> dict:
    data = json.loads((META / "whitelist.json").read_text(encoding="utf-8"))
    if "families" not in data:
        raise SystemExit("whitelist.json 缺少 families")
    return data


def to_woff2(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    print(f"  encode: {src.name} -> {dst.name}", flush=True)
    font = TTFont(str(src))
    font.flavor = "woff2"
    font.save(str(dst))


def collect_sources(family: dict) -> list[Path]:
    rel = family["sourceSubdir"]
    d = SOURCES / rel
    if not d.is_dir():
        raise SystemExit(f"源目录不存在: {d}")
    files = sorted([p for p in d.iterdir() if p.suffix.lower() in (".otf", ".ttf", ".ttc")])
    if not files:
        raise SystemExit(f"目录内无字体文件: {d}")
    return files


def build_family(family: dict) -> dict:
    fid = family["id"]
    out_dir = DIST_WEB / fid
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    print(f"family: {fid}", flush=True)

    css_name = _css_string(_css_family(family))
    css_blocks: list[str] = []
    weight_rows: list[dict] = []

    file_dir = out_dir / "files"
    for src in collect_sources(family):
        woff2_name = f"{src.stem}.woff2"
        dst = file_dir / woff2_name
        to_woff2(src, dst)
        weight, style, hint = infer_face(src.stem, fid)
        url = f"files/{woff2_name}"
        range_line = ""
        if _use_cjk_range(family):
            range_line = (
                "  unicode-range: U+4E00-9FFF, U+3400-4DBF, U+20000-2A6DF, "
                "U+3000-303F, U+FF00-FFEF;\n"
            )
        if hint == "variable":
            block = (
                f"@font-face {{\n  font-family: {css_name};\n  src: url('{url}') "
                f"format('woff2-variations');\n  font-weight: {weight};\n  font-style: {style};\n"
                f"  font-display: swap;\n}}"
            )
        else:
            block = (
                f"@font-face {{\n  font-family: {css_name};\n  src: url('{url}') format('woff2');\n"
                f"  font-weight: {weight};\n  font-style: {style};\n  font-display: swap;\n"
                f"{range_line}}}"
            )
        css_blocks.append(block)
        weight_rows.append(
            {
                "sourceFile": src.name,
                "woff2": f"files/{woff2_name}",
                "fontWeight": weight,
                "fontStyle": style,
                "variable": hint == "variable",
            }
        )

    (out_dir / "index.css").write_text("\n\n".join(css_blocks) + "\n", encoding="utf-8")
    return {
        "id": fid,
        "displayName": family.get("displayName", fid),
        "licenseId": family.get("licenseId", ""),
        "stylesheet": f"{fid}/index.css",
        "weights": weight_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="构建 WOFF2 与 CDN 用 CSS / manifest")
    parser.add_argument(
        "--cdn-base",
        default="",
        help="可选。不含尾斜杠，写入 manifest；CSS 内使用相对路径，可不填。示例：https://cdn.jsdelivr.net/gh/ORG/shadowkitai_fonts@v0.1.0/dist/web",
    )
    parser.add_argument(
        "--only",
        nargs="*",
        default=None,
        help="仅构建指定家族 id，空格分隔；省略则构建全部",
    )
    args = parser.parse_args()

    data = load_whitelist()
    manifest_families: list[dict] = []
    for fam in data["families"]:
        if fam.get("skipBuild"):
            continue
        if args.only is not None and fam["id"] not in args.only:
            continue
        manifest_families.append(build_family(fam))

    manifest: dict = {
        "version": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "families": manifest_families,
    }
    base = args.cdn_base.strip().rstrip("/")
    if base:
        manifest["cdnBase"] = base
    (META / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"done: {DIST_WEB}, {META / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
