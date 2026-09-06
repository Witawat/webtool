# CHECKLIST.md — ตัวติดตามความคืบหน้า (Progress Tracker)

> ใช้คู่กับ docs/PLAN.md — ขีด ✓ เมื่อทำเสร็จจริง (ทดสอบ/verify แล้ว ห้ามขีดตามที่ตั้งใจ) — session ใหม่อ่านไฟล์นี้รู้สถานะทันที

## กติกา
- เครื่องมือทุกตัวต้องผ่าน **คุณภาพขั้นต่ำต่อเครื่องมือ** (หัวข้อล่าง) ก่อนขีด ✓
- เรียงตามลำดับ PLAN §11 (easy → hard) อย่าข้าม

## Phase 0 — โครง
- [x] main.py (create_app, mount routers, /healthz, exception handler)
- [x] core/config.py (Settings + ค่าตาราง PLAN §4.1 + TRUST_PROXY)
- [x] core/paths.py (BASE_DIR + sys._MEIPASS)
- [x] core/validation.py (parse_ip/domain/host/port/cidr + validate_url_safe + PORT_NAMES)
- [x] core/rate_limit.py (RateLimiter + get_client_ip)
- [x] core/timeout.py (async_with_timeout)
- [x] core/errors.py (AppError + ตาราง code → HTTP)
- [x] core/i18n.py (STRINGS th/en + t + all_strings)
- [x] templates/base.html + home.html (grid 17 การ์ด)
- [x] static/css/style.css (dark/light) + static/js/app.js
- [x] pyproject.toml (pytest asyncio_mode + marker network + ruff config)
- [x] .gitignore + .env.example + requirements.txt
- [x] setup.bat + run-dev.bat
- [x] tests: conftest + test_validation / test_i18n / test_rate_limit / test_errors (+test_home)
- [x] DoD: run-dev.bat → หน้า grid 17 การ์ด · สลับไทย/EN + dark/light · /healthz 200
- [x] commit แรก + `gh repo create Witawat/webtool --source . --remote origin --push`

## Phase 1 — 14 self-host
- [x] 1. my-ip
- [x] 2. port-checker
- [x] 3. dns
- [x] 4. subnet-calc
- [x] 5. port-scan
- [x] 6. ping
- [x] 7. traceroute
- [x] 8. ssl
- [x] 9. whois
- [x] 10. asn-rdap
- [x] 11. fetch
- [x] 12. header
- [ ] 13. phone
- [ ] 14. email-dns

### คุณภาพขั้นต่ำต่อเครื่องมือ (ทำครบก่อนขีด)
- [ ] services/<slug>.py — คืน JSON ตาม schema PLAN §5
- [ ] routers/<slug>.py — GET /tools/<slug> (หน้า) + POST /api/<slug>
- [ ] templates/tools/<slug>.html + static/js/tools/<slug>.js (renderResult)
- [ ] tests/test_<slug>.py (unit; network จริง → marker `network`)
- [ ] ทดสอบจริง: input ถูก → ผลตรง schema
- [ ] edge: input ผิด → 400 · ยิงซ้ำ → 429 · timeout → 504
- [ ] i18n: ข้อความทุกอันผ่าน I18N (th+en, ไม่มี string แข็งใน JS)
- [ ] SSRF guard (เฉพาะ fetch / header / reverse_ip / network_location)
- [ ] แจ้ง provider ในหน้า (เฉพาะ external)

## Phase 2 — external
- [ ] providers/geoip.py (ip-api http → MaxMind geoip2 ถ้ามี key)
- [ ] providers/reverse_ip.py (HackerTarget, parse ข้อความล้วน)
- [ ] reverse_ip: router + page + js + test (mock provider)
- [ ] network_location: router + page + js + Leaflet map + test (mock provider)
- [ ] DoD: หน้าแจ้ง provider · mock test ผ่าน · ip-api http ใช้ได้จริง

## Phase 3 — premium
- [ ] providers/email.py (EMAIL_API_KEY)
- [ ] email_lookup: router + page + js (ไม่มี key → TOOL_DISABLED 503)
- [ ] DoD: ไม่มี key → 503 + หน้าแจ้ง "ต้องตั้ง key" · มี key → ทำงาน

## Phase 4 — polish
- [ ] Bulk lookup (wrapper หลายค่า ใช้ validation+rate limit เดิม)
- [ ] about / disclaimer / error / empty states
- [ ] README.md + CHANGELOG.md (เริ่ม section v0.1.0)
- [ ] แปลไทยเต็ม th/en ทุกหน้า
- [ ] DoD: `pytest -m "not network"` + `ruff check .` ผ่าน

## Phase 5 — packaging
- [ ] assets/app.ico (Pillow จาก PNG)
- [ ] upx → tools/upx/
- [ ] webtool.spec + build.bat + run-exe.bat
- [ ] DoD: build.bat → dist\webtool.exe รันได้ + เปิด browser อัตโนมัติ + icon ติด

## Release (หลัง Phase 5)
- [ ] สร้าง tools/release-notes-patch.py (คัดลอกต้นแบบ → DEFAULT_REPO=Witawat/webtool → commit)
- [ ] CHANGELOG section + เขียน notes.md (UTF-8, write tool)
- [ ] `gh release create` + `.venv\Scripts\python tools\release-notes-patch.py` + ตรวจ `.checked` ด้วย read tool
