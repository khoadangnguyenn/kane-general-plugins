# Nguồn bên thứ ba

Kane gộp mã từ hai plugin. Chỉ đổi tên danh tính (sp, hyp thành kane); hành vi giữ nguyên.

| Thành phần | Nguồn | Phiên bản | Giấy phép |
|---|---|---|---|
| agents/ (builder, critic, grunt, scout, writer), hooks/ (trừ phần hyp), 7 skill: bao-tri, chuyen, khoi-tao, nghien-cuu, tiep-tuc, viet, xay-dung, package.json | plugin sp của haiha-ux (solo-prompts) | 4.17.1 | MIT, bản đầy đủ ở THIRD_PARTY/sp-LICENSE |
| agents/verifier.md, scripts/, bin/, 4 skill: vong, kiem-chung, phan-bac, so-bang-chung | plugin hyp của tác giả kane | 0.3.0 | tác giả là chủ kane |

Phụ thuộc runtime: @playwright/mcp 0.0.84 (Apache-2.0, cài bằng npm ci).
