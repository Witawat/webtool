# SESSION_STATE.md

## Objective
ออกแบบ + สร้างเว็บเครื่องมือเครือข่ายสไตล์ yougetsignal.com (ไทย/EN) — ครอบคลุมทั้งหมด 17 เครื่องมือ + UI ไทย/EN + Bulk lookup

## ข้อสำคัญ
- สแต็ก: Python 3.12 + FastAPI + uvicorn, Jinja2 SSR + vanilla JS (ไม่มี build step), ใช้ fetch+JSON (ไม่ใช้ form submit)
- **แผนเป็น implementation-ready** — docs/PLAN.md มี: JSON schema ครบ 17 ตัว (§5), ตาราง timeout/rate-limit/limit (§4.1), error model (§4.3), frontend architecture (§7), เฟส+DoD (§11)
- 14 self-host (เฟส 1) / 3 external: reverse_ip=HackerTarget, network_location=ip-api(http! ฟรีเป็น HTTP เท่านั้น)→MaxMind, reverse_email=premium ปิด default
- ข้อห้าม: อย่า subprocess, python-whois ต้อง to_thread (dns.asyncresolver async ตรง), ทุก endpoint timeout+semaphore, port scan IP เดี่ยว ≤100 พอร์ต, SSRF guard, หลัง proxy ใช้ --proxy-headers --forwarded-allow-ips
- packaging: PyInstaller 6.22.2 มีแล้ว / UPX ยังไม่มี / app.ico ยังไม่มี — spec + core/paths.py + _MEIPASS + UPX=AV false positive
- Repo GitHub: **Witawat/webtool** (public) — สร้างแล้ว 2026-09-06 · release ครั้งแรกต้องสร้าง tools/release-notes-patch.py (ต้นแบบ Cloudflare, ปรับ DEFAULT_REPO=Witawat/webtool) · กับดัก mojibake ไทย + read tool ตรวจ

## Completed
- **Phase 0 เสร็จสมบูรณ์** (commit `954f208` "chore: scaffold project skeleton (Phase 0)" — push ขึ้น origin/master แล้ว): main.py + core/ 7 ไฟล์ + routers/home.py + templates(base/home) + static(css/js) + pyproject.toml + .gitignore/.env.example/requirements.txt + setup/run-dev.bat + tests 6 ชุด
- ทดสอบจริง: `pytest -m "not network"` = **58 passed** · `ruff check .` = ผ่าน · เปิดเบราว์เซอร์ตรวจ DoD: หน้า grid 17 การ์ด, สลับไทย/EN, dark/light (แก้บั๊กปุ่ม theme กลับข้าง), /healthz 200, favicon SVG data-URI
- แก้ระหว่างทำ: validate_url_safe รองรับ IPv6 bracket + localhost (SSRF block), ruff UP045/UP035/UP047/UP041/B904
- commit แรก → `gh repo create Witawat/webtool --public --source . --remote origin --push` สำเร็จ
- **my-ip เสร็จ** (commit `dac7ac5`): services/my_ip.py (ip+version+hostname+geo null) + routers/my_ip.py (GET /tools/my-ip + POST /api/my-ip rate 60/min) + templates/tools/my-ip.html + static/js/tools/my-ip.js + tests/test_my_ip.py (schema + API + 429) · เพิ่ม tool.html (base หน้าเครื่องมือ) + main.py auto-discover router + json_ok helper · ทดสอบเบราว์เซอร์: ไทย/EN, AJAX ผล, title, favicon — 63 passed · ชื่อไทย my-ip = "ที่อยู่ IP ของฉัน"
- **port-checker เสร็จ** (commit `2adf7a3`): services/port.py check_port (resolve→connect→state open/filtered/closed + latency + service) + routers/port_checker.py (rate 10/min, 400/429) + templates/tools/port-checker.html (host+port + Common Ports ปุ่มลัด chip) + static/js/tools/port-checker.js + tests/test_port_checker.py (unit + network marker + API) · ทดสอบเบราว์เซอร์: 8.8.8.8:443 → open + HTTPS + badge เขียว + ปุ่มลัดเติม port — 70 passed
- **dns เสร็จ** (commit `687837a`): services/dns_lookup.py (dns.asyncresolver async ตรง + gather parallel + _format_value ต่อ type + reverse PTR ถ้าอินพุตเป็น IP) + routers/dns_lookup.py (rate 30/min, types validate 9 ตัว) + templates/tools/dns.html (checkbox types 9) + static/js/tools/dns.js (ตาราง Type/Name/TTL/Value) + tests/test_dns_lookup.py (format pure + API 400/429 + network จริง) · ทดสอบเบราว์เซอร์: example.com A/MX/TXT ตารางครบ + TTL — 80 passed + network 3 ผ่าน

## Active
- **Phase 1 ตัวถัดไป: subnet-calc** (ลำดับ: my-ip ✓ → port-checker ✓ → dns ✓ → subnet-calc → port-scan → ping → traceroute → ssl → whois → asn-rdap → fetch → header → phone → email-dns)
- subnet-calc schema §5.13: `{cidr}` → network/broadcast/netmask/wildcard/first_host/last_host/usable_hosts/total_hosts/prefix/ip_version · `ipaddress` pure **ไม่แตะ network** → rate สูง 60/min, ไม่ต้อง timeout · input ผ่าน parse_cidr

## Blocked
- ไม่มี

## Next Move
1. **subnet-calc**: services/subnet_calc.py (pure ipaddress) + routers/subnet_calc.py (rate 60/min) + templates/tools/subnet-calc.html (cidr input) + static/js/tools/subnet-calc.js (render key-value) + tests/test_subnet_calc.py (pure unit ครบ) → ขีด CHECKLIST + commit `feat(subnet-calc): ...`
2. ต่อ port-scan (IP เดี่ยว ≤100, semaphore) → ping (icmplib + TCP fallback)
3. Phase 2: reverse_ip + network_location · Phase 3: reverse_email · Phase 4: polish + Bulk + i18n เต็ม + README/CHANGELOG · Phase 5: packaging + release

## คำสั่งยืนยัน
- setup: `setup.bat` · dev: `run-dev.bat` · test: `pytest -m "not network"` · lint: `ruff check .` · build: `build.bat` (Phase 5)
- วิธีรัน server ตรวจด้วยเบราว์เซอร์: `.venv\Scripts\python -m uvicorn main:app --host 127.0.0.1 --port 8000`

## Commit ล่าสุด
- `687837a` feat(dns): add dns lookup tool · version: 0.1.0
