"""
根据文件名推断 @font-face 的 font-weight / 是否为可变字体。
"""

from __future__ import annotations

import re


def infer_face(stem: str, family_id: str) -> tuple[str, str, str | None]:
    """
    @param stem 无扩展名的文件名（小写）
    @param family_id 白名单家族 id
    @returns (css_weight_or_range, font_style, format_hint) format_hint 为 variable 时生成区间字重
    """
    s = stem.lower()
    if "vf" in s or "variable" in s:
        return "100 900", "normal", "variable"

    if family_id == "harmonyos-sans-sc":
        if "thin" in s:
            return "100", "normal", None
        if "light" in s:
            return "300", "normal", None
        if "regular" in s:
            return "400", "normal", None
        if "medium" in s:
            return "500", "normal", None
        if "black" in s:
            return "900", "normal", None
        if "bold" in s:
            return "700", "normal", None

    if family_id == "source-code-pro":
        if "extralight" in s:
            return "200", "normal", None
        if "light" in s:
            return "300", "normal", None
        if "regular" in s:
            return "400", "normal", None
        if "medium" in s:
            return "500", "normal", None
        if "semibold" in s:
            return "600", "normal", None
        if "black" in s:
            return "900", "normal", None
        if "bold" in s:
            return "700", "normal", None

    # 思源黑体 / 宋体 简体
    if "extralight" in s:
        return "200", "normal", None
    if "light" in s:
        return "300", "normal", None
    if "normal" in s and "sans" in s:
        return "350", "normal", None
    if "regular" in s:
        return "400", "normal", None
    if "medium" in s:
        return "500", "normal", None
    if "semibold" in s:
        return "600", "normal", None
    if "heavy" in s or "black" in s:
        return "900", "normal", None
    if "bold" in s:
        return "700", "normal", None

    m = re.search(r"-(\d+)$", s)
    if m:
        return m.group(1), "normal", None
    return "400", "normal", None


def css_family_name(family_id: str) -> str:
    """供 font-family 使用的展示名（与 CSS 文件内一致）。"""
    mapping = {
        "source-han-sans-cn": "Source Han Sans CN",
        "source-han-serif-cn": "Source Han Serif CN",
        "source-code-pro": "Source Code Pro",
        "harmonyos-sans-sc": "HarmonyOS Sans SC",
    }
    return mapping.get(family_id, family_id)
