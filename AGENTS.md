# AGENTS.md

โปรเจกต์: เว็บเครื่องมือเครือข่าย (network tools) สไตล์ yougetsignal.com — โจทย์จาก user: "ออกแบบเครื่องมือที่ทำงานเหมือน https://www.yougetsignal.com/th พร้อมแนะนำส่วนเพิ่มเติมและภาษาที่ใช้"

## สถานะปัจจุบัน (สำคัญ)
- Repo ยังว่างเปล่า — `git init` สด ไม่มี commit ไม่มีโค้ด
- ยังไม่ได้ scaffold — งานแรกของ agent คือสร้างโครงตามสแต็กข้างล่าง

## สแต็กที่ตัดสินใจ (ตอบโจทย์ "ใช้ภาษาอะไร")
- Backend: **Python 3 + FastAPI + uvicorn** (async — จำเป็นเพราะงาน network ต้องควบคุม timeout เอง)
- Frontend: เริ่มด้วย **HTML/CSS/vanilla JS ไม่มี build step** + Jinja2 SSR ตามความจำเป็น (เลี่ยง build pipeline ไว้ก่อน)
- Dependency: `requirements.txt` (หรือ uv)
- โฟลเดอร์อยู่ใต้ `Python_code\` → ยึด Python เป็นหลัก

## ขอบเขตเครื่องมือ (ตกลงแล้ว — ครอบคลุมทั้งหมด 17 อัน + UI ไทย/EN)
10 อันตามเว็บจริง (ตรวจ 2026): Port Checker, DNS Lookup, SSL/TLS Checker, WHOIS Lookup, Reverse IP Lookup, Fetch, Network Location, What Is My IP, Reverse E-mail Lookup, Phone Number Geolocator
+ ส่วนเสริม 7: Port Range Scanner, Ping, Traceroute, ASN/IP WHOIS (RDAP), HTTP Header Checker, Subnet/CIDR Calculator, e-mail domain DNS analysis
+ UI: ภาษาไทย + สลับ EN/TH (default th) + Bulk lookup (wrapper optional)

**แผนเต็ม (โครงสร้าง/API/เฟส/ข้อควรระวัง) อยู่ใน `docs/PLAN.md` — เริ่มงานให้อ่านก่อน** · **ติดตามสถานะงาน: `docs/CHECKLIST.md` (ขีด ✓ ทุกขั้น)**

## สถาปัตยกรรม / library — สิ่งที่ agent มักเข้าใจผิด
- **งาน network ทั้งหมดต้องรันฝั่ง server** — browser เปิด raw TCP / อ่าน WHOIS เองไม่ได้ และ API สาธารณะมี CORS กีดกัน
- Port scan/checker, ping, traceroute, DNS → Python `socket` / `icmplib` / `dnspython` รันบน asyncio
- WHOIS → `python-whois` หรือ raw whois ผ่าน port 43
- SSL/TLS → `openssl s_client` หรือ `ssl` module + `cryptography`
- GeoIP → MaxMind GeoLite2 (ฟรี ต้องสมัคร license key) หรือ ip-api.com (ฟรีไม่ต้อง key แต่อัตราจำกัด)
- **Reverse IP / Reverse E-mail ต้องพึ่ง API ภายนอก** (HackerTarget ฟรีจำกัด / SecurityTrails เสียเงิน) — มีข้อมูล self-host ไม่ได้ · Phone Geolocator กลับ self-host ได้ (library `phonenumbers` offline) · e-mail domain DNS analysis ก็ self-host (อ่าน TXT/MX ผ่าน DNS)

## Gotchas
- Port scan/checker หน้าตาคล้ายเครื่องมือโจมตี → จำกัด input (รับ IP เดี่ยวหรือช่วงเล็ก, domain ต้องแปลงเป็น IP ผ่าน DNS ก่อน), rate limit, timeout สั้น
- คำสั่งที่ค้างได้นาน (traceroute, port scan ทั้งช่วง) → ทุก endpoint ต้องมี timeout + จำกัด parallel
- ทุก feature ที่พึ่ง API ภายนอกต้องระบุ provider ในหน้าให้ user เห็นชัด

## Command (Windows — มี .bat wrapper ไว้ root)
- ครั้งแรก: `setup.bat` (สร้าง venv + ติดตั้ง deps)
- รัน dev: `run-dev.bat` (= `.venv\Scripts\python -m uvicorn main:app --reload`) หรือ `uvicorn main:app --reload`
- build exe: `build.bat` (รัน pyinstaller webtool.spec, UPX optional) · รัน exe: `run-exe.bat`
- test: `pytest -m "not network"` · lint: `ruff check .`

## UI/UX (ลองใช้เว็บจริงแล้ว — ภาพใน `docs/ui-ref/`)
- เลียนแบบ yougetsignal: grid การ์ดหน้าแรก, ผลลัพธ์ในหน้า (AJAX ไม่ reload) เป็นประโยค + badge สี (open=เขียว/filtered=เหลือง/closed=แดง), ปุ่มสลับไทย/EN (default th) + dark/light mode
- i18n ต้อง**แปลเต็มทุกหน้า** (เว็บจริงแปลไม่ครบ — Reverse IP/Fetch/E-mail/Phone ยังอังกฤษ)
- รายละเอียดครบ: §8 ของ `docs/PLAN.md`

## Git / GitHub / Release
- Repo ว่าง (git init สด) — ยังไม่มี commit/remote · ชื่อผู้พัฒนา (git user): **Maker Witawat <witawat57@gmail.com>** (ตั้งใน config แล้ว) · บัญชี GitHub: **Witawat** (`gh` auth active) · **repo ใช้ชื่อ `Witawat/webtool`**
- สร้าง repo หลัง Phase 0: commit แรกเสร็จ → `gh repo create Witawat/webtool --public --source . --remote origin --push`
- Commit: `feat(scope)/fix/chore/docs/refactor` + ทำงานบน master ตรง · ตรวจ `git status`+`git diff` ก่อนเสมอ · .gitignore ต้องมี .env/.venv/dist/build/logs
- Release (หลัง Phase 5): **ครั้งแรกสร้าง `tools/release-notes-patch.py` ในโปรเจกต์นี้** (คัดลอกจาก `D:\MyCode\Cloudflare\tools\release-notes-patch.py` → ปรับ DEFAULT_REPO=Witawat/webtool) แล้วทำตาม PLAN §15 · กับดัก: ห้าม `gh release edit` กับไฟล์ไทยบน Windows (mojibake cp874) — ใช้ PATCH ผ่าน Python เสมอ · ตรวจไทยด้วย read tool ไม่ใช่ PowerShell

## Packaging (exe onefile — Phase 5)
- มีในแผนแล้ว §13 ของ `docs/PLAN.md` — PyInstaller onefile + UPX + icon (`assets/app.ico` ยังต้องสร้าง)
- PyInstaller 6.20.0 ติดตั้งแล้วบนเครื่องนี้ · **UPX ยังไม่ติดตั้ง** · ใช้ spec (`webtool.spec`) ไม่ใช่ flags ล้วน
- กับดักตอน frozen: templates/static ต้องอ้าง `sys._MEIPASS` (core/paths.py) · uvicorn ต้อง `--collect-all uvicorn` · UPX+port scanner = AV false positive เกือบ 100% (ทำ UPX optional)
