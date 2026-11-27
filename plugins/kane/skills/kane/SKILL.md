---
name: kane
description: "Chỉ đường khi việc thường ngày chưa rõ dùng skill nào: \"chuẩn làm việc của tôi là gì\", \"bắt đầu từ đâu\", \"nên dùng cái nào\". Nêu luật làm việc chung và chỉ sang kane:write-human-docs, kane:wiki, kane:init, kane:resume."
---

# kane — bảng tra chuẩn của chủ kane

Skill nào không có trong phiên thì bỏ qua và làm như Claude bình thường.

## Bộ điều phối (gộp từ sp 4.17.1, MIT, haiha-ux — lõi)
| Việc | Skill / agent |
|---|---|
| Khởi tạo dự án, tiếp tục, đổi chế độ | `/kane:init`, `/kane:resume`, `/kane:switch` |
| Vòng xây dựng, bảo trì, viết tài liệu | `kane:build-loop`, `kane:maintain`, `kane:write-human-docs` |
| Đồng bộ kane với chuẩn gốc trên máy | `kane:sync` |
| Agent | `kane:builder` (viết mã, TDD), `kane:critic` (phản biện), `kane:grunt` (chạy lệnh), `kane:scout` (tra cứu), `kane:writer` (tài liệu) |

## Lấy thêm từ crew 0.3.0 (MIT, An Thien Truong)
Skill `kane:code-style`.

## Wiki Obsidian (claude-obsidian 1.9.2, MIT, AgriciDaniel)
Skill `kane:wiki*`, `kane:canvas`, `kane:think`, `kane:obsidian-*`, `kane:defuddle`, `kane:save`; lệnh `/kane:wiki`, `/kane:save`…; agent `kane:wiki-ingest`, `kane:wiki-lint`, `kane:wiki-verifier`. KHÔNG chép hook của plugin này (hook gốc tự `git commit` thư mục wiki sau mỗi lần sửa, trái luật cấm commit ở một số dự án). Script phụ ở `obsidian/`.

## MCP (`.mcp.json`, đường dẫn theo dự án đang mở)
context7 (tài liệu thư viện), exa (tìm web), playwright (trình duyệt, qua `hooks/pw.js`), codegraph (bản đồ mã của dự án), pdf (đọc PDF trong dự án), obsidian (đọc `wiki/` của dự án). MCP riêng từng dự án (freecad, kicad, các kho Obsidian cố định của Company) vẫn ở `.mcp.json` của dự án đó.

## Luật làm việc chung (tóm từ CLAUDE.md toàn cục của chủ kane ngày 2026-11-26)
1. **Giải thích cho user:** tiếng Việt; kết luận trước; gọi mọi thứ bằng nội dung, mã chỉ đặt trong ngoặc ở cuối câu; không tự đặt nhãn rồi dùng nhãn để giải thích; thuật ngữ giải thích ngay lần đầu; mỗi ý chính một ví dụ cụ thể; câu ngắn, chủ động; số liệu để trong bảng.
2. **Mọi thay đổi có nguồn:** bài báo hạng cao, chuẩn chính thức, luật venue, hoặc file của user. Không có nguồn → `TỰ QUYẾT — chưa có nguồn`, đưa lựa chọn cho user. Cuối việc: bảng thay đổi → nguồn → trạng thái.
3. **Nguồn trích trong paper phải đọc toàn văn** (mọi trang); ghi "đọc toàn văn N/N trang". Nguồn khác đọc phần cần, ghi "đọc phần X".
4. **Ghi chú cũ là ảnh chụp:** trước khi một ghi chú (STATE, wiki, memory) quyết định việc làm, kiểm nó bằng một phép thử rẻ; lệnh mới của user thắng ghi chú cũ.
5. **Không dùng `rm -rf`, `rm -r`:** xoá thư mục bằng `python3 -I -c "import shutil,sys; [shutil.rmtree(p) for p in sys.argv[1:]]" <thư mục>`, nêu tên chính xác, chỉ xoá thứ mình tạo.
6. **Báo cáo kỹ thuật:** đang cố làm gì; đã biết gì (số, file:dòng); cần gì tiếp và ai làm.
