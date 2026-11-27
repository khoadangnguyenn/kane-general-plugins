#!/usr/bin/env python3
"""Chọn gói plugin kane cho từng dự án. Dùng: chon_tang.py goi-y|ghi|hien|tinh <thư mục> [gói,... | id lựa chọn,...].

Danh mục gói (plugin, dấu hiệu dự án, token, từ khoá) nằm hết trong goi_tang.json; thêm plugin con = thêm dòng ở đó.
Cơ chế: Claude Code đọc `enabledPlugins` trong <dự án>/.claude/settings.local.json (cá nhân, không commit), khoá này
thắng cài đặt người dùng; đổi có hiệu lực sau `/reload-plugins` hoặc khi mở phiên mới. Chỉ đụng plugin ĐÃ CÀI; gói "giu" không bị đổi.
Đường dẫn ~/.claude đổi được bằng KANE_CLAUDE_HOME, danh mục bằng KANE_GOI_TANG (để test)."""
import fnmatch
import json
import os
import sys
from pathlib import Path

CFG = json.loads(Path(os.environ.get("KANE_GOI_TANG") or Path(__file__).with_name("goi_tang.json")).read_text("utf-8"))
GOI = CFG["goi"]
CA_NHAN = next((p for g in GOI if g.get("giu") for p in g["plugin"]), None)  # plugin của gói `giu` (nếu danh mục có)
SKIP = {"node_modules", ".git", ".venv", "venv", "__pycache__"}


def claude_home():
    return Path(os.environ.get("KANE_CLAUDE_HOME") or Path.home() / ".claude")


