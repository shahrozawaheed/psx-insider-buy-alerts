import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

API_URL = "https://beta-restapi.sarmaaya.pk/api/announcements/insider-transactions"
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

# Pakistan date
today = datetime.now(ZoneInfo("Asia/Karachi")).strftime("%Y-%m-%d")
display_date = datetime.now(ZoneInfo("Asia/Karachi")).strftime("%B %d, %Y")

# Get today's insider transactions
response = requests.get(
    API_URL,
    params={
        "from": today,
        "to": today
    },
    timeout=30
)

response.raise_for_status()
data = response.json()

transactions = data.get("response", [])

# Only BUY transactions
buys = [
    t for t in transactions
    if str(t.get("action", "")).strip().lower() == "buy"
]

# Don't send anything if there are no BUY transactions
if not buys:
    print(f"No insider BUY transactions for {today}")
    exit(0)

# Build Discord message
message = f"**PSX Insider Transactions BUY**\nDate: {display_date}\n\n"

for i, t in enumerate(buys, start=1):
    symbol = t.get("symbol", "N/A")
    name = str(t.get("name", "N/A")).strip()
    position = t.get("position", "N/A")
    quantity = t.get("quantity", 0)
    rate = t.get("rate", 0)
    attachment = t.get("attachment")

    message += (
        f"**{i}. {symbol}**\n"
        f"👤 {name}\n"
        f"💼 {position}\n"
        f"📊 {quantity:,} shares @ Rs. {rate}\n"
    )

    if attachment:
        message += f"📎 [PSX Document]({attachment})\n"

    message += "\n"

# Send Discord message
discord_response = requests.post(
    WEBHOOK_URL,
    json={
        "content": message,
        "flags": 4
    },
    timeout=30
)

discord_response.raise_for_status()

print(f"Sent {len(buys)} BUY transaction(s) to Discord.")
