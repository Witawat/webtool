# PLAN.md — แผนพัฒนา (Implementation-Ready)

เว็บเครื่องมือเครือข่ายสไตล์ yougetsignal.com — **17 เครื่องมือ** + UI ไทย/EN + Bulk lookup (optional)
เอกสารนี้คือ single source of truth สำหรับการทำงาน — อ่านจบแล้วลงมือได้เลย

---

## 1. ภาพรวม + ขอบเขต

| # | กลุ่ม | เครื่องมือ | self-host | ทำเฟส |
|---|---|---|---|---|
| 1 | ตรวจสอบ | What Is My IP | ✅ | 1 |
| 2 | ตรวจสอบ | Port Checker | ✅ | 1 |
| 3 | ตรวจสอบ | Port Range Scanner | ✅ | 1 |
| 4 | ตรวจสอบ | Ping | ✅ | 1 |
| 5 | ตรวจสอบ | Traceroute | ✅ | 1 |
| 6 | DNS | DNS Lookup | ✅ | 1 |
| 7 | DNS | e-mail domain DNS analysis (MX/SPF/DKIM/DMARC) | ✅ | 1 |
| 8 | SSL | SSL/TLS Checker | ✅ | 1 |
| 9 | WHOIS | WHOIS Lookup (domain) | ✅ | 1 |
| 10 | WHOIS | ASN / IP WHOIS (RDAP) | ✅ | 1 |
| 11 | HTTP | Fetch (HTTP debugger) | ✅ | 1 |
| 12 | HTTP | HTTP Header Checker | ✅ | 1 |
| 13 | คำนวณ | Subnet/CIDR Calculator | ✅ | 1 |
| 14 | โทรศัพท์ | Phone Number Geolocator | ✅ (offline) | 1 |
| 15 | Reverse | Reverse IP Lookup | ❌ ภายนอก | 2 |
| 16 | GeoIP | Network Location (แผนที่) | ❌ ภายนอก | 2 |
| 17 | Reverse | Reverse E-mail Lookup (เต็ม) | ❌ ภายนอก | 3 |
| — | UI | ไทย/EN + dark/light + Bulk lookup | — | 4 |

**หลักการออกแบบ:** 14 ตัวแรกทำก่อน (self-host หมด) → ต่อยอดตัวพึ่ง API → premium ปิด default → polish

---

## 2. สแต็ก + dependencies

- Backend: **Python 3.12 + FastAPI + uvicorn** (async) · Frontend: **Jinja2 SSR + vanilla JS + CSS** (ไม่มี build step) · แผนที่: **Leaflet ผ่าน CDN**
- Config: `pydantic-settings` อ่าน `.env` · ไม่มี DB (stateless, คำนวณ real-time)

### requirements.txt (ติดตั้งเวอร์ชันล่าสุด ณ วันติดตั้ง; ทดสอบบน Python 3.12.10)
```
fastapi
uvicorn[standard]
jinja2
python-multipart        # สำรอง (ถ้าจะทำ form submit — §6 ตัดสินใจใช้ fetch ล้วน)
httpx
dnspython               # ใช้ dns.asyncresolver (native async)
python-whois            # WHOIS domain (blocking → ต้อง asyncio.to_thread)
icmplib                 # ping / traceroute (ต้องสิทธิ์ raw socket บางเครื่อง)
phonenumbers            # phone geolocator (offline)
cryptography            # แยก field cert ใน SSL checker
pydantic-settings       # .env

# สำรอง (ใช้เมื่อตั้ง key เท่านั้น)
geoip2                  # GeoLite2 (MaxMind) เมื่อตั้ง MAXMIND_KEY — §5.16

# dev
pytest
pytest-asyncio
ruff
pyinstaller             # (ติดตั้งแล้ว 6.20.0)
pillow                  # สร้าง assets/app.ico จาก PNG
```

---

## 3. โครงสร้างไฟล์ (สร้างให้ครบตามนี้)

