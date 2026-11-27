#!/usr/bin/env node
// Gợi ý khi lệch: câu user khớp từ khoá của một gói plugin ĐÃ CÀI nhưng đang TẮT ở dự án này → nhắc 1 dòng, mỗi gói 1 lần mỗi phiên.
// Danh mục gói đọc từ scripts/goi_tang.json (không mã cứng tên gói/plugin); từ khoá: `tu_khoa` của từng gói.
// Gói chưa cài đủ (kể cả plugin phụ thuộc) → im lặng. Hook lỗi → cho qua.
const fs = require('fs');
const os = require('os');
const path = require('path');

const khongDau = (s) => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').toLowerCase();
const coTu = (cau, tu) => khongDau(tu).split('+').every((p) => new RegExp('(^|[^a-z0-9])' + p.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '([^a-z0-9]|$)').test(cau));

const doc = (f) => { try { return JSON.parse(fs.readFileSync(f, 'utf8')); } catch (e) { return {}; } };
const danhMuc = () => doc(process.env.KANE_GOI_TANG || path.join(__dirname, '..', 'scripts', 'goi_tang.json'));
const ten = (k) => k.split('@')[0];

function baoHam(cat, ps) {
  const ra = new Set(); const moi = [...ps];
  while (moi.length) { const p = moi.pop(); if (!ra.has(p)) { ra.add(p); moi.push(...(((cat.plugins || {})[p] || {}).phu_thuoc || [])); } }
  return ra;
}

function daCai(cat, cwd, home) {
  const ra = new Set();
  const pl = doc(path.join(home, '.claude', 'plugins', 'installed_plugins.json')).plugins || {};
  for (const [k, ban] of Object.entries(pl)) {
    const [n, mkt] = k.split('@');
    if (!(cat.marketplace || []).includes(mkt)) continue;
    if ((Array.isArray(ban) ? ban : []).some((b) => b.scope === 'user' || (b.projectPath && cwd.startsWith(b.projectPath)))) ra.add(n);
  }
  return ra;
}

// Người dùng < dự án < local, cùng thứ tự ưu tiên của Claude Code.
function dangBat(cwd, home) {
  const gop = {};
  for (const f of [path.join(home, '.claude', 'settings.json'), path.join(cwd, '.claude', 'settings.json'), path.join(cwd, '.claude', 'settings.local.json')]) Object.assign(gop, doc(f).enabledPlugins || {});
  return new Set(Object.entries(gop).filter(([, v]) => v === true).map(([k]) => ten(k)));
}

function nhacLech({ cat, prompt, cwd, home, daNhac }) {
  const p = String(prompt || '').trim();
  if (!p || p.startsWith('/') || !cat.goi) return { text: '', ma: [] };
  const cau = khongDau(p); const cai = daCai(cat, cwd, home); const bat = dangBat(cwd, home);
  const dong = []; const ma = [];
  for (const g of cat.goi) {
    if (g.loi || g.giu || daNhac.has(g.ma)) continue;
    if (![...baoHam(cat, g.plugin)].every((x) => cai.has(x)) || g.plugin.every((x) => bat.has(x))) continue;
    const tu = (g.tu_khoa || []).find((t) => coTu(cau, t));
    if (!tu) continue;
    dong.push(`[kane] Việc này dùng ${g.ten} (${g.plugin.join(', ')}), đang tắt ở dự án này: chạy /kane:switch để bật, rồi gõ /reload-plugins.`);
    ma.push(g.ma);
  }
  return { text: dong.join('\n'), ma };
}

// Có ghi nhớ "đã nhắc" theo phiên (file trong thư mục tạm).
function lech(inp, opt = {}) {
  const home = opt.home || os.homedir();
  const cwd = (inp && inp.cwd) || process.env.CLAUDE_PROJECT_DIR || process.cwd();
  const f = path.join(opt.tmp || os.tmpdir(), `kane-lech-${String((inp && inp.session_id) || process.ppid).replace(/[^\w-]/g, '_')}.json`);
  const da = new Set(Array.isArray(doc(f)) ? doc(f) : []);
  const r = nhacLech({ cat: opt.cat || danhMuc(), prompt: inp && inp.prompt, cwd, home, daNhac: da });
  if (r.ma.length) { try { fs.writeFileSync(f, JSON.stringify([...da, ...r.ma])); } catch (e) { /* bỏ qua */ } }
  return r.text;
}
module.exports = { nhacLech, lech, baoHam };
