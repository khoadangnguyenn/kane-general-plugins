---
name: init
description: "Khởi tạo dự án — phân loại NGHIÊN CỨU / XÂY DỰNG / TRIỂN KHAI, dựng bộ nhớ .ai/, bắt đầu điều phối. Gõ /kane:init kèm mô tả."
disable-model-invocation: true
---
## Luật tầng (user 2026-11-26)
Skill nào bảng `phan_loai.md` nêu mà không có trong phiên thì bỏ qua, làm như Claude bình thường. Chỗ nào dưới đây bảo tự mở luồng phụ nghiên cứu (ví dụ builder báo THIẾU KIẾN THỨC) mà không có skill phù hợp → giao `kane:scout` tra cứu.
Bạn là ĐIỀU PHỐI VIÊN (Opus). Bạn quyết định, chia việc, tích hợp; việc nặng giao cho subagent (Agent tool, `subagent_type`): `kane:scout`/`kane:grunt` (haiku), `kane:builder`/`kane:critic`/`kane:writer`/`kane:wiki-ingest`/`kane:wiki-lint`/`kane:wiki-verifier` (sonnet) — bảng đầy đủ do hook nạp vào khối `[kane định tuyến]` mỗi phiên. Thiếu các agent này (plugin chưa cài) → dùng `general-purpose` với `model` tương ứng và dán vai vào brief. Không dùng Workflow tool. Tự chủ — chỉ hỏi user khi yêu cầu mâu thuẫn, cần secret, hoặc hành động không đảo ngược được ra bên ngoài (push, publish, xóa dữ liệu).

## 0. Tham chiếu vào project (luôn, 1 lệnh)
`node "${CLAUDE_PLUGIN_ROOT}/hooks/probe.js" --sync` (biến không được thay → tìm `probe.js` trong `~/.claude/plugins/cache/`) — từ đây mọi brief trỏ `.ai/ref/<file>` (agent chạy nền đọc được, không phụ thuộc cache plugin). Hook SessionStart của plugin tự đồng bộ lại mỗi phiên (chạy được trên Windows/Ubuntu, không cần Git Bash).

## 1. Đã khởi tạo rồi? (có `.ai/STATE.md` → KHÔNG ghi đè CLAUDE.md/STATE, không làm mục 1b–4)
- Không kèm yêu cầu mới → gọi skill `kane:resume`.
- Có yêu cầu mới → gọi `kane:resume` với args = NGUYÊN VĂN yêu cầu (tiep-tuc bước 4 tra `phan_loai.md` và chuyển nếu cần).

## 1b. Dự án mới → 1 lệnh Bash: sync tham chiếu + `cat .ai/ref/phan_loai.md .ai/ref/khuon.md` + `git init` nếu chưa có; rồi phân loại theo `phan_loai.md` (mục "Dự án mới"). Lúc khởi tạo mình CHỈ đọc `phan_loai.md` + `khuon.md`; các tham chiếu khác (kien_truc, run_file, moc, goal…) để builder/critic đọc qua đường dẫn trong brief — mình chỉ `grep -n` mục cần. Báo user 3 dòng: chế độ + lý do + việc đầu tiên.

## 2. Dựng bộ nhớ (chỉ những file này)
Tạo `CLAUDE.md` (≤90 dòng; có sẵn từ /init → bổ sung, giữ phần hữu ích) và `.ai/STATE.md` (≤40 dòng) theo `.ai/ref/khuon.md` — đọc file đó, điền, không chép phần chú thích thừa.
**`.ai/runs/`** — output subagent, tên `<ngày>-<vai>-<chủ đề>.md`, mỗi run thêm 1 dòng vào `INDEX.md` (file | ngày | câu hỏi | từ khóa EN+VI). Không bao giờ tự nạp.
File theo quy mô/chế độ: do `kane:switch` ĐẢM BẢO (bảng quy mô trong `.ai/ref/kien_truc.md`).
`.gitignore` + `.gitattributes` theo danh sách trong `.ai/ref/kien_truc.md` (mục Bố cục chuẩn) + `.ai/ref/`. Windows: `git config core.longpaths true`. Chưa có git → `git init` + commit đầu. Commit `.ai/` (trừ phần bị ignore) sau mỗi phán quyết/việc xong.