```
webtool/
├── main.py                      # FastAPI: create_app(), mount routers, /healthz, exception handler
├── requirements.txt
├── pyproject.toml               # [tool.pytest] asyncio_mode + marker network · [tool.ruff] config · version
├── .env.example                 # MAXMIND_KEY=  HACKERTARGET_KEY=  EMAIL_API_KEY=
├── .gitignore                   # .env, .venv, dist/, build/, __pycache__, logs/
├── setup.bat                    # venv + pip install
├── run-dev.bat
├── build.bat
├── run-exe.bat
├── webtool.spec                 # PyInstaller (Phase 5)
│
├── core/
│   ├── __init__.py
│   ├── config.py                # Settings(pydantic-settings): ตัวเลข timeout/limit ทั้งหมด + คีย์
│   ├── paths.py                 # BASE_DIR = Path(getattr(sys,"_MEIPASS", __file__..parent)); templates/static/logs อ้างจากนี้
│   ├── validation.py            # parse_ip, parse_domain, parse_port, parse_url, validate_url_safe (SSRF), PORT_NAMES
│   ├── rate_limit.py            # RateLimiter (sliding window in-memory), get_client_ip()
│   ├── timeout.py               # async_with_timeout(coro, sec) → asyncio.wait_for wrapper
│   ├── errors.py                # AppError(code,message_key,status,field?) + ERROR_MESSAGES th/en
│   └── i18n.py                  # STRINGS{th,en}, t(lang,key,**fmt), all_strings(lang)
│
├── services/
│   ├── __init__.py
│   ├── port.py                  # check_port(), scan_ports()
│   ├── ping.py                  # icmplib wrapper + TCP fallback
│   ├── traceroute.py
│   ├── dns_lookup.py            # dns.asyncresolver wrapper
│   ├── ssl_checker.py
│   ├── whois.py                 # python-whois ใน asyncio.to_thread
│   ├── rdap_asn.py
│   ├── fetch_http.py            # ใช้ร่วมกับ header_checker (client ตัวเดียว)
│   ├── my_ip.py
│   ├── phone_geo.py
│   ├── subnet_calc.py           # pure, ไม่แตะ network
│   └── providers/               # abstraction API ภายนอก
│       ├── __init__.py
│       ├── geoip.py             # ip-api (http://) → MaxMind
│       ├── reverse_ip.py        # HackerTarget
│       └── email.py             # premium
│
├── routers/                     # 1 ไฟล์/เครื่องมือ: GET หน้า + POST /api/<slug>
│   ├── __init__.py
│   ├── home.py                  # GET /, GET /healthz
│   ├── port_checker.py  port_scan.py  ping.py  traceroute.py  dns_lookup.py
│   ├── email_dns.py   ssl_checker.py  whois.py  asn_rdap.py  fetch_http.py
│   ├── header_checker.py  my_ip.py  phone_geo.py  subnet_calc.py
│   ├── reverse_ip.py  network_location.py  email_lookup.py
│
├── templates/
│   ├── base.html                # nav + lang switch + theme + footer + blocks
│   ├── home.html                # grid การ์ด 17 เครื่องมือ
│   ├── tool.html                # base หน้าเครื่องมือ (H1+desc+form+result+about)
│   └── tools/<slug>.html        # 17 ไฟล์บาง: ฟอร์ม + about (extends tool.html)
│
├── static/
│   ├── css/style.css            # CSS variables สำหรับ dark/light
│   └── js/
│       ├── app.js               # api(slug,payload), I18N embed, lang/theme toggle, helpers
│       └── tools/<slug>.js      # 17 ไฟล์: renderResult(el, data) + form submit
│
├── assets/app.ico               # สร้าง Phase 5
├── tools/upx/upx.exe            # ดาวน์โหลด Phase 5
├── docs/
│   ├── PLAN.md  SESSION_STATE.md  ui-ref/*.png
└── tests/
    ├── conftest.py              # asyncio_mode=auto, register marker "network"
    ├── test_validation.py  test_i18n.py  test_rate_limit.py  test_errors.py
    ├── test_subnet_calc.py      # pure unit
    └── test_<slug>.py           # ต่อเครื่องมือ (network จริง → marker)
```

---

## 4. core infrastructure (สร้างก่อนเสมอ)

### 4.1 core/config.py — ค่าทั้งหมดอยู่ที่เดียว (table ใน PLAN = ค่าเริ่มต้น)
| ค่า | default | ใช้ที่ |
|---|---|---|
| `PORT_TIMEOUT_S` | 3.0 | port checker ต่อพอร์ต |
| `SCAN_PORT_TIMEOUT_S` | 1.5 | port scan ต่อพอร์ต |
| `SCAN_MAX_PORTS` | 100 | port scan |
| `SCAN_MAX_PARALLEL` | 20 | semaphore port scan |
| `PING_COUNT` / `PING_TIMEOUT_S` | 4 / 2.0 | ping |
| `TRACE_MAX_HOPS` / `TRACE_HOP_TIMEOUT_S` | 30 / 2.0 | traceroute |
| `DNS_TIMEOUT_S` | 5.0 | dnspython lifetime |
| `SSL_CONNECT_TIMEOUT_S` | 10.0 | ssl checker |
| `WHOIS_TIMEOUT_S` | 10.0 | whois |
| `HTTP_TIMEOUT_S` | 10.0 | fetch/header/rdap/reverse_ip |
| `HTTP_MAX_REDIRECTS` / `HTTP_MAX_BODY` | 5 / 1 MB | fetch/header |
| `GEOIP_TIMEOUT_S` | 5.0 | geoip |
| `TRUST_PROXY` | false | ถ้า true → get_client_ip อ่าน X-Forwarded-For (หลัง proxy ต้องรัน --proxy-headers --forwarded-allow-ips) |
| `GLOBAL_SEMAPHORE` | 50 | จำกัด outbound ทั้งหมด |

