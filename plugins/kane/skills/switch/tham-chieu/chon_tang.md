# Chọn gói plugin cho dự án

Mục đích: mỗi dự án chỉ nạp các plugin kane nó cần, vì mọi plugin đang bật đều nạp lại ở mỗi lần gọi model (đỡ token mỗi lượt so với bật hết). Người dùng chọn loại việc bằng lời thường; mỗi lựa chọn ghi sẵn gói nó bật, ví dụ `→ bật: core`. Tên gói hiển thị bằng tiếng Anh: tầng lồng nhau nối bằng `›`, gói việc nằm trong ngoặc ngay sau tầng có `chua_viec` (không có thì nối bằng `+`), gói `giu` nối cuối bằng `+`. Danh mục gói và bảng `loai_viec` (các bước hỏi) nằm ở `${CLAUDE_PLUGIN_ROOT}/scripts/goi_tang.json`; thêm gói là thêm dòng ở đó, không sửa code.

## Các bước
1. Chạy `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/chon_tang.py" goi-y "<thư mục dự án>"` (biến không được thay → tìm `chon_tang.py` trong `~/.claude/plugins/cache/`). Kết quả JSON có `cau_hoi` (danh sách câu, đã lọc gói chưa cài), `tu_dong` (câu chỉ còn 1 lựa chọn, đã chọn luôn), `de_xuat` (mã gói theo dấu hiệu dự án), `plugin_bat`. `cau_hoi` rỗng → không có gì để hỏi: chạy bước 3 với `gon` (hoặc `tinh` với id rỗng).
2. Có `chạy không người trực` (`claude -p`) hoặc `/goal` đang bật → không hỏi: lấy id của lựa chọn có `(Recommended)` đầu tiên ở mỗi câu bước 1 rồi sang bước 3; không có gợi ý → `gon`.
3. Hỏi bằng AskUserQuestion, theo `cau_hoi` (chỉ đưa `question`, `header`, `multiSelect`, `options[].label/description` vào công cụ; `id`, `ma`, `chi_khi` để bạn tra; mỗi câu đã gom sẵn tối đa 4 lựa chọn, tối đa 4 câu một lần gọi):
   - Lần gọi 1: các câu có `id` = `nhom` (nếu có hơn 4 lựa chọn, script đã chia thành 2 câu). Dòng đầu `Như lần trước (Recommended)` (id `truoc`) là chế độ nhanh: user chọn nó thì dừng hỏi, dùng thẳng. Nhóm có dấu hiệu dự án cũng được đánh `(Recommended)` và đứng đầu, nhưng không tự bật.
   - Lần gọi 2: các câu còn lại mà `chi_khi` thoả (`chi_khi` là id lựa chọn bước 1 mà user đã chọn; `null` thì luôn hỏi): `loai` và `them` khi chọn Dựng sản phẩm, `muc` khi chọn Nghiên cứu, `tu` khi chọn Tự chọn từng gói, `ca-nhan` (chỉ có khi gói cá nhân đã cài và chưa bật). Quá 4 câu thì chia hai lần gọi. Câu `muc` chọn một; mọi câu khác chọn nhiều, bỏ trống được.
   - Không bao giờ hỏi lại điều script đã bỏ (`tu_dong`).
4. Gom id đã chọn (cách nhau dấu phẩy) và chạy `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/chon_tang.py" tinh "<thư mục dự án>" <id,...>` (không chọn gì → `gon`). Kết quả: `ghi` (mã gói), `bat` (chuỗi hiển thị), `tokens`. `truoc` thắng mọi id khác. Gói nào cần plugin khác (`phu_thuoc` trong danh mục) thì tự kéo theo plugin đó.
5. Chạy `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/chon_tang.py" ghi "<thư mục dự án>" <giá trị ghi ở bước 4>`. Script tự bật plugin phụ thuộc, tắt plugin đã cài khác trong dự án, không đụng plugin riêng của máy (trừ khi user chọn `ca-nhan` thì chỉ bật thêm), không bao giờ ghi plugin chưa cài. Ghi vào `<dự án>/.claude/settings.local.json` (cá nhân, không commit; giữ nguyên khoá khác).
6. Báo user 1–2 dòng: `bat`, token mỗi lượt. Nhắc: **gõ `/reload-plugins` một lần để áp dụng ngay** (MCP của plugin vẫn chỉ đổi khi mở phiên mới; reload làm mất bộ nhớ đệm lời nhắc một lần; nguồn: code.claude.com/docs/en/plugins/cli-reference). Thanh trạng thái (nếu có) hiện `↻ /reload-plugins` cho tới khi áp dụng.

## Luật
- Không bao giờ nêu tên hay nhắc tới plugin/gói user chưa cài: chỉ nói về những gì có trong `cau_hoi`.
- Dấu hiệu dự án (index.html, ProjectSettings, *.tex…) chỉ đánh `(Recommended)`, không tự chọn thay user.
- Script lỗi (mã thoát 2) → báo nguyên văn lỗi, không tự sửa settings tay.
- Xem trạng thái: `chon_tang.py hien "<thư mục>"`.