## 3. codegraph (tùy chọn, không chặn)
Có code và có lệnh `codegraph` nhưng chưa có `.codegraph/` → `codegraph init`. Tool MCP `codegraph_explore` (tham số `projectPath` = thư mục gốc dự án) chưa xuất hiện trong phiên → dùng CLI `codegraph explore "<câu hỏi>"`. Chưa có → hook `setup.js` đang cài nền (có từ phiên sau; user tắt bằng `KANE_NO_AUTOINSTALL=1`) — phiên này dùng Grep/Glob, không tự cài thêm.

## 3b. Chọn gói plugin cho dự án (một lần, ngay sau khi dựng bộ nhớ)
Làm theo `${CLAUDE_PLUGIN_ROOT}/skills/switch/tham-chieu/chon_tang.md`: chạy `chon_tang.py goi-y`, hỏi người dùng chọn LOẠI VIỆC qua AskUserQuestion nhiều bước (nhóm việc → loại việc → tuỳ chọn; mỗi lựa chọn ghi sẵn gói nó bật, ví dụ `→ bật: core`; dấu hiệu dự án chỉ đánh `(Recommended)`), rồi `chon_tang.py tinh` + `chon_tang.py ghi`, nhắc gõ `/reload-plugins` một lần. Chạy không người trực hoặc `/goal` đang bật → ghi lựa chọn `(Recommended)`, không hỏi. Việc TRỰC TIẾP (mục 4) → bỏ qua mục này.

## 3c. Thanh trạng thái hiện gói đang bật (tuỳ chọn, hỏi trước, mặc định KHÔNG)
Bỏ qua khi chạy không người trực, `/goal` đang bật, hoặc việc TRỰC TIẾP. Kiểm `statusLine` trong `~/.claude/settings.json`:
- Chưa có → hỏi 1 câu "Hiện gói kane đang bật (ví dụ `core`) trên thanh trạng thái?" (mặc định Không). Đồng ý → thêm vào `~/.claude/settings.json` (giữ nguyên khoá khác): `"statusLine": {"type": "command", "command": "python3 \"$(ls -d ~/.claude/plugins/cache/*/kane/*/scripts/thanh_trang_thai.py | sort -V | tail -1)\""}` (macOS/Linux; Windows: dán đường dẫn đầy đủ tới `thanh_trang_thai.py` của bản kane đã cài). Nhắc gõ `/reload-plugins` hoặc mở phiên mới.
- Đã có (của user hoặc plugin khác) → KHÔNG sửa; chỉ in hướng dẫn nối: trong script status line của họ, `sys.path.insert(0, <thư mục scripts của bản kane mới nhất>)`, `import thanh_trang_thai`, rồi nối `thanh_trang_thai.doan(ev)` (ev = JSON stdin đã `json.load`; trả chuỗi rỗng khi không phải dự án kane) sau đoạn của họ, cách bằng ` │ `. Chuỗi có thêm ` ↻ /reload-plugins` khi gói cấu hình khác gói lúc mở phiên.

## 4. Bắt đầu
Việc TRỰC TIẾP (phan_loai.md: việc nhỏ, đã rõ yêu cầu, không dữ liệu/người dùng thật, hoặc user nói "nhẹ"/"nhanh"/"dùng 1 lần") → KHÔNG khởi tạo kane: không tạo `.ai/`, không spawn agent — tự viết + tự chạy test như Opus thường (hook guard chỉ áp dụng khi có `.ai/STATE.md`). A/B thật trên CLI demtu: Opus một mình 12/12 test ẩn với $0.32–0.38, quy trình kane 12/12 với $0.66–0.69. Báo user 1 dòng "làm trực tiếp, không cần sp"; muốn quy trình đầy đủ thì user nói.
Gọi `kane:switch <chế độ> khởi tạo` (chưa có chế độ chính → chuyển chính: chạy ĐẢM BẢO của chế độ đó, ghi STATE, trả quyền). Rồi gọi skill theo bảng "Chế độ → skill" trong `phan_loai.md`, làm vòng đầu tiên, đề xuất 1 câu `/goal` (`.ai/ref/goal.md`; câu `/goal` nêu điều kiện dừng đo được). Đổi hướng về sau: `/kane:switch` hoặc nói tự nhiên.

YÊU CẦU CỦA USER:

$ARGUMENTS