### 4.2 core/validation.py
- `parse_ip(s)` → `ipaddress.ip_address` (IPv4/IPv6) / `ValueError`
- `parse_domain(s)` → lowercase + `idna` encode + regex `^([a-z0-9-]+\.)+[a-z]{2,63}$` (ตัด trailing dot)
- `parse_host(s)` → domain **หรือ** IP (แล้วแต่เครื่องมือ)
- `parse_port(s)` → int 1–65535 (ห้าม 0)
- `parse_cidr(s)` → `ipaddress.ip_network(strict=False)`
- `validate_url_safe(url)` → **SSRF guard:** บังคับ scheme http/https, ตัด credentials, `urlsplit` → host → `parse_host` → resolve DNS → เช็คทุก IP ที่ resolve ได้ว่าไม่เป็น private/link-local/loopback/reserved/multicast (`ip.is_private` / `is_link_local` / `is_loopback` / `is_reserved` / `is_multicast`) → ถ้าโดน throw `AppError("SSRF_BLOCKED")`; ห้าม redirect ไป IP ต้องห้าม (เช็คซ้ำใน middleware/redirect loop)
- `PORT_NAMES` dict: `{21:"FTP",22:"SSH",23:"TELNET",25:"SMTP",53:"DNS",80:"HTTP",110:"POP3",115:"SFTP",135:"RPC",139:"NetBIOS",143:"IMAP",443:"HTTPS",445:"SMB",1433:"MSSQL",3306:"MySQL",3389:"RDP",5432:"PostgreSQL",5900:"VNC",6379:"Redis",8080:"HTTP-Alt",25565:"Minecraft"}`

### 4.3 core/errors.py — error model (เดียวตลอดระบบ)
`AppError(code, message_key, status=400, field=None, extra=None)`
| code | HTTP | ความหมาย |
|---|---|---|
| `INVALID_INPUT` | 400 | format ผิด (มี field ระบุ) |
| `SSRF_BLOCKED` | 400 | URL/host ติด internal |
| `NOT_FOUND` | 404 | resolve ไม่เจอ |
| `RATE_LIMITED` | 429 | เกิน rate limit |
| `UPSTREAM_ERROR` | 502 | provider/ภายนอกพัง |
| `TIMEOUT` | 504 | เกิน timeout |
| `TOOL_DISABLED` | 503 | ไม่มี key premium |
| `INTERNAL` | 500 | อื่นๆ (log เท่านั้น) |

### 4.4 core/rate_limit.py
- `RateLimiter` in-memory sliding window: `allow(ip, key, limit_per_min) -> bool`
- `get_client_ip(request)` → ใช้ `request.client.host`; ถ้า `config.TRUST_PROXY` → อ่าน `X-Forwarded-For` ซ้ายสุด
- ใช้ middleware/Depends `require_rate(limit)` ต่อ router ของแต่ละเครื่องมือ
- ⚠️ in-memory ไม่แชร์ข้าม worker → dev ใช้ 1 worker; สเกลหลาย worker ค่อยย้าย Redis

### 4.5 core/i18n.py
- `STRINGS = {"th": {...}, "en": {...}}` — dict กลาง; key ระบบ namespace เช่น `tool.port_checker.name`, `result.open`, `err.invalid_input`, `common.check`, `nav.home`, `ui.about`
- `t(lang, key, **fmt)` → `.format(**fmt)`; ถ้า key หาย → คืน key เอง (เห็นตอน dev)
- lang จาก cookie `lang` → query `?lang=` ชนะ cookie; default `th`
- Jinja: `@app.context_processor` ใส่ `t=t, lang=lang` ให้ทุก template; JS: `base.html` ฝัง `<script>window.I18N = {{ all_strings(lang) | tojson }}</script>`
- หลัก: **แปลเต็มทุกหน้า** (เว็บจริงแปลไม่ครบ — เราเหนือกว่า)

---

## 5. เครื่องมือ 17 — API contract, schema, params (แม่แบบสำหรับการทำทั้งหมด)

> ทุกตัว: `POST /api/<slug>` รับ JSON, คืน `{ok:true, data, duration_ms}` หรือ `{ok:false, error:{code, message, field?}}`
> ทุกตัวมี rate limit + timeout (จาก §4.1/§4.3) · input ผ่าน core/validation เสมอ

### 5.1 What Is My IP — `POST /api/my-ip` (ไม่ต้อง input)
```json
{ok:true, data:{ip:"171.5.12.194", version:4, hostname:"...", geo:{city,region,country,country_code,lat,lon,isp,asn}?}, duration_ms:5}
```
geo ใช้ provider geoip (ถ้าไม่มี key/callable → null) · rate 60/min

### 5.2 Port Checker — `{host, port}`
```json
{ok:true, data:{host, ip:"142.250.190.78", port:80, service:"HTTP", state:"open|filtered|closed", latency_ms:21}, duration_ms:21}
```
state: `open`=connect สำเร็จ / `filtered`=timeout / `closed`=refused · ใช้ `asyncio.open_connection` + `async_with_timeout(PORT_TIMEOUT_S)` · rate 10/min

