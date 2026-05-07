#!/usr/bin/env python3
"""
将仓库根目录下字体按名称表族名聚类后移入 sources/，并合并写入 meta/whitelist.json。
新家族默认 skipBuild: true；人工确认授权后可对单条改为 false 再执行构建。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from organize_lib import PRESERVED_ORDER, cluster_by_family, list_root_font_files, move_chunk

REPO_ROOT = Path(__file__).resolve().parents[1]
META = REPO_ROOT / "meta"
WHITELIST = META / "whitelist.json"


def _script_for_preserved(fid: str) -> str:
    if fid == "source-code-pro":
        return "none"
    if fid in ("source-han-sans-cn", "source-han-serif-cn", "harmonyos-sans-sc"):
        return "cjk"
    return "none"


def _normalize_entry(f: dict) -> dict:
    o = dict(f)
    fid = o.get("id", "")
    o.setdefault("script", _script_for_preserved(fid))
    if str(fid).startswith("root-"):
        o.setdefault("cssName", o.get("displayName", fid))
        o.setdefault("skipBuild", True)
    else:
        o.setdefault("skipBuild", False)
    return o


def _sort_families(items: list[dict]) -> list[dict]:
    def key(f: dict) -> tuple:
        i = f.get("id", "")
        if i in PRESERVED_ORDER:
            return (0, PRESERVED_ORDER.index(i))
        if not str(i).startswith("root-"):
            return (1, i)
        return (2, i)

    return sorted((_normalize_entry(f) for f in items), key=key)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="只聚类并打印前若干条，不移动、不写回")
    args = parser.parse_args()

    data = json.loads(WHITELIST.read_text(encoding="utf-8"))
    old_families = list(data.get("families", []))
    used_ids: set[str] = {f.get("id", "") for f in old_families if f.get("id")}

    root_fonts = list_root_font_files(REPO_ROOT)
    if not root_fonts:
        print("根目录无待整理字体")
        out = {
            "version": max(2, int(data.get("version", 1))),
            "families": _sort_families(old_families),
        }
        if not args.dry_run:
            WHITELIST.write_text(
                json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        return 0

    print(f"根目录 {len(root_fonts)} 个文件，聚类中…", flush=True)
    clusters = cluster_by_family(root_fonts, used_ids)
    print(f"将生成 {len(clusters)} 个白名单条目", flush=True)

    if args.dry_run:
        for row, chunk in clusters[:15]:
            print(row["id"], row["sourceSubdir"], len(chunk))
        if len(clusters) > 15:
            print("…")
        return 0

    n_moved = 0
    for row, chunk in clusters:
        move_chunk(REPO_ROOT / "sources", chunk, row["sourceSubdir"])
        n_moved += len(chunk)

    new_by_id = {r["id"]: r for r, _ in clusters}
    merged_by_id = {f["id"]: f for f in old_families if f.get("id")}
    merged_by_id.update(new_by_id)
    final = _sort_families(list(merged_by_id.values()))

    out = {"version": 2, "families": final}
    WHITELIST.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"完成: 移动 {n_moved} 个文件，白名单共 {len(final)} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
