---
name: auto
description: "Cho dự án đã khởi tạo tự chạy liền mạch, chỉ hỏi người ở việc lớn: \"cứ làm tiếp đi, tôi không cần xem từng bước\", \"làm hết giúp tôi, có gì quan trọng thì hỏi\", \"tự làm đến khi xong\". Đọc .ai/STATE.md, chọn bước kế, gọi skill con, lặp lại; chỉ dừng hỏi một câu khi sắp lên máy thật, xoá dữ liệu, ghi đè lịch sử git, tốn tiền, gửi dữ liệu ra ngoài, chọn hướng nghiên cứu, hoặc khách nghiệm thu. Việc khác tự quyết và ghi giả định. Khác kane:resume: resume mở lại dự án để cùng làm, có người quyết từng bước; auto chạy một mạch tới cổng lớn kế. Gõ /kane:auto [ghi chú]."
---
# Tự chạy tới cổng lớn kế

Bạn là điều phối viên. Không có `.ai/STATE.md` → dừng, bảo user chạy `/kane:init <mô tả>`. Người đã nói "tự làm" thì đừng hỏi lại những việc đảo ngược được: làm, ghi lại, trình kết quả, để người chỉnh sau.

## Vòng lặp
1. **Có khối `[kane brief]` trong context thì KHÔNG đọc STATE.md; chỉ đọc đoạn thiếu bằng offset/limit hoặc grep.** Không có khối thì đọc `.ai/STATE.md`: mục Chế độ, Đang chạy, Tiếp theo. Dòng "Đang chạy" còn sót = agent đã chết: làm như `kane:resume` bước 2.
2. Chọn bước kế theo thứ tự:
   - Có dòng `Tiếp: <plugin:skill> — <bước>` (do skill của từng gói ghi khi đóng pha hoặc qua cổng): gọi đúng skill đó bằng công cụ Skill, kèm bước. Nhiều dòng `Tiếp:` (dự án ghép) → làm từ trên xuống. Bạn không cần biết sổ riêng của gói (`.xxx/state.json`) nằm đâu.
   - Skill trong dòng đó không gọi được (chưa cài hoặc tắt): nói đúng một câu "bước này cần gói chứa `<skill>`, bật bằng /kane:switch rồi mở phiên mới" và dừng. Không đoán thay, không tự làm theo trí nhớ.
   - Không có dòng `Tiếp:`: theo `kane:resume` bước 3-5 (việc `[~]`, rồi `[ ]` của mốc hiện tại, gọi skill theo chế độ).
3. Làm xong bước → ghi STATE (một lần cho cả cụm kết quả) → quay lại 1. Hết việc `[ ]` hoặc gặp cổng → dừng và báo.
4. Đóng một mốc: gọi `kane:maintain` ngay, rồi báo user ≤5 dòng.

## Bảy cổng lớn: dừng, hỏi một câu kèm khuyến nghị
(a) triển khai lên máy thật hoặc môi trường thật · (b) xoá dữ liệu · (c) ghi đè lịch sử git (force-push, `reset --hard`, rebase đã đẩy) · (d) chi tiền, kể cả API trả phí · (e) gửi dữ liệu ra ngoài (email, tải lên dịch vụ, đăng công khai) · (f) chọn hướng nghiên cứu · (g) khách nghiệm thu, hoặc quyết định chạy thật.

Ví dụ câu hỏi: "Sắp đẩy bản này lên máy chủ thật. Khuyến nghị: chờ bạn xem bản thử trước. Đẩy luôn hay chờ?"

- Quyền deploy, push, nhập khoá do chủ dự án giữ: auto chỉ chuẩn bị lệnh, không tự chạy.
- Cổng đang chờ người ghi đúng một khuôn `Cổng <tên>: chờ người quyết — <việc>`; người trả lời xong → đổi thành `Cổng <tên>: <quyết định>, <ngày>`.
- Mọi việc ngoài bảy cổng: tự quyết, ghi một dòng `Giả định: <điều đã giả định>` vào STATE, làm tiếp. Không chặn chờ người với việc đảo ngược được.
- Chưa chắc việc có thuộc cổng không (ví dụ lệnh có thể xoá file) → coi là cổng.

## Giữ ngữ cảnh nhỏ
- Soát đơn giản (đếm, quét, đối chiếu danh sách, chạy test lấy kết quả): giao `kane:grunt` (haiku). Việc cần phán đoán (chọn thiết kế, đọc kết quả mơ hồ) giữ ở model chính.
- Log dài hoặc đầu ra lớn: giao agent đọc rồi trả tóm tắt ≤10 dòng kèm đường dẫn file; không dán log vào phiên chính.

## Ba nguyên tắc (nguồn: bài nói của Lauren Tan, AI Engineer 2026-11; diễn đạt lại, giấy phép gốc chưa xác minh)
- Chứng minh nó chạy được: "xong" chỉ khi đã chạy thật (test, lệnh, trang mở được) và có kết quả thật để báo; build qua chưa đủ. Bước có kiểm tra mà kiểm tra bị chặn quyền hoặc chưa chạy được thì KHÔNG đánh `[x]`: đánh `[~]` kèm "chưa kiểm: <lý do>" và nói rõ trong câu báo cuối.
- Giữ ngữ cảnh nhỏ: đẩy việc nặng cho agent con, giữ ở phiên chính bản tóm tắt.
- Lỗi lặp lại của agent thì biến thành kiểm tra tất định (test, lint, hook), không chỉ thêm một dòng nhắc vào luật. Thấy cùng một lỗi lần thứ hai: viết kiểm tra, rồi mới làm tiếp.

GHI CHÚ CỦA USER: $ARGUMENTS
