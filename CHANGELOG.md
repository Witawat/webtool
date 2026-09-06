# Changelog

## v0.1.0 (2026-09-06)

✨ **ฟีเจอร์ใหม่**
- 17 เครื่องมือครบ: my-ip, port-checker, port-scan, ping, traceroute, dns, email-dns, ssl, whois, asn-rdap, fetch, header, subnet-calc, phone, reverse-ip, network-location, email-lookup
- UI ไทย/EN (default ไทย) + dark/light theme
- Bulk lookup (รองรับ 10 เครื่องมือ)
- หน้า About / Disclaimer
- หน้าแรกแบบ grid การ์ด 17 เครื่องมือ

🔧 **ปรับปรุง**
- ผลลัพธ์แสดงในหน้า (AJAX, ไม่ reload) พร้อม badge สีและเวลา
- SSRF guard ใน fetch / header / reverse-ip / network-location
- rate limit + timeout ทุก endpoint

⚠️ **หมายเหตุ**
- reverse-ip / network-location / email-lookup ใช้ API ภายนอก (HackerTarget / ip-api.com) — ระบุ provider ในแต่ละหน้า
- email-lookup เป็น premium ต้องตั้ง `EMAIL_API_KEY` ใน `.env` ถึงจะทำงาน (ไม่มี key → 503)

📥 **การติดตั้ง**
- `setup.bat` สร้าง `.venv` + ติดตั้ง dependencies · `run-dev.bat` รัน dev server