### 5.3 Port Range Scanner — `{ip, start_port, end_port}` (≤ SCAN_MAX_PORTS)
```json
{ok:true, data:{ip, scanned:100, open_ports:[{port:80, service:"HTTP", latency_ms:21}, ...], closed:95}, duration_ms:1234}
```
**ข้อจำกัด:** รับ **IP เดี่ยวเท่านั้น** (ไม่รับ domain) · `Semaphore(SCAN_MAX_PARALLEL)` + `gather` · rate 3/min

### 5.4 Ping — `{host, count?=4}`
```json
{ok:true, data:{host, ip, sent:4, received:4, loss_pct:0, rtt_ms:{min,avg,max}, alive:true, icmp:true}, duration_ms:...}
```
ใช้ `icmplib.async_ping`; ถ้า ICMP ถูกบล็อก (alive=False แต่ TCP ตอบ) → fallback TCP ping ที่พอร์ต 80/443 แล้ว `icmp:false` · rate 10/min

### 5.5 Traceroute — `{host, max_hops?=30}`
```json
{ok:true, data:{host, ip, hops:[{ttl:1, ip, hostname, rtt_ms:[1.2,1.3,1.4], timed_out:false}, ...]}, duration_ms:...}
```
`icmplib.async_traceroute` · timeout/hop 2s · ต้องสิทธิ์ raw socket (ดู §9) · rate 3/min

### 5.6 DNS Lookup — `{domain, types?=["A","AAAA","CNAME","MX","NS","TXT","SOA","SRV","CAA"]}`
```json
{ok:true, data:{domain, records:[{type:"A", name:"example.com", ttl:3600, value:"93.184.216.34"}, {type:"MX", name, ttl, value:"10 mail.example.com"}, ...], reverse?:"..."}, duration_ms:...}
```
`dns.asyncresolver.resolve(name, rdtype, lifetime=DNS_TIMEOUT_S)`; TXT → value เป็น list · PTR แยก: `resolve_address(ip)` · rate 30/min

### 5.7 e-mail domain DNS analysis — `{domain}`
```json
{ok:true, data:{domain, mx:[{priority, host}], spf:{present, pass, record}, dkim:{present, pass, records:[{selector, record}]}, dmarc:{present, pass, record}, summary:"pass|warn|fail"}, duration_ms:...}
```
อ่าน DNS: MX record / TXT `v=spf1` / `_dmarc.<domain>` TXT / `default._domainkey` (+ ลอง `google._domainkey`, `selector1._domainkey` เป็นต้น) · summary: pass=ครบ / warn=ขาดบาง / fail=ขัดกัน · rate 30/min

### 5.8 SSL/TLS Checker — `{host, port?=443}`
```json
{ok:true, data:{host, ip, port, connected:true, valid:true, protocol:"TLSv1.3", cipher:"TLS_AES_128_GCM_SHA256", cert:{subject_cn, sans:[], issuer, valid_from, valid_to, days_left, serial, sig_algo}, warnings:["expires_soon"]}, duration_ms:...}
```
`asyncio.open_connection(host, port, ssl=ctx, server_hostname=host)` (SNI สำคัญ!) · `ssl` module + `cryptography` แยก field cert · warnings: `expires_soon`(<30d), `expired`(<0), `self_signed`, `hostname_mismatch` · rate 10/min

### 5.9 WHOIS Lookup — `{domain}`
```json
{ok:true, data:{domain, registrar, created, updated, expires, status:[], nameservers:[], raw_text, tld_privacy:false}, duration_ms:...}
```
`python-whois` **ใน `asyncio.to_thread`** (blocking!) + timeout · domain เป็นหลัก (IP → ใช้ข้อ 10) · บาง TLD privacy → `tld_privacy:true` · rate 10/min

### 5.10 ASN / IP WHOIS — `{ip}` หรือ `{asn}`
```json
{ok:true, data:{ip, handle, name, type:"IP Network", start_address, end_address, cidr, country, asn:{number, name}, org:{handle, name}, source:"rdap.org"}, duration_ms:...}
```
`httpx.AsyncClient(follow_redirects=True)` → `https://rdap.org/ip/<ip>` / `https://rdap.org/autnum/<asn>` (301 → RIR ARIN/APNIC/RIPE/...) · ไม่ต้อง key · rate 20/min

### 5.11 Fetch — `{method, url, headers?, body?, follow_redirects?}`
```json
{ok:true, data:{method, url, final_url, status, reason, headers:{}, body, body_truncated:true, size_bytes, time_ms, redirects:["url", ...]}, duration_ms:...}
```
`httpx.AsyncClient(timeout=HTTP_TIMEOUT_S, follow_redirects=..., max_redirects=HTTP_MAX_REDIRECTS, limits=...)` · **SSRF guard ก่อนส่งทุกครั้ง (รวม redirect)** · ตัด body ที่ HTTP_MAX_BODY · rate 10/min

### 5.12 HTTP Header Checker — `{url}`
```json
{ok:true, data:{url, status, headers:{}, security:{hsts:{present,value}, csp:{present}, x_frame_options, x_content_type_options, referrer_policy, permissions_policy}, score:3}, duration_ms:...}
```
GET/HEAD + วิเคราะห์ security headers (แต่ละ header → present/missing) · score 0–6 (มีกี่ตัว) · แชร์ client กับ Fetch · SSRF guard · rate 10/min

