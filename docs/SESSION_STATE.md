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
- **subnet-calc เสร็จ** (commit `578d095`): services/subnet_calc.py (pure ipaddress, /31 /32 IPv6) + routers/subnet_calc.py (rate 60/min) + template/js (key-value) + tests/test_subnet_calc.py (pure ครบ) — 89 passed
- **port-scan เสร็จ** (commit `7a68378`): services/port.py เพิ่ม scan_ports (Semaphore+parallel, resolve_ip public) + routers/port_scan.py (IP เดี่ยวเท่านั้น ≤100 ports, rate 3/min, outer timeout = ceil×timeout+10) + template/js (ตาราง open ports) + tests/test_port_scan.py (400/429/network) — 96 passed · ⚠️ rate 3/min แคบ → test ต้องจำกัด API calls ในไฟล์ (ลบ reversed_range test)
- **ping เสร็จ** (commit `2585f94`): services/ping.py (icmplib async_ping + TCP fallback 80/443 + icmp:false) + routers/ping.py (rate 10/min, count 1-10) + template/js (badge alive + rtt) + tests/test_ping.py — 102 passed · ทดสอบจริง 1.1.1.1 → ICMP ทำงาน rtt ~20ms (privileged=False ใช้ได้บนเครื่องนี้)
- **traceroute เสร็จ** (commit `fff8fdb`): services/traceroute.py (icmplib.traceroute sync → asyncio.to_thread) + routers/traceroute.py (rate 3/min, max_hops 3-30) + template/js (ตาราง hop) + tests/test_traceroute.py — 107 passed · ทดสอบจริง 1.1.1.1 → 5 hops + rtt
  - ⚠️ **icmplib 3.0.4 gotchas**: ไม่มี async_traceroute (มีแค่ traceroute sync → to_thread) · traceroute ไม่รับ privileged (ต้อง raw socket เสมอ) · Hop object มี `distance` ไม่มี `ttl` (แมป ttl=distance) · rtts sanitize None/inf
- **ssl เสร็จ** (commit `0c52dbf`): services/ssl_checker.py (ssl.CERT_NONE+check_hostname=False เพื่อดึง cert แม้ไม่ผ่าน verify → cryptography แยก field + _host_matches wildcard + warnings expired/expires_soon/self_signed/hostname_mismatch) + routers/ssl_checker.py (rate 10/min, port default 443) + template/js (banner เตือน + การ์ด cert) + tests/test_ssl_checker.py — 117 passed · ทดสอบจริง example.com → TLSv1.3 + cert ครบ (เจอ/แก้ bug: _cert_info ลืมคืน key warnings)
- **whois เสร็จ** (commit `60429c7`): services/whois.py (**python-whois ใน asyncio.to_thread** + _as_list/_fmt_date + tld_privacy จาก hint "privacy/redacted") + routers/whois.py (parse_domain เท่านั้น ไม่รับ IP, rate 10/min) + template/js (การ์ด + raw_text collapsible) + tests/test_whois.py — 126 passed · ทดสอบจริง example.com → registrar RESERVED-IANA (เจอ/แก้ bug: whois.js rows() ไม่ return html)
- **asn-rdap เสร็จ** (commit `9dcc3a1`): services/rdap_asn.py (httpx rdap.org + follow_redirects → RIR, parse cidr/org จาก entities/vcard) + routers/asn_rdap.py (rate 20/min, detect IP หรือ ASN จาก query เดียว) + template/js (การ์ด + provider-note) + tests/test_asn_rdap.py (parsers pure + network) — 133 passed · ทดสอบจริง 8.8.8.8 → NET-8-8-8-0-2/Google LLC, ASN 15169 → GOOGLE
- **fetch เสร็จ** (commit `172d007`): services/fetch_http.py (**manual redirect loop + SSRF guard ทุก redirect** + ตัด body 1MB) + routers/fetch_http.py (method/headers/body/follow, rate 10/min) + template/js (method select + headers/body textarea + badge status + collapsible) + tests/test_fetch_http.py (SSRF/400/429/network) — 139 passed · ⚠️ rate test อย่าใช้ URL จริง (8.8.8.8) — ใช้ 127.0.0.1 (block เร็ว) กัน test ค้าง
- **header เสร็จ** (commit `ab869ee`): services/header_checker.py (GET + วิเคราะห์ security headers 6 ตัว + score 0-6 + SSRF) + routers/header_checker.py (rate 10/min) + template/js (score + badge present/missing ต่อ header) + tests — 144 passed · example.com → 200 + score 0/6 (ไม่มี security headers)
- **phone เสร็จ** (commit `672abe9`): services/phone_geo.py (**phonenumbers offline** — parse/valid/e164/region/carrier/timezones/type) + routers/phone_geo.py (rate 20/min) + template/js (badge valid) + tests/test_phone_geo.py (offline, ไม่ต้อง network) — 152 passed · +16692226000 → US/California/America_Los_Angeles, 2ms
- **email-dns เสร็จ** (commit `b920978`): services/email_dns.py (MX + TXT spf/dmarc + DKIM selectors 8 ตัว + summary pass/warn/fail) + routers/email_dns.py (rate 30/min) + template/js (ตาราง MX + badge ต่อ spf/dkim/dmarc) + tests — 155 passed · gmail.com → MX 5 + SPF + DMARC (DKIM ไม่พบ = จริงของ gmail)