def doc_json(p):
    try:
        d = json.loads(Path(p).read_text("utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def ten_plugin_biet():
    return set(CFG["plugins"]) | {p for g in GOI for p in g["plugin"]}


def da_cai(thu_muc):
    """{plugin: 'plugin@marketplace'} cho plugin trong danh mục đã cài ở mức người dùng hoặc dự án này."""
    ra, biet = {}, ten_plugin_biet()
    for key, ban in doc_json(claude_home() / "plugins" / "installed_plugins.json").get("plugins", {}).items():
        name, _, mkt = key.partition("@")
        if name not in biet or mkt not in CFG["marketplace"]:
            continue
        for b in ban if isinstance(ban, list) else []:
            pp = b.get("projectPath")
            if b.get("scope") == "user" or (pp and str(thu_muc).startswith(pp)):
                ra[name] = key
    return ra


def bao_ham(plugins):
    ra, moi = set(), list(plugins)
    while moi:
        p = moi.pop()
        if p not in ra:
            ra.add(p)
            moi += CFG["plugins"].get(p, {}).get("phu_thuoc", [])
    return ra


def goi_co_san(cai):
    return [g for g in GOI if bao_ham(g["plugin"]) <= set(cai)]


def ep_gop(thu_muc):
    """enabledPlugins đã gộp: người dùng < dự án < local, từng khoá một như Claude Code."""
    gop = {}
    for f in (claude_home() / "settings.json", thu_muc / ".claude" / "settings.json", thu_muc / ".claude" / "settings.local.json"):
        ep = doc_json(f).get("enabledPlugins")
        gop.update(ep if isinstance(ep, dict) else {})
    return gop


def plugin_bat(thu_muc, cai):
    """Plugin đã cài và đang bật."""
    gop = ep_gop(thu_muc)
    return [p for p in cai if gop.get(cai[p]) is True]


def hien_thi(plugins, giu=False):
    """Tên ngắn các gói có đủ plugin: `core › <tầng>(<gói việc>)`. Tầng lồng nhau (`bac`) nối bằng ›; gói việc ghi trong ngoặc sau tầng có `chua_viec`; gói `giu` nối cuối bằng +. Không có tầng chứa việc thì gói việc nối bằng +."""
    ps = set(plugins)
    co = [g for g in GOI if set(g["plugin"]) <= ps]
    ten = lambda g: g.get("ten_ngan") or g["ten"]
    viec = [ten(g) for g in co if not g.get("bac") and not g.get("giu")]
    cuoi = [ten(g) for g in co if g.get("giu")] if giu else []
    bac_g = [g for g in co if g.get("bac")]
    bac = [ten(g) for g in bac_g]
    chu = next((i for i, g in enumerate(bac_g) if g.get("chua_viec")), None)
    if chu is not None and viec:
        bac[chu] += "(" + ", ".join(viec) + ")"
        viec = []
    return " + ".join(x for x in [" › ".join(bac), *viec, *cuoi] if x)


def tokens(plugins):
    ps = set(plugins)
    return CFG["co_so"] + sum(g["token"] for g in GOI if not g.get("giu") and set(g["plugin"]) <= ps)


def dau_hieu(d, mau):
    """Các tên khớp mẫu trong thư mục (2 cấp). Mẫu '/x' chỉ cấp 1; mẫu có '/' ở giữa là đường dẫn cụ thể;
    mẫu 'a+b' chỉ tính khi tên b nằm cùng thư mục với tên khớp a (vd 'hooks.py+modules.txt')."""
    ten = {}  # tên thường → (đường dẫn tương đối, ở cấp 1)
    rels = set()
    try:
        top = list(os.scandir(d))[:300]
    except OSError:
        return []
    for e in top:
        ten.setdefault(e.name.lower(), (e.name, True))
        rels.add(e.name.lower())
        if e.is_dir(follow_symlinks=False) and not e.name.startswith(".") and e.name not in SKIP:
            try:
                for c in list(os.scandir(e.path))[:200]:
                    ten.setdefault(c.name.lower(), (f"{e.name}/{c.name}", False))
                    rels.add(f"{e.name}/{c.name}".lower())
            except OSError:
                pass
    ra = []
    for m in mau:
        if "/" in m.strip("/") and (Path(d) / m).exists():
            ra.append(m)
            continue
        dau, *kem = m.lower().split("+")
        ml = dau.lstrip("/")
        gan = lambda rel: all(f"{rel.rpartition('/')[0]}/{k}".lstrip("/") in rels for k in kem)
        ra += sorted(rel for k, (rel, c1) in ten.items() if fnmatch.fnmatchcase(k, ml) and (c1 or not m.startswith("/")) and gan(rel.lower()))
    return list(dict.fromkeys(ra))


def chia(opts, toi_da=4):
    """Chia đều thành các nhóm 2–4 lựa chọn (5 → 3 + 2), vì mỗi câu AskUserQuestion tối đa 4 lựa chọn."""
    k = -(-len(opts) // toi_da)
    out, i = [], 0
    for n in range(k):
        m = len(opts) // k + (n < len(opts) % k)
        out.append(opts[i:i + m])
        i += m
    return out


def lan_truoc(thu_muc, co):
    """Mã gói đã bật lần trước trong settings.local.json của dự án (None nếu chưa từng chọn)."""
    ep = doc_json(thu_muc / ".claude" / "settings.local.json").get("enabledPlugins")
    ten = {k.partition("@")[0] for k, v in ep.items() if v is True} if isinstance(ep, dict) else set()
    if "kane" not in ten:
        return None
    return [g["ma"] for g in co if not g.get("loi") and not g.get("giu") and set(g["plugin"]) <= ten]


def menu(thu_muc, cai, co, bc):
    """Câu hỏi nhiều bước cho AskUserQuestion (bảng `loai_viec` trong goi_tang.json). Chỉ gói đã cài; câu chỉ còn 1 lựa chọn bị bỏ và chọn luôn (`tu_dong`),
    riêng câu tuỳ chọn thêm lựa chọn "Không". Mỗi lựa chọn có `id` (đưa vào `tinh`), `ma` (mã gói) và dòng `→ bật: …`. Nhóm/gói có dấu hiệu dự án chỉ được đánh dấu (Recommended)."""
    lv = CFG.get("loai_viec")
    loi = [p for g in GOI if g.get("loi") for p in g["plugin"]]
    if not lv or not bao_ham(loi) <= set(cai):
        return {"cau_hoi": [], "tu_dong": []}
    co_ma, gm = {g["ma"]: g for g in co}, {g["ma"]: g for g in GOI}
    cau, tu_dong = [], []

    def opt(id, nhan, goi, sau="", bat=None, th=(), mo_ta=""):
        ps = bao_ham(loi + [p for m in goi for p in gm[m]["plugin"]])
        mo = f"→ bật: {bat or hien_thi(ps, giu='ca-nhan' in goi) + sau}" + (f" (≈{tokens(ps)} token mỗi lượt)" if not bat else "") + (f" · {mo_ta}" if mo_ta else "") + (f"; thấy {', '.join(th[:3])}" if th else "")
        return {"id": id, "label": nhan + (" (Recommended)" if th else ""), "description": mo, "ma": list(goi), "de_xuat": bool(th)}

    def buoc(id, text, header, nhieu, chi_khi, opts, tuy_chon=False):
        opts = sorted(opts, key=lambda o: not o["de_xuat"])
        if len(opts) == 1 and tuy_chon:
            opts.append({"id": f"{id}:khong", "label": "Không thêm", "description": "→ giữ nguyên", "ma": [], "de_xuat": False})
        if len(opts) == 1:
            tu_dong.append({"id": opts[0]["id"], "chi_khi": chi_khi, "ma": opts[0]["ma"]})
        for n, ph in enumerate(chia(opts) if len(opts) > 1 else []):
            k = len(chia(opts))
            cau.append({"id": id, "question": text, "header": header + (f" {n + 1}/{k}" if k > 1 else ""), "multiSelect": nhieu, "chi_khi": chi_khi, "options": ph})

    def th_cua(goi):
        return [x for m in goi for x in bc.get(m, [])]

    chon_duoc = [g for g in co if not g.get("loi") and not g.get("giu")]
    for st in lv:
        opts = []
        for e in st["muc"]:
            id = f"{st['buoc']}:{e['ma']}"
            if st["buoc"] == "nhom":
                con = {m for s2 in lv if s2.get("chi_khi") == f"nhom:{e['ma']}" for x in s2["muc"] for m in x["goi"] if m in co_ma}
                if e.get("tu_chon"):
                    if len(chon_duoc) >= 3:
                        opts.append(opt(id, e["nhan"], [], bat=e["bat"]))
                elif set(e["goi"]) <= set(co_ma):
                    opts.append(opt(id, e["nhan"], e["goi"], sau=e.get("sau", ""), th=th_cua(con)))
            elif set(e["goi"]) <= set(co_ma):
                opts.append(opt(id, e["nhan"], e["goi"], th=th_cua(e["goi"])))
        if st["buoc"] == "nhom":
            truoc = lan_truoc(thu_muc, co)
            if truoc is not None:
                o = opt("truoc", "Như lần trước", truoc)
                o.update(label="Như lần trước (Recommended)", de_xuat=True)
                opts.insert(0, o)
        buoc(st["buoc"], st["cau"], st["header"], st["nhieu"], st.get("chi_khi"), opts, st.get("tuy_chon", False))
    if any(o["id"] == "nhom:tu-chon" for q in cau for o in q["options"]):
        buoc("tu", "Chọn từng gói (tự kéo theo các gói bắt buộc của gói đã chọn)", "Gói", True, "nhom:tu-chon",
             [opt(f"tu:{g['ma']}", g.get("ten_ngan") or g["ten"], [g["ma"]], th=bc.get(g["ma"], []), mo_ta=g["mo_ta"]) for g in chon_duoc])
    if CA_NHAN and CA_NHAN in cai and CA_NHAN not in plugin_bat(thu_muc, cai):
        cau.append({"id": "ca-nhan", "question": "Bật gói cá nhân?", "header": "Cá nhân", "multiSelect": False, "chi_khi": None, "options": [
            {"id": "ca-nhan:khong", "label": "Không (mặc định)", "description": "→ giữ nguyên", "ma": [], "de_xuat": False},
            opt("ca-nhan:co", "Có, bật gói cá nhân", ["ca-nhan"])]})
    return {"cau_hoi": cau, "tu_dong": tu_dong}


def tinh(thu_muc, arg):
    """Tập gói từ các `id` lựa chọn đã trả lời (cách nhau dấu phẩy). `truoc` thắng mọi lựa chọn khác. Trả mã để đưa vào `ghi`."""
    cai = da_cai(thu_muc)
    co = goi_co_san(cai)
    m = menu(thu_muc, cai, co, {})
    opts = {o["id"]: o for q in m["cau_hoi"] for o in q["options"]}
    ids = [x.strip() for x in arg.split(",") if x.strip() and x.strip() != "gon"]
    sai = [x for x in ids if x not in opts]
    if sai:
        raise SystemExit("không có lựa chọn: " + ", ".join(sai))
    ma = [] if "truoc" not in ids else list(opts["truoc"]["ma"])
    if "truoc" not in ids:
        for x in ids:
            ma += opts[x]["ma"]
        for t in m["tu_dong"]:
            if not t["chi_khi"] or t["chi_khi"] in ids:
                ma += t["ma"]
    ma = list(dict.fromkeys(ma))
    gm = {g["ma"]: g for g in GOI}
    ps = bao_ham([p for g in GOI if g.get("loi") for p in g["plugin"]] + [p for x in ma for p in gm[x]["plugin"]])
    return {"goi": ma, "ghi": ",".join(ma) or "gon", "bat": hien_thi(ps, giu="ca-nhan" in ma), "tokens": tokens(ps)}


def goi_y(thu_muc):
    cai = da_cai(thu_muc)
    co = goi_co_san(cai)
    loi = [g for g in co if g.get("loi")]
    hien = [g for g in co if not g.get("loi") and not g.get("giu")]
    nen = set().union(*[bao_ham(g["plugin"]) for g in loi]) if loi else set()
    nang = tokens(nen.union(*[bao_ham(g["plugin"]) for g in hien])) if loi else 0
    ra, dh = [], {}
    for g in hien:
        bc = dh[g["ma"]] = dau_hieu(thu_muc, g.get("dau_hieu", []))
        ps = nen | bao_ham(g["plugin"])
        ra.append({"ma": g["ma"], "ten": g["ten"], "mo_ta": g["mo_ta"], "plugin": sorted(ps - nen), "tokens": tokens(ps),
                   "tiet_kiem": nang - tokens(ps), "de_xuat": bool(bc),
                   "ly_do": f"thấy {', '.join(bc[:3])}" if bc else ""})
    ra.sort(key=lambda g: not g["de_xuat"])
    mn = menu(thu_muc, cai, co, dh)
    return {"thu_muc": str(thu_muc), "da_cai": sorted(cai), "plugin_bat": plugin_bat(thu_muc, cai),
            "loi": {"ma": [g["ma"] for g in loi], "tokens": tokens(nen)} if loi else None,
            "de_xuat": [g["ma"] for g in ra if g["de_xuat"]], "goi": ra, "cau_hoi": mn["cau_hoi"], "tu_dong": mn["tu_dong"],
            "tokens_giu": sum(g["token"] for g in co if g.get("giu")),
            "do_ngay": CFG["do_ngay"], "nguon_so": CFG.get("nguon", "")}


def ghi(thu_muc, arg):
    cai = da_cai(thu_muc)
    co = {g["ma"]: g for g in goi_co_san(cai) if not g.get("giu")}
    chon, ca_nhan = set(), False
    for x in (s.strip() for s in arg.split(",") if s.strip()):
        if x == "gon":
            continue
        if x == "ca-nhan" and CA_NHAN in cai:
            ca_nhan = True
            continue
        if x == "tat-ca":
            chon.update(p for g in co.values() for p in g["plugin"])
        elif x in co:
            chon.update(co[x]["plugin"])
        elif x in ten_plugin_biet() and x not in {p for g in GOI if g.get("giu") for p in g["plugin"]}:
            chon.add(x)
        else:
            raise SystemExit(f"không có gói hoặc plugin đã cài: {x}")
    chon = bao_ham(chon | {p for g in GOI if g.get("loi") for p in g["plugin"]})
    thieu = sorted(chon - set(cai))
    if thieu:
        raise SystemExit("chỉ ghi được plugin đã cài, thiếu: " + ", ".join(thieu))
    f = thu_muc / ".claude" / "settings.local.json"
    cu = {}
    if f.exists():
        try:
            cu = json.loads(f.read_text("utf-8"))
        except ValueError:
            raise SystemExit(f"{f} không phải JSON hợp lệ: không ghi đè")
        if not isinstance(cu, dict) or not isinstance(cu.get("enabledPlugins", {}), dict):
            raise SystemExit(f"{f} có enabledPlugins không phải object: không ghi đè")
    giu = {p for g in GOI if g.get("giu") for p in g["plugin"]}
    quan_ly = {p for g in GOI if not g.get("giu") for p in g["plugin"]} - giu
    ep = cu.setdefault("enabledPlugins", {})
    for p in quan_ly & set(cai):
        ep[cai[p]] = p in chon
    if ca_nhan:
        ep[cai[CA_NHAN]] = True
        chon.add(CA_NHAN)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(cu, ensure_ascii=False, indent=2) + "\n", "utf-8")
    return {"da_ghi": str(f), "bat": sorted(chon), "tat": sorted((quan_ly & set(cai)) - chon), "tokens": tokens(chon),
            "ghi_chu": "gõ /reload-plugins một lần để áp dụng ngay (hoặc mở phiên mới)"}


def main(argv):
    if len(argv) < 3 or argv[1] not in ("goi-y", "ghi", "hien", "tinh") or (argv[1] in ("ghi", "tinh") and len(argv) < 4):
        raise SystemExit(__doc__)
    d = Path(argv[2]).resolve()
    if not d.is_dir():
        raise SystemExit(f"không có thư mục {d}")
    if argv[1] == "goi-y":
        r = goi_y(d)
    elif argv[1] == "ghi":
        r = ghi(d, argv[3])
    elif argv[1] == "tinh":
        r = tinh(d, argv[3])
    else:
        r = {"plugin_bat": plugin_bat(d, da_cai(d))}
    print(json.dumps(r, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main(sys.argv)
    except SystemExit as e:
        if e.code and not isinstance(e.code, int):
            print(e.code, file=sys.stderr)
            sys.exit(2)
        raise