### 5.13 Subnet/CIDR Calculator — `{cidr}`
```json
{ok:true, data:{cidr:"192.168.1.0/24", network, broadcast, netmask, wildcard, first_host, last_host, usable_hosts:254, total_hosts:256, prefix:24, ip_version:4}, duration_ms:0}
```
`ipaddress` pure · **ไม่แตะ network** → rate สูง 60/min, ไม่ต้อง timeout

### 5.14 Phone Number Geolocator — `{number, country?}`
```json
{ok:true, data:{number, valid:true, e164:"+16692226000", country:"US", region:"California", carrier:"AT&T", timezones:["America/Los_Angeles"], number_type:"MOBILE"}, duration_ms:...}
```
`phonenumbers` offline: `parse` → `is_valid_number` → `geocoder.description_for_number` / `carrier.name_for_number` / `timezone.time_zones_for_number` / `number_type` · ถ้าไม่ valid → `{valid:false}` (ยัง ok:true) · rate 20/min

### 5.15 Reverse IP Lookup — `{ip}` (external)
```json
{ok:true, data:{ip, domains:["a.com","b.net"], count:2, provider:"HackerTarget"}, duration_ms:...}
```
`GET https://api.hackertarget.com/reverseiplookup/?q=<ip>` → คืน **ข้อความล้วน** (บรรทัดละ domain, ขึ้นต้น `error`/`API count exceeded` = UPSTREAM_ERROR) · rate 3/min (กันโดนแบน provider) · `HACKERTARGET_KEY` **ไม่บังคับ** (ฟรี tier ใช้ได้เลย แต่จำกัดอัตรา); ถ้าตั้ง key ใน .env → append `&key=<key>` · แสดง provider ในหน้า

### 5.16 Network Location — `{ip_or_domain}` (external)
```json
{ok:true, data:{query, ip, city, region, country, country_code, lat, lon, isp, org, asn, provider:"ip-api.com"}, duration_ms:...}
```
default: **`http://ip-api.com/json/<ip>?fields=...`** — ⚠️ ฟรี tier เป็น **HTTP เท่านั้น** (HTTPS ต้องเสียเงิน) → ใช้ http + timeout · rate 10/min (สำรองเผื่อ 45/min ของ provider) · ถ้าเซ็ต `MAXMIND_KEY` → ใช้ GeoLite2 ผ่าน `geoip2` แทน (ชี้ใน config) · หน้าแสดงผลบนแผนที่ Leaflet

### 5.17 Reverse E-mail Lookup — `{email}` (premium, ปิด default)
```json
{ok:true, data:{email, provider:"...", available:true, result:null}, duration_ms:...}
```
ต้องการ `EMAIL_API_KEY` (provider เสียเงิน) → ถ้าไม่มี key คืน `TOOL_DISABLED` + หน้าแสดง "ต้องตั้ง key" · Tier-1 (ฟรี) ที่ทำได้ก่อนคือข้อ 5.7 · rate 3/min

---

## 6. API + error model (สรุป)
- `GET /` หน้าแรก grid · `GET /healthz` → `{status:"ok"}` · `GET /tools/<slug>` หน้า SSR · `POST /api/<slug>` JSON
- Response สำเร็จ: `{ok:true, data, duration_ms}` · Error: `{ok:false, error:{code, message, field?}}` (message แปลตามภาษา)
- ทุก `POST /api/*` ถูก rate limit ตามตาราง §5 + ผ่าน timeout
- content-type: `application/json` ทั้ง request/response (frontend ใช้ fetch + JSON ไม่ต้อง python-multipart ยกเว้นจะทำ <form> submit — ตัดสินใจ: **ใช้ fetch เท่านั้น** → ตัด python-multipart ได้ แต่เก็บไว้แผนสำรอง)

---

## 7. Frontend architecture

### 7.1 ไฟล์
- `base.html`: `<head>` + nav (logo, lang button, theme toggle) + `{% block content %}` + footer + `<script src=/static/js/app.js>`; ฝัง `window.I18N` + `window.LANG`
- `tool.html` (extends base): H1 + desc + `<form id=tool-form>` (block `form_fields`) + `<button>{% t('common.check') %}</button>` + `<div id=result>` + `<div class=about>` (block `about`) + `<script src=/static/js/tools/<slug>.js>`
- `tools/<slug>.html`: กำหนด form fields + about เท่านั้น (โค้ด JS อยู่ใน static/js/tools/)

### 7.2 app.js (shared)
- `api(slug, payload)` → `fetch('/api/'+slug, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)})` → ตรวจ res.ok; ถ้า 429/504/503 → `showError(el, err)`
- `showError(el, err)` → ใส่ `<div class="alert-error">I18N['err.'+err.code]</div>`
- `showLoading(el)` → button disabled + `<div class="loading">I18N['ui.loading']…</div>`
- `langSwitch(lang)` → set cookie + reload
- `themeToggle()` → toggle `data-theme` + cookie
- helper: `fmtDuration(ms)`, `esc(s)` (escape HTML ก่อน render ทุกค่า)