## ✅ **Phase 1 จบ — 14 self-host ครบ** · `pytest -m "not network"` = 155 passed · `ruff check .` ผ่าน · ทุกตัวตรวจเบราว์เซอร์แล้ว (ภาษาไทย/EN + AJAX + badge)

## ✅ **Phase 2 จบ — external** (171 passed, ruff ผ่าน)
- **providers/geoip.py**: ip-api **http** (`http://ip-api.com/json/<q>?fields=...`) default · ถ้า `MAXMIND_DB_PATH` (เพิ่มใน config/.env.example) → geoip2 GeoLite2 (to_thread, resolve domain ก่อน) · คืน dict {query,ip,city,region,country,country_code,lat,lon,isp,org,asn,provider}
- **providers/reverse_ip.py**: HackerTarget `reverseiplookup/?q=<ip>` (ข้อความล้วน) + `is_upstream_error` (error/API count exceeded) + `parse_domains` · key append `&key=` ถ้ามี
- **reverse-ip** (commit `3cacfd7`): router rate 3/min + SSRF (block internal IP) + template/js (ตารางโดเมน + count) + test (mock provider + network) · 8.8.8.8 → 500 โดเมน
- **network-location** (commit `e9b909e`): router rate 10/min + SSRF (IP internal หรือ domain resolve → internal block) + template/js + **Leaflet map** (CDN unpkg, extra_head/extra_scripts block ใน base.html) + test (mock + ip-api จริง) · 8.8.8.8 → Ashburn/US + map
- ⚠️ กับดัก: PS 5.1 `Set-Content -Encoding UTF8` เติม BOM → เขียนไฟล์โค้ดใหม่ต้อง UTF8-no-BOM (เจอตอน rename validation.py) · SSRF guard ใช้ public `is_forbidden_ip`/`resolve_host_ips` (rename จาก _private ใน validation)

## ✅ **Phase 3 จบ — premium** (180 passed, ruff ผ่าน)
- **email-lookup** (commit `26cf23b`): providers/email.py (ไม่มี EMAIL_API_KEY → **TOOL_DISABLED 503**; มี key → คืน {email, provider, available:true, result:null} placeholder — ยังไม่มี provider จริง) + routers/email_lookup.py (rate 3/min) + template/js (หน้าแจ้ง "ต้องตั้งค่า EMAIL_API_KEY" เมื่อไม่มี key) + tests/test_email_lookup.py (parse_email + 503/400/429 + mock key) · เพิ่ม `parse_email` ใน core/validation.py

## ✅ **Phase 4 จบ — polish** (189 passed, ruff ผ่าน)
- **Bulk lookup** (commit `3592300`): services/bulk.py (registry 10 เครื่องมือ: dns/whois/subnet-calc/phone/ping/ssl/email-dns/reverse-ip/network-location/email-lookup · ≤10 ค่า · per-item timeout 20s · AppError → error แปลตาม lang) + routers/bulk.py (rate 5/min, GET /tools/bulk) + template/js (ตารางผล) + tests/test_bulk.py · ตรวจเบราว์เซอร์: subnet-calc 2 ค่า → ตาราง 2 แถว
- **about/disclaimer**: routes /about + /disclaimer + templates + nav links (i18n nav.about/nav.disclaimer/page.*)
- **README.md + CHANGELOG.md** (section v0.1.0 — release ใช้ย่อจากนี้)
- i18n เต็ม: test_i18n full coverage th=en keys + tool 17 name/desc · แก้ string แข็ง bulk.js (Status/Result → i18n)
- ⚠️ กับดักตอน edit i18n: แทนที่ block ที่มี nav.lang → เผลอตัด nav.lang th หาย (ต้องตรวจคืน)

