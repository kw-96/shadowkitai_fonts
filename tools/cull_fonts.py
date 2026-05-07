#!/usr/bin/env python3
"""
按 cull_rules 从 sources 删除目标外字体；空目录删族；回写 meta/whitelist.json。
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

from cull_rules import names_lower, should_remove

REPO = Path(__file__).resolve().parents[1]
SOURCES = REPO / "sources"
WL = REPO / "meta" / "whitelist.json"
EXT = {".ttf", ".otf", ".ttc"}


def _open(p: Path) -> TTFont:
    if p.suffix.lower() == ".ttc":
        return TTFont(str(p), fontNumber=0)
    return TTFont(str(p))


def _is_font_file(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() in (".ttf", ".otf", ".ttc", ".fon")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    cnt: dict[str, int] = {}
    dels: list[Path] = []

    for fonts_dir in sorted(SOURCES.rglob("fonts")):
        if not fonts_dir.is_dir():
            continue
        for p in sorted(fonts_dir.iterdir()):
            if not _is_font_file(p) or p.suffix.lower() == ".fon":
                continue
            try:
                f = _open(p)
            except Exception:
                continue
            try:
                nl = names_lower(f)
                rm, why = should_remove(p, f, p.stem, nl)
            finally:
                f.close()
            if rm:
                cnt[why] = cnt.get(why, 0) + 1
                dels.append(p)
            else:
                cnt["keep"] = cnt.get("keep", 0) + 1

    print("统计:", cnt, "将删文件数:", len(dels))
    if args.dry_run:
        return 0

    for p in dels:
        try:
            try:
                os.chmod(p, stat.S_IWRITE)
            except OSError:
                pass
            p.unlink()
        except OSError as e:
            print("unlink fail", p, e, file=sys.stderr)

    for fonts_dir in sorted(SOURCES.rglob("fonts"), reverse=True):
        if not fonts_dir.is_dir():
            continue
        rest = [x for x in fonts_dir.iterdir() if x.is_file()]
        if rest:
            continue
        par = fonts_dir.parent
        try:
            fonts_dir.rmdir()
            if par.is_dir() and not any(par.iterdir()):
                par.rmdir()
        except OSError:
            pass

    data = json.loads(WL.read_text(encoding="utf-8"))
    keep: list[dict] = []
    for fam in data.get("families", []):
        rel = fam.get("sourceSubdir", "")
        d = SOURCES / rel
        has = False
        if d.is_dir():
            for p in d.iterdir():
                if p.is_file() and p.suffix.lower() in (".ttf", ".otf", ".ttc", ".fon"):
                    has = True
                    break
        if has:
            keep.append(fam)
    data["families"] = keep
    WL.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("whitelist 剩余", len(keep), "条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