### 7.3 per-tool JS (17 ไฟล์)
- แต่ละไฟล์: `document.getElementById('tool-form').onsubmit = async e => { e.preventDefault(); showLoading(); try { const res = await api('<slug>', readForm()); renderResult(document.getElementById('result'), res.data); } catch(err){ showError(...) } }`
- `renderResult(el, data)` ต่อเครื่องมือ: ใช้ `esc()` ทุกค่า, ปุ่มลัด (Common Ports) เติม input
- **i18n ใน JS:** ใช้ `window.I18N` เท่านั้น ไม่มี string แข็งใน JS

### 7.4 ธีม
- CSS variables: `--bg, --fg, --card, --border, --accent, --ok(#16a34a), --warn(#d97706), --err(#dc2626)` + `[data-theme=dark]` override
- badge สถานะ: `.badge-ok` (เขียว) / `.badge-warn` (เหลือง) / `.badge-err` (แดง)

---

## 8. UI/UX (อิงจากการลองใช้เว็บจริง 2026 — ภาพใน docs/ui-ref/)
สังเกตจาก https://www.yougetsignal.com/th และ /tools/open-ports: nav บน + H1 + grid การ์ด (h3+desc) · ปุ่มสลับภาษา "ไทย/English" + dark/light · ผลลัพธ์แสดง**ในหน้าเดิม (AJAX)** เป็นประโยค + badge สี (open=เขียว/filtered=เหลือง/closed=แดง) · quick-select "Common Ports" · ส่วน About ใต้ฟอร์ม · ของจริง**แปลไทยไม่ครบ** (Reverse IP/Fetch/E-mail/Phone ยังอังกฤษ) → เราจะแปลเต็ม

แบบแผนต่อเครื่องมือ (เลียนแบบ + ปรับ):
- ฟอร์ม: input เด่น + ปุ่ม Check (กด Enter ได้) + placeholder ตัวอย่าง (google.com / 80) + ปุ่มลัด (Common Ports ใน Port Checker)
- โหลด: ข้อความ "...กำลังตรวจสอบ" + button disabled
- ผลสั้น (Port/My IP): ประโยคสรุป + badge สี ตาม §7.4
- รายการ (DNS/Traceroute/Scan): ตารางหัวคอลัมน์
- คีย์-ค่า (WHOIS/SSL/GeoIP): การ์ดแยกหัวข้อ · SSL: banner เตือนเมื่อ expires_soon/expired
- JSON (Fetch): หัวข้อ status/headers/body แยก + collapsible + ตัด body
- error: banner ในหน้า (localized) · แสดง `duration_ms` ใต้ผลเสมอ
- external: ข้อความเล็ก "Data: <provider> (ฟรี จำกัดอัตรา)"

---

## 9. Gotchas / security (บังคับทุกข้อ)
- งาน network ต้องรันฝั่ง server (browser เปิด raw TCP/WHOIS ไม่ได้ + CORS)
- **SSRF guard** (validation.validate_url_safe) ใช้กับ fetch/header/reverse_ip/network_location — รวมเช็ค redirect
- **ทุก endpoint timeout + semaphore** — traceroute/scan/fetch ค้างได้นาน
- **Port scan:** IP เดี่ยวเท่านั้น ≤100 พอร์ต, timeout สั้น, rate 3/min — หน้าตาเหมือนเครื่องมือโจมตี
- **blocking lib:** `python-whois` ต้อง `asyncio.to_thread` · `dns.asyncresolver` ใช้ async ตรง ไม่ต้อง thread
- อย่าใช้ subprocess/shell สำหรับงาน network (เลี่ยง command injection)
- **client IP หลัง proxy:** ต้อง `uvicorn --proxy-headers --forwarded-allow-ips=<proxy_ip>` ไม่งั้น my-ip + rate limit ผิด
- **rate limit in-memory ไม่แชร์ข้าม worker** → dev 1 worker; หลาย worker = Redis (ไม่ใช่ v1)
- **ping/traceroute ต้องสิทธิ์ raw socket:** Linux `setcap cap_net_raw+ep` / Windows admin บางกรณี; มี TCP fallback
- **ip-api ฟรี = HTTP เท่านั้น** (HTTPS เสียเงิน) — ใช้ http + timeout
- คีย์ API ใน `.env` เท่านั้น ไม่ commit · อย่า log body/คีย์
- error shape เดียวตลอดระบบ (core/errors.py)

---

## 10. Testing (pytest)
- `tests/conftest.py`: `asyncio_mode=auto`; ลง marker `network` ใน pyproject.toml
- Unit (ไม่แตะ network): test_validation (รวม SSRF guard), test_i18n, test_rate_limit, test_errors, test_subnet_calc
- Integration (network จริง): test_<slug>.py ใช้ `@pytest.mark.network` → default **ข้าม** (`pytest -m "not network"`)
- external API: **mock** provider ใน test (ไม่ยิงจริง)
- วิธี test API โดยไม่เปิด server: `httpx.AsyncClient(transport=ASGITransport(app=app))`
- lint: `ruff check .`

