#!/usr/bin/env python3
"""Đoạn status line cho gói kane: `core › <tầng>(<gói việc>)`, thêm ` ↻ /reload-plugins` khi tập plugin đang cấu hình khác tập lúc mở phiên.
Dùng: echo '<JSON status line>' | thanh_trang_thai.py, hoặc `from thanh_trang_thai import doan`. Im lặng (in rỗng) khi thư mục không phải dự án kane.
Tập lúc mở phiên do hook SessionStart (probe.js) ghi vào $KANE_CACHE_DIR|~/.cache/kane/phien/<session_id>.json.
Nguồn trường: code.claude.com/docs/en/statusline (workspace.project_dir, workspace.current_dir, cwd, session_id)."""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chon_tang import doc_json, ep_gop, hien_thi  # noqa: E402


def la_kane(ten):
    return ten == "kane" or ten.startswith("kane-")


def goc_du_an(d):
    return next((p for p in (d, *d.parents) if (p / ".ai" / "STATE.md").exists()), None)


def doan(ev):
    ws = ev.get("workspace") if isinstance(ev.get("workspace"), dict) else {}
    d = ws.get("project_dir") or ws.get("current_dir") or ev.get("cwd")
    if not d or not goc_du_an(Path(d)):
        return ""
    ten = {k.partition("@")[0] for k, v in ep_gop(Path(ws.get("project_dir") or d)).items() if v is True}
    ten = {t for t in ten if la_kane(t)}
    chuoi = hien_thi(ten, giu=True)
    if not chuoi:
        return ""
    sid = str(ev.get("session_id") or "")
    if re.fullmatch(r"[\w-]+", sid):
        cache = Path(os.environ.get("KANE_CACHE_DIR") or Path.home() / ".cache" / "kane")
        luc_mo = doc_json(cache / "phien" / f"{sid}.json").get("plugins")
        if isinstance(luc_mo, list) and set(luc_mo) != ten:
            chuoi += " ↻ /reload-plugins"
    return chuoi


def main():
    try:
        ev = json.load(sys.stdin)
        out = doan(ev if isinstance(ev, dict) else {})
    except Exception:
        out = ""
    if out:
        print(out)


if __name__ == "__main__":
    main()
