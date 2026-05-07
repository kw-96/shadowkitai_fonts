"""
根目录字体扫描、按名称表族名聚类、分桶（每目录 ≤8 个）辅助函数。
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from fontTools.ttLib import TTFont

_MAX_PER_DIR = 8
# 保留已有白名单家族 id，合并时原样写回
PRESERVED_ORDER: tuple[str, ...] = (
    "source-han-sans-cn",
    "source-han-serif-cn",
    "source-code-pro",
    "harmonyos-sans-sc",
)
_FONT_SUFFIX = {".ttf", ".otf", ".ttc", ".TTF", ".OTF", ".TTC", ".fon", ".FON"}


def list_root_font_files(repo_root: Path) -> list[Path]:
    """列出仓库根目录下字体文件（不含子目录）。"""
    out: list[Path] = []
    for p in repo_root.iterdir():
        if not p.is_file():
            continue
        su = p.suffix
        if su in _FONT_SUFFIX or su.lower() in (".ttf", ".otf", ".ttc", ".fon"):
            out.append(p)
    return sorted(out, key=lambda x: x.name.lower())


def read_family_display_name(path: Path) -> str:
    """
    从 name 表读取族名字符串；失败时退回无扩展名文件名。
    TTC 取第一子字体。
    """
    try:
        if path.suffix.lower() == ".ttc":
            ttf = TTFont(str(path), fontNumber=0)
        else:
            ttf = TTFont(str(path))
        table = ttf["name"]
        for nid in (1, 4, 6, 0):
            for rec in table.names:
                if rec.nameID == nid:
                    try:
                        return str(rec)
                    except Exception:
                        continue
    except Exception:
        pass
    return path.stem


def _norm_key(name: str) -> str:
    t = re.sub(r"\s+", " ", name.strip().lower())
    t = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", t)
    return t.strip() or "unknown"


def _slug(base: str, used: set[str], hint: str = "") -> str:
    s = re.sub(r"[^a-z0-9-]+", "-", base.lower())
    s = re.sub(r"-+", "-", s).strip("-")[:40] or "fn"
    if hint:
        s = f"{s}-{hint[:8]}"
    cand = s
    n = 0
    while cand in used:
        n += 1
        cand = f"{s}-n{n}"
    used.add(cand)
    return cand


def cluster_by_family(
    paths: list[Path], used_ids: set[str]
) -> list[tuple[dict, list[Path]]]:
    """
    按各文件族名聚类，每簇按文件名排序后每最多 8 个拆为一条 sources 记录。
    @returns 列表: (family_entry, 该桶内文件路径)
    """
    groups: dict[str, list[Path]] = {}
    for j, p in enumerate(paths):
        if j and j % 100 == 0:
            print(f"  名称表 {j}/{len(paths)}", flush=True)
        fam = read_family_display_name(p)
        k = _norm_key(fam)
        groups.setdefault(k, []).append(p)

    out: list[tuple[dict, list[Path]]] = []
    for _k, plist in sorted(groups.items(), key=lambda x: (x[0] or "")):
        plist = sorted(plist, key=lambda x: x.name.lower())
        display = read_family_display_name(plist[0])
        base_slug = re.sub(r"[^a-z0-9]+", "-", _norm_key(display)[:48])
        base_slug = re.sub(r"-+", "-", base_slug).strip("-") or "unknown"
        part_idx = 0
        for i in range(0, len(plist), _MAX_PER_DIR):
            part_idx += 1
            chunk = plist[i : i + _MAX_PER_DIR]
            if len(plist) <= _MAX_PER_DIR:
                id_base = f"root-{base_slug[:40]}"
            else:
                id_base = f"root-{base_slug[:36]}-p{part_idx}"
            fid = _slug(id_base, used_ids, "")
            subdir = f"{fid}/fonts"
            script = "none"
            dlow = display.lower()
            if any(
                k in dlow
                for k in (
                    "han",
                    "cjk",
                    "sc",
                    "tc",
                    "jp",
                    "kr",
                    "noto",
                    "hei",
                    "song",
                    "ming",
                )
            ) or re.search(r"[\u4e00-\u9fff]", display):
                script = "cjk"
            note = "自根目录按名称表族名归组"
            if len(plist) > _MAX_PER_DIR:
                note = f"自根目录按名称表族名归组（分桶 {part_idx}）"
            out.append(
                (
                    {
                        "id": fid,
                        "displayName": display,
                        "licenseId": "pending-review",
                        "sourceSubdir": subdir,
                        "cssName": display,
                        "script": script,
                        "skipBuild": True,
                        "note": note,
                    },
                    chunk,
                )
            )
    return out


def move_chunk(sources: Path, chunk: list[Path], subdir: str) -> None:
    """将根目录文件移入 sources/<subdir>/（如 source-han-sans-cn/fonts）。"""
    target_dir = sources / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    for p in chunk:
        dest = target_dir / p.name
        if dest.exists():
            continue
        shutil.move(str(p), str(dest))