---

## 11. เฟสการพัฒนา + Definition of Done

> **ติดตามสถานะด้วย `docs/CHECKLIST.md`** — ขีด ✓ ทุกขั้นที่ทำเสร็จจริง (มีรายการต่อเฟส + ต่อเครื่องมือครบ)

### Phase 0 — โครง (ทำก่อนทุกอย่าง)
**สร้าง:** main.py, core/ ทั้ง 7 ไฟล์, templates/base.html+home.html, static/css/style.css, static/js/app.js, pyproject.toml, .gitignore, .env.example, requirements.txt, setup.bat, run-dev.bat
**DoD:** `run-dev.bat` เปิดแล้วหน้าแรก grid 17 การ์ดโหลดได้ · สลับไทย/EN + dark/light ใช้ได้ · /healthz ตอบ 200 · validation/errors/rate_limit/i18n มี unit test ผ่าน

### Phase 1 — 14 self-host (ทีละตัว ตามลำดับ)
**ต่อเครื่องมือ:** services/<slug>.py + routers/<slug>.py + templates/tools/<slug>.html + static/js/tools/<slug>.js + tests/test_<slug>.py
**ลำดับ:** my-ip → port-checker → dns → subnet-calc (ง่ายก่อน) → port-scan → ping → traceroute → ssl → whois → asn-rdap → fetch → header → phone → email-dns
**DoD (ต่อตัว):** POST /api/<slug> คืน JSON ตาม schema §5 · หน้าแสดงผลถูกต้อง · rate limit + timeout ทำงาน (ยิงซ้ำโดน 429) · unit test ผ่าน
**จบเฟส:** 14 ตัวครบ, `pytest -m "not network"` ผ่านทั้งหมด

### Phase 2 — external (reverse_ip, network_location)
**DoD:** provider abstraction ทำงาน + หน้าแจ้ง provider · mock test ผ่าน · ip-api http ใช้งานได้จริง

### Phase 3 — premium (reverse_email)
**DoD:** ไม่มี key → หน้าแสดง "ต้องตั้ง key" + API คืน TOOL_DISABLED (503) · มี key → ทำงาน

### Phase 4 — polish
**สร้าง:** Bulk lookup (wrapper รับหลายค่า ใช้ validation+rate limit เดิม), about/disclaimer, error/empty states, README, CHANGELOG.md (เริ่ม section v0.1.0 — release ใช้ย่อจากนี้), แปลไทยเต็ม
**DoD:** `pytest -m "not network"` + `ruff check .` ผ่าน · ทุกหน้า/ทุกข้อความแปลครบ th/en

### Phase 5 — packaging (exe)
**สร้าง:** assets/app.ico (Pillow จาก PNG), ดาวน์โหลด upx → tools/upx/, webtool.spec, build.bat, run-exe.bat
**DoD:** `build.bat` → dist\webtool.exe รันได้, เปิดเบราว์เซอร์อัตโนมัติ, icon ติดถูก, smoke test ผ่าน (รายละเอียด §13)

---

## 12. สคริปต์ .bat (Windows)
| ไฟล์ | เนื้อหาหลัก |
|---|---|
| `setup.bat` | `python -m venv .venv` + `.venv\Scripts\pip install -r requirements.txt` |
| `run-dev.bat` | `.venv\Scripts\python -m uvicorn main:app --reload` |
| `build.bat` | `if "%UPX_DIR%"=="" set UPX_DIR=tools\upx` + `.venv\Scripts\pyinstaller webtool.spec` |
| `run-exe.bat` | `dist\webtool.exe --port 8000` |

เหตุผลที่ต้องมี: Windows ไม่มี venv PATH หลัง cd; user ดับเบิลคลิกได้; build.bat ตั้ง UPX_DIR (ไม่มี upx → spec ข้ามบีบ ไม่พัง)

---

## 13. Packaging exe (Phase 5)
- exe = local server: รัน uvicorn บน `127.0.0.1:<port>` + เปิดเบราว์เซอร์อัตโนมัติ · args `--port` `--no-browser` `--headless`
- PyInstaller 6.20.0 (มีแล้ว) · **UPX ยังไม่ติดตั้ง** · **app.ico ยังไม่มี**
- webtool.spec ต้องมี: `--onefile`, `--icon=assets/app.ico`, `--upx-dir` (optional), `--add-data "templates;templates" --add-data "static;static"` (Windows คั่น `;`), `--collect-all uvicorn` (import dynamic loops/protocols), `--collect-all cryptography`, hidden-import `python_multipart`
- **Path ตอน frozen:** templates/static/logs อ้าง `core/paths.BASE_DIR` = `getattr(sys,"_MEIPASS", parent)` — ต้องใช้ผ่าน paths.py เท่านั้น
- รัน uvicorn ผ่านโค้ด (`uvicorn.run(app, host="127.0.0.1", ...)`) ไม่ใช้ CLI
- **UPX + port scanner = AV false positive เกือบ 100%** → UPX optional (env `UPX=1`), แนะนำ code-signing; ถ้าถูกฟลากหนัก → ใช้ onedir
- firewall prompt ตอน bind → bind loopback เท่านั้น; `--noconsole` → redirect log ไป `logs\app.log`
- onefile startup ช้า (~1-3s) — ยอมรับได้ v1

