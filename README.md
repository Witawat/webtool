# WebTool

เว็บเครื่องมือเครือข่ายฟรีสไตล์ [yougetsignal.com](https://www.yougetsignal.com/th) — **17 เครื่องมือ** + UI ไทย/EN (default ไทย) + dark/light theme + Bulk lookup

ทุกเครื่องมือคำนวณแบบเรียลไทม์บนเซิร์ฟเวอร์ ไม่มีการเก็บข้อมูลของคุณ

## คุณสมบัติ

- **ตรวจสอบ**: What Is My IP · Port Checker · Port Range Scanner · Ping · Traceroute
- **DNS**: DNS Lookup · E-mail Domain DNS (MX/SPF/DKIM/DMARC)
- **SSL**: SSL/TLS Checker
- **WHOIS**: WHOIS Lookup · ASN / IP WHOIS (RDAP)
- **HTTP**: Fetch (HTTP debugger) · HTTP Header Checker (คะแนนความปลอดภัย)
- **คำนวณ**: Subnet/CIDR Calculator
- **โทรศัพท์**: Phone Number Geolocator (offline)
- **Reverse**: Reverse IP Lookup (HackerTarget) · Network Location + แผนที่ (ip-api.com) · Reverse E-mail Lookup (ต้องตั้งค่า API key)
- **Bulk Lookup**: ตรวจหลายค่าพร้อมกันใน 10 เครื่องมือที่รองรับ

## สแต็ก

- Python 3.12 + FastAPI + uvicorn (async)
- Jinja2 SSR + vanilla JS (ไม่มี build step) · Leaflet map ผ่าน CDN
- อ่านค่า config จาก `.env` (คัดลอกจาก `.env.example`)

## เริ่มต้นใช้งาน

```bat
setup.bat       :: สร้าง .venv + ติดตั้ง dependencies
run-dev.bat     :: รัน dev server (uvicorn main:app --reload)
```

แล้วเปิด `http://127.0.0.1:8000`

## ทดสอบ / Lint

```bat
.venv\Scripts\python -m pytest -m "not network"   :: unit tests (ข้าม network จริง)
.venv\Scripts\python -m pytest -m network          :: tests ที่แตะ network จริง
.venv\Scripts\python -m ruff check .               :: lint
```

## โครงสร้าง

```
main.py          FastAPI app (create_app + auto-discover routers)
core/            config · validation (รวม SSRF guard) · rate_limit · errors · i18n · paths · timeout
services/        ตรรกะต่อเครื่องมือ + providers/ (API ภายนอก)
routers/         1 ไฟล์ต่อเครื่องมือ (GET หน้า + POST /api/<slug>)
templates/       Jinja2 (base/home/tool + tools/<slug>)
static/          CSS + JS (app.js shared + tools/<slug>.js)
tests/           pytest
docs/            PLAN.md · CHECKLIST.md · SESSION_STATE.md · ui-ref/
```

## หมายเหตุ

- งาน network ทั้งหมดรันฝั่งเซิร์ฟเวอร์ (browser เปิด raw TCP/WHOIS ไม่ได้)
- เครื่องมือที่พึ่ง API ภายนอกจะระบุ provider ในหน้าให้เห็นชัดเจน
- Port scan จำกัด IP เดี่ยว ≤100 พอร์ต · ทุก endpoint มี timeout + rate limit

## License

MIT
