# SESSION_STATE.md

## Objective
ออกแบบ + สร้างเว็บเครื่องมือเครือข่ายสไตล์ yougetsignal.com (ไทย/EN) — ครอบคลุมทั้งหมด 17 เครื่องมือ + UI ไทย/EN + Bulk lookup

## ข้อสำคัญ
- Repo ว่างเปล่า (git init สด) — ยังไม่มีโค้ดเลย
- สแต็ก: Python 3.12 + FastAPI + uvicorn, Jinja2 SSR + vanilla JS (ไม่มี build step), ใช้ fetch+JSON (ไม่ใช้ form submit)
- **แผนเป็น implementation-ready** — docs/PLAN.md มี: JSON schema ครบ 17 ตัว (§5), ตาราง timeout/rate-limit/limit (§4.1), error model (§4.3), frontend architecture (§7), เฟส+DoD (§11)
- 14 self-host (เฟส 1) / 3 external: reverse_ip=HackerTarget, network_location=ip-api(http! ฟรีเป็น HTTP เท่านั้น)→MaxMind, reverse_email=premium ปิด default
- ข้อห้าม: อย่า subprocess, python-whois ต้อง to_thread (dns.asyncresolver async ตรง), ทุก endpoint timeout+semaphore, port scan IP เดี่ยว ≤100 พอร์ต, SSRF guard, หลัง proxy ใช้ --proxy-headers --forwarded-allow-ips
- packaging: PyInstaller 6.20.0 มีแล้ว / UPX ยังไม่มี / app.ico ยังไม่มี — spec + core/paths.py + _MEIPASS + UPX=AV false positive

## Completed
- ตรวจเว็บ + ลองใช้จริง (เบราว์เซอร์): หน้าแรก grid, Port Checker ผล "Port 80 ... is filtered" badge สี, /th แปลไทยไม่ครบ — ภาพใน docs/ui-ref/
- เขียน AGENTS.md + docs/PLAN.md (implementation-ready 16 หัวข้อ + Git/GitHub §14 + Release §15) + docs/SESSION_STATE.md + **docs/CHECKLIST.md** (ตัวติดตามงาน ต่อเฟส/ต่อเครื่องมือ)
- แก้รอบแล้ว: 18→17, dns.asyncresolver, Phone Geo self-host, SSRF guard รายละเอียด, .bat 4 ตัว, packaging §13, UI/UX §8
- **เพิ่ม Git/Release**: ชื่อผู้พัฒนา (git user) = Maker Witawat <witawat57@gmail.com> (ตั้งใน config แล้ว) · บัญชี GitHub = Witawat (active) · repo ใช้ `Witawat/webtool` · สร้าง repo หลัง Phase 0 (`gh repo create Witawat/webtool --source . --remote origin --push`) · release ครั้งแรกต้องสร้าง tools/release-notes-patch.py ในโปรเจกต์ (ต้นแบบ Cloudflare, ปรับ DEFAULT_REPO=Witawat/webtool) · กับดัก mojibake ไทย + read tool ตรวจ
- **ตรวจแผนล่าสุด + แก้ไม่สอดคล้อง**: python-multipart → สำรอง (ใช้ fetch ล้วน), เพิ่ม TRUST_PROXY ในตารางค่า, เพิ่ม geoip2 (MaxMind), เพิ่ม pyproject.toml (pytest/ruff), §5.15 HackerTarget key ชัดขึ้น, PLAN §11 ชี้ docs/CHECKLIST.md

## Active
- ยังไม่ scaffold — ขั้นถัดไป: **Phase 0** ตาม PLAN §11 + ขีด docs/CHECKLIST.md (main.py + core/ ทั้ง 7 + base/home template + css/js + pyproject.toml + .gitignore + .env.example + requirements.txt + setup/run-dev.bat)

## Blocked
- ไม่มี

## Next Move
1. Phase 0 + DoD (หน้าแรก grid 17 การ์ด, สลับภาษา/ธีม, /healthz, unit test ผ่าน) → commit แรก + `gh repo create Witawat/webtool --source . --remote origin --push`
2. Phase 1: 14 self-host เรียง my-ip → port-checker → dns → subnet-calc → port-scan → ping → traceroute → ssl → whois → asn-rdap → fetch → header → phone → email-dns (แต่ละตัวผ่าน "คุณภาพขั้นต่ำ" ใน CHECKLIST)
3. Phase 2: reverse_ip + network_location (ip-api http + Leaflet)
4. Phase 3: reverse_email (premium)
5. Phase 4: polish + Bulk + i18n เต็ม + CHANGELOG + README
6. Phase 5: app.ico + upx + webtool.spec + build.bat
7. Release ครั้งแรก: สร้าง tools/release-notes-patch.py + gh release create + PATCH (PLAN §15)

## คำสั่งยืนยัน
- setup: `setup.bat` · dev: `run-dev.bat` · test: `pytest -m "not network"` · lint: `ruff check .` · build: `build.bat`

## Commit ล่าสุด
- ไม่มี (ยังไม่มี commit) · version: 0.0.0