## ✅ **Phase 5 จบ — packaging exe** (189 passed, ruff ผ่าน)
- **assets/app.ico** (Pillow: วงกลมฟ้า + W + จุด — สร้างด้วยสคริปต์ชั่วคราว)
- **main.py**: static import routers 18 ตัว (PyInstaller วิเคราะห์ไม่เห็น dynamic import → ModuleNotFoundError) · CLI `--host/--port/--no-browser/--headless` + เปิด browser อัตโนมัติ + stdout/stderr fallback (devnull) + uvicorn log_config ปลอดภัย (formatter ไม่พึ่ง isatty)
- **core/paths.py**: frozen → TEMPLATES/STATIC จาก _MEIPASS, **LOGS_DIR = exe dir\logs** (ไม่ใช่ temp)
- **webtool.spec** (onefile + icon + add-data templates/static + hiddenimports uvicorn loops/protocols/cryptography/python_multipart + UPX optional จาก UPX_DIR env) · **build.bat** (-y + PATH ใส่ UPX_DIR) · **run-exe.bat** (start /min)
- **Smoke test ผ่าน**: dist\webtool.exe → healthz ok + home 17 cards + api subnet/port-checker 200 + app.log ที่ dist\logs + **browser เปิดอัตโนมัติ** (มี request จาก browser ใน log) · exe 20.4MB
- ⚠️ **กับดัก packaging (สำคัญ):**
  1. **windowed (console=False) exe ค้างก่อน Python เริ่ม** บนเครื่องนี้ (GUI subsystem) → ใช้ **console=True** + run-exe.bat `start /min` (ยอมหน้าต่าง minimized) — บันทึก: ถ้าจะใช้ windowed ต้องทดสอบบนเครื่องมี desktop
  2. **uvicorn formatter crash** `'NoneType' object has no attribute 'isatty'` เมื่อ sys.stdout=None → fallback devnull + log_config กำหนดเอง (formatter ธรรมดา)
  3. **pkgutil.iter_modules ใช้ไม่ได้ใน frozen** (ไม่เห็น routers) + **dynamic importlib ใช้ไม่ได้** → ต้อง static import
  4. logs ต้องอยู่ exe dir (LOG_DIR=DATA_DIR/logs) ไม่ใช่ _MEIPASS (temp หาย)

## Active
- **Release v0.1.0** (PLAN §15): สร้าง `tools/release-notes-patch.py` ในโปรเจกต์ (คัดลอกต้นแบบ Cloudflare → DEFAULT_REPO=Witawat/webtool → commit) · เขียน notes.md (write tool UTF-8) · `gh release create v0.1.0 --notes-file ... dist\webtool.exe` · PATCH SHA256 + body (กัน mojibake ไทย) · ตรวจ .checked ด้วย read tool

## Blocked
- ไม่มี

## Next Move
1. **สร้าง tools/release-notes-patch.py** (คัดลอกจาก D:\MyCode\Cloudflare\tools\release-notes-patch.py → ปรับ DEFAULT_REPO=Witawat/webtool) + commit `chore(release): add release-notes-patch script`
2. เขียน CHANGELOG section v0.1.0 (มีแล้ว) → เขียน notes.md ตาม template release-notes
3. `gh release create v0.1.0 --repo Witawat/webtool --title "WebTool v0.1.0" --notes-file notes.md dist\webtool.exe`
4. `.venv\Scripts\python tools\release-notes-patch.py v0.1.0 notes.md --repo Witawat/webtool` → ตรวจ `.checked` ด้วย read tool

## คำสั่งยืนยัน
- setup: `setup.bat` · dev: `run-dev.bat` · test: `pytest -m "not network"` · lint: `ruff check .` · build: `build.bat` (Phase 5)
- วิธีรัน server ตรวจด้วยเบราว์เซอร์: `.venv\Scripts\python -m uvicorn main:app --host 127.0.0.1 --port 8000` · ⚠️ หลังสร้าง router ใหม่ต้อง restart server (auto-discover รันตอน create_app) — เห็น 404 /api/<slug> = ลืม restart

## Commit ล่าสุด
- `3592300` feat(bulk): add bulk lookup wrapper · version: 0.1.0 · **Phase 1-5 ครบ** — เหลือ release v0.1.0