---

## 14. Git + GitHub workflow
- สถานะปัจจุบัน: `git init` สด (branch `master`), ยังไม่มี commit/remote · ชื่อผู้พัฒนา (git user): **Maker Witawat <witawat57@gmail.com>** (ตั้งใน config แล้ว) · บัญชี GitHub: **Witawat** (`gh auth` active) — **สร้าง repo ใต้ `Witawat`**
- **สร้าง repo GitHub** (ทำหลัง Phase 0 เสร็จ — commit แรกเสร็จก่อน push):
  ```
  git add -A
  git commit -m "chore: scaffold project skeleton (Phase 0)"
  gh repo create Witawat/webtool --public --source . --remote origin --push
  ```
  (เปลี่ยน `--public` เป็น `--private` ได้ตามใจ)
- **Commit convention:** `feat(scope): ...` / `fix(scope): ...` / `chore: ...` / `docs: ...` / `refactor: ...` — เช่น `feat(port-checker): add scan service`, `docs: update PLAN` — commit ย่อยบ่อย ๆ ทำงานบน master ตรง
- **ก่อน commit แรก ตรวจ `.gitignore` ครบ:** `.env`, `.venv/`, `dist/`, `build/`, `__pycache__/`, `logs/`, `*.pyc` — ห้าม commit secret
- ขั้นตอน commit: ตรวจ `git status` + `git diff` ก่อนเสมอ, stage เฉพาะไฟล์ที่ตั้งใจ
- **Version/tag:** semver `v0.1.0`, `v1.0.0` … — ต้องตรงกับ `__version__` ในโค้ด (core/config.py)

## 15. Release (รีรีส) — หลัง Phase 5 (มี exe)
- เครื่องมือ: `gh` (auth แล้ว) + release-notes skill (`templates/release-notes.md`) + `tools/release-notes-patch.py`
- **ครั้งแรก ต้องสร้าง `tools/release-notes-patch.py` ในโปรเจกต์นี้:** คัดลอกจากต้นแบบที่มีอยู่ (เช่น `D:\MyCode\Cloudflare\tools\release-notes-patch.py`) → ปรับ `DEFAULT_REPO=Witawat/webtool` → commit — ใช้กับ release นี้และครั้งถัดไป (ห้ามไปเรียกจากโปรเจกต์อื่นตอนรัน)
- ขั้นตอน (ตาม skill):
  1. รวบรวม: อ่าน CHANGELOG.md (section เวอร์ชันนั้น) / `git log` ระหว่าง tag เก่า-ใหม่
  2. เขียน notes `.md` ตาม template — **ใช้ write tool/Python UTF-8 เท่านั้น** (ห้าม Set-Content กับไฟล์มีไทย)
  3. สร้าง: `gh release create v<tag> --repo Witawat/webtool --title "<โปรเจกต์> v<tag>" --notes-file <notes.md> dist\webtool.exe`
  4. อัปเดต SHA256 + PATCH body: `.venv\Scripts\python tools\release-notes-patch.py v<tag> <notes.md> --repo Witawat/webtool` (กัน mojibake ไทย + เขียน `<notes>.checked`)
  5. ตรวจไทยใน `<notes>.checked` ด้วย **read tool — ห้ามผ่าน PowerShell pipeline**
- **กับดัก:** `gh release edit --notes-file` กับไฟล์ไทยบน Windows นี้ = mojibake (gh อ่านไฟล์เป็น cp874) → ใช้ PATCH ผ่าน Python เสมอ
- tag ซ้ำ → ลบก่อน: `gh release delete <tag>` + `git push origin --delete <tag>`
- ทุก release ต้องมี CHANGELOG.md (สร้างใน Phase 4) + notes มีหัวข้อตาม template (✨/🔧/⚠️/📥/✅ + SHA256)

## 16. คำสั่งรวม (สรุป)
| งาน | คำสั่ง |
|---|---|
| ตั้งค่าแรก | `setup.bat` |
| รัน dev | `run-dev.bat` หรือ `.venv\Scripts\python -m uvicorn main:app --reload` |
| รัน dev หลัง proxy | `... uvicorn main:app --proxy-headers --forwarded-allow-ips=127.0.0.1` |
| test (ไม่แตะ network) | `pytest -m "not network"` |
| test ทั้งหมด | `pytest` |
| lint | `ruff check .` |
| build exe | `build.bat` |
| รัน exe | `run-exe.bat` |
| สร้าง repo GitHub | `gh repo create Witawat/webtool --source . --remote origin --push` (หลัง commit แรก) |
| release | ดู §15 — `gh release create` + `tools/release-notes-patch.py` |
