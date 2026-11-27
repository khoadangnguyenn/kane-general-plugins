#!/usr/bin/env node
// Gợi ý skill của MỘT tầng kane (mỗi plugin tầng có bản sao riêng, đọc dinh_tuyen_skill.json cạnh nó).
//   node goi_y_skill.js index   (SessionStart) → in luật định tuyến của tầng (không in lại danh sách skill Claude Code đã nạp).
//   node goi_y_skill.js prompt  (UserPromptSubmit) → câu user khớp từ khoá thì nhắc gọi đúng skill.
// Nguồn: Vercel 2026-01-27 (danh mục đặt sẵn trong ngữ cảnh: 100 % so với 53–79 %); Romanov TDS 2026-11-10
// (hook SessionStart: 15 % → 62 % với câu gián tiếp); câu có thứ tự hành động tốt hơn "MUST" (Vercel).
// Hook lỗi thì im lặng cho qua (van xả của sp).
const fs = require('fs');
const path = require('path');

const bang = () => JSON.parse(fs.readFileSync(path.join(__dirname, 'dinh_tuyen_skill.json'), 'utf8'));
const khongDau = (s) => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').toLowerCase();
const coTu = (cau, tu) => new RegExp('(^|[^a-z0-9])' + tu.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '([^a-z0-9]|$)').test(cau);

function danhMuc(b) {
  // Claude Code đã tự nạp danh sách skill (tên + mô tả): chỉ in luật định tuyến của tầng và lệnh user gõ (skill tắt với Claude).
  const lenh = b.skills.filter((s) => s.lenh).map((s) => `- ${s.viec} → user gõ \`${s.lenh}\` (Claude không tự gọi)`);
  return [b.ghi_chu ? `[${b.plugin}] ${b.ghi_chu}` : '', ...lenh].filter(Boolean).join('\n');
}

function khop(b, prompt) {
  const p = String(prompt || '').trim();
  if (!p || p.startsWith('/')) return [];
  const cau = khongDau(p);
  const ra = [];
  for (const s of b.skills) {
    const tu = (s.tu_khoa || []).find((t) => khongDau(t).split('+').every((phan) => coTu(cau, phan.trim())));
    if (tu) ra.push({ ...s, tu });
  }
  return ra.slice(0, 2);
}

function nhac(b, ds) {
  if (!ds.length) return '';
  return ds.map((s) => s.lenh ? `[${b.plugin}] Câu này khớp "${s.tu}" (${s.viec}): nhắc user gõ lệnh \`${s.lenh}\` (Claude không tự gọi được).` : `[${b.plugin}] Câu này khớp "${s.tu}" → skill \`${s.skill}\` (${s.viec}). Việc đầu tiên: gọi Skill \`${s.skill}\` (trước cả lệnh xem file như ls/Read), rồi làm theo các bước của nó. Không đúng việc thì bỏ qua lời nhắc này.`).join('\n');
}

function out(ev, text) {
  if (text) process.stdout.write(JSON.stringify({ hookSpecificOutput: { hookEventName: ev, additionalContext: text } }));
}

if (require.main === module) {
  try {
    const b = bang();
    if (process.argv[2] === 'index') out('SessionStart', danhMuc(b));
    else if (process.argv[2] === 'prompt') {
      let raw = '';
      process.stdin.on('data', (d) => (raw += d));
      process.stdin.on('end', () => {
        try {
          const inp = JSON.parse(raw || '{}');
          let lech = '';
          try { lech = require('./lech_tang.js').lech(inp); } catch (e) { /* cho qua */ }
          out('UserPromptSubmit', [nhac(b, khop(b, inp.prompt)), lech].filter(Boolean).join('\n'));
        } catch (e) { /* cho qua */ }
      });
    }
  } catch (e) { /* hook lỗi → cho qua */ }
}
module.exports = { khongDau, coTu, khop, nhac, danhMuc };
