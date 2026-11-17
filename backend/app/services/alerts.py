from __future__ import annotations
import os, smtplib, urllib.request, urllib.parse
from email.mime.text import MIMEText
def notify(channel: str, destination: str, message: str) -> dict:
    """Real delivery when env configured; otherwise explicit not_configured (never faked)."""
    if channel=="email":
        host=os.getenv("SMTP_HOST")
        if not host: return {"sent":False,"reason":"SMTP not configured"}
        msg=MIMEText(message); msg["Subject"]="Price alert — Cheapest Product Finder"; msg["From"]=os.getenv("SMTP_USER",""); msg["To"]=destination
        with smtplib.SMTP(host, int(os.getenv("SMTP_PORT","587"))) as s:
            s.starttls(); 
            if os.getenv("SMTP_USER"): s.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD",""))
            s.send_message(msg); return {"sent":True}
    if channel=="telegram":
        tok=os.getenv("TELEGRAM_BOT_TOKEN")
        if not tok: return {"sent":False,"reason":"TELEGRAM_BOT_TOKEN not configured"}
        url=f"https://api.telegram.org/bot{tok}/sendMessage?"+urllib.parse.urlencode({"chat_id":destination,"text":message})
        urllib.request.urlopen(url, timeout=10); return {"sent":True}
    if channel=="whatsapp": return {"sent":False,"link":f"https://wa.me/{destination}?text="+urllib.parse.quote(message),"reason":"WhatsApp delivered as click-to-send link"}
    if channel=="whatsapp_official":
        # v3 policy: official WhatsApp Cloud API only for programmatic
        # sends. No credentials exist in this environment (BLOCKED).
        if not os.getenv("WHATSAPP_CLOUD_TOKEN"): return {"sent":False,"reason":"WhatsApp official Cloud API not configured (WHATSAPP_CLOUD_TOKEN)"}
        return {"sent":False,"reason":"WhatsApp Cloud API send path requires a configured phone-number id + template (owner setup)"}
    if channel=="webpush": return {"sent":False,"reason":"web push requires VAPID keys + browser subscription (env-gated)"}
    return {"sent":False,"reason":"unknown channel"}
