---
name: sync
description: "Kiểm xem các bản sao chuẩn trong kane còn khớp bản gốc trên máy không: \"kane cũ chưa\", \"cập nhật kane\", \"đồng bộ lại file chuẩn\", hoặc sau khi sửa một file chuẩn gốc."
---

# kane:sync — đồng bộ bản sao với bản gốc

Quy ước (lấy từ Paper-Workflow `MANIFEST.md` §Cách dùng): **bản gốc thắng**. `MANIFEST.csv` ở gốc plugin ghi ba cột: `ban_trong_kane`, `ban_goc`, `sha256` (mã băm bản gốc lúc chép).

Plugin cài từ marketplace thư mục `kane-local`, Claude Code đọc thẳng thư mục repo kane (`claude plugin list` ghi "Read from: <thư mục repo kane>", kiểm 2026-11-26). Skill này chỉ dành cho người bảo trì: cần `MANIFEST.csv` ở gốc repo và các bản gốc trên máy tác giả. Sửa ở đó, mở phiên mới là có hiệu lực.

## Bước 1 — kiểm (chỉ đọc)
```bash
cd <thư mục repo kane> && python3 -I - <<'EOF'
import csv,hashlib,os
H=os.path.expanduser('~'); sh=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest()
doi=mat=0
for r in csv.DictReader(open('MANIFEST.csv')):
    g=r['ban_goc'].replace('~',H,1)
    if not os.path.exists(g): mat+=1; print('MẤT GỐC ',r['ban_trong_kane']); continue
    if sh(g)!=r['sha256']: doi+=1; print('GỐC ĐỔI ',r['ban_trong_kane'],'<-',r['ban_goc'])
print(f'gốc đổi: {doi} · mất gốc: {mat}')
EOF
```

## Bước 2 — chép lại (chỉ khi user đồng ý)
Báo user danh sách "GỐC ĐỔI" trước. Được đồng ý thì chạy:
```bash
cd <thư mục repo kane> && python3 -I - <<'EOF'
import csv,hashlib,os,shutil
H=os.path.expanduser('~'); sh=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest()
rows=list(csv.DictReader(open('MANIFEST.csv')))
for r in rows:
    g=r['ban_goc'].replace('~',H,1)
    if os.path.exists(g) and sh(g)!=r['sha256']:
        os.makedirs(os.path.dirname(r['ban_trong_kane']),exist_ok=True)
        shutil.copy2(g,r['ban_trong_kane']); r['sha256']=sh(g); print('đã chép',r['ban_trong_kane'])
w=csv.DictWriter(open('MANIFEST.csv','w',newline=''),fieldnames=['ban_trong_kane','ban_goc','sha256'])
w.writeheader(); w.writerows(rows)
EOF
```
Sau đó tăng `version` trong `.claude-plugin/plugin.json` rồi mở phiên mới.

## Giới hạn
- Script chỉ thấy file đã có trong `MANIFEST.csv`. File chuẩn MỚI ở bản gốc (ví dụ một chuẩn mới trong `Paper-Workflow/chuan/`) phải thêm tay: chép vào `references/…`, thêm một dòng vào `MANIFEST.csv`, và thêm vào bảng tham chiếu của skill liên quan.
- Ba file tổng hợp `TONG_HOP_LUAT_*.md` do agent viết ngày 2026-11-26, không có bản gốc. Khi bản gốc đổi nhiều, viết lại chúng.
- Không dùng `rm -rf`. Xoá file thừa bằng `python3 -I -c "import os; os.remove('<đường dẫn>')"`.
