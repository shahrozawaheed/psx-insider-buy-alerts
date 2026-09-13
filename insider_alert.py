import os
import requests
import time
from datetime import datetime
from zoneinfo import ZoneInfo

API_URL = "https://beta-restapi.sarmaaya.pk/api/announcements/insider-transactions"
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

# ==================================================
# PAKISTAN DATE
# ==================================================

pakistan_time = datetime.now(ZoneInfo("Asia/Karachi"))

today = pakistan_time.strftime("%Y-%m-%d")
display_date = pakistan_time.strftime("%B %d, %Y")

print("PSX Insider Transactions Alert Bot Started")
print("Pakistan Date:", today)

# ==================================================
# GET TODAY'S INSIDER TRANSACTIONS
# ==================================================

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

print("Total transactions:", len(transactions))

# ==================================================
# FILTER BUY TRANSACTIONS
# ==================================================

buys = [
    t for t in transactions
    if str(t.get("action", "")).strip().lower() == "buy"
]

# ==================================================
# FILTER SELL TRANSACTIONS
# ==================================================

sells = [
    t for t in transactions
    if str(t.get("action", "")).strip().lower() == "sell"
]

print("BUY transactions:", len(buys))
print("SELL transactions:", len(sells))

# ==================================================
# CALCULATE TRANSACTION VALUE
# ==================================================

def calculate_transaction_value(quantity, rate):

    try:
        quantity_number = float(
            str(quantity).replace(",", "").strip()
        )

        rate_number = float(
            str(rate).replace(",", "").strip()
        )

        return quantity_number * rate_number

    except (ValueError, TypeError):

        return None


# ==================================================
# FORMAT TRANSACTION VALUE
# ==================================================

def format_transaction_value(value):

    if value is None:
        return "N/A"

    if value.is_integer():
        return f"Rs. {value:,.0f}"

    return f"Rs. {value:,.2f}"


# ==================================================
# BUILD DISCORD MESSAGE
# ==================================================

def build_message(title, transaction_list):

    message = (
        f"**{title}**\n"
        f"Date: {display_date}\n\n"
    )

    for i, t in enumerate(transaction_list, start=1):

        symbol = t.get(
            "symbol",
            "N/A"
        )

        name = str(
            t.get("name", "N/A")
        ).strip()

        position = t.get(
            "position",
            "N/A"
        )

        quantity = t.get(
            "quantity",
            0
        )

        rate = t.get(
            "rate",
            0
        )

        attachment = t.get(
            "attachment"
        )

        # Calculate transaction value
        transaction_value = calculate_transaction_value(
            quantity,
            rate
        )

        formatted_value = format_transaction_value(
            transaction_value
        )

        message += (
            f"**{i}. {symbol}**\n"
            f"👤 {name}\n"
            f"💼 {position}\n"
            f"📊 {quantity:,} shares @ Rs. {rate}\n"
            f"💰 Transaction Value: {formatted_value}\n"
        )

        if attachment:

            message += (
                f"📎 [PSX Document]({attachment})\n"
            )

        message += "\n"

    return message


# ==================================================
# SEND BUY MESSAGE
# ==================================================

if buys:

    buy_message = build_message(
        "PSX Insider Transactions [BUY]",
        buys
    )

    print(
        "Sending BUY transactions to Discord..."
    )

    discord_response = requests.post(
        WEBHOOK_URL,
        json={
            "content": buy_message,
            "flags": 4
        },
        timeout=30
    )

    discord_response.raise_for_status()

    print(
        f"Sent {len(buys)} BUY transaction(s) to Discord."
    )

else:

    print(
        f"No insider BUY transactions for {today}"
    )


# ==================================================
# WAIT 10 MINUTES BEFORE SELL MESSAGE
# ==================================================

if sells:

    print(
        "SELL transactions found."
    )

    print(
        "Waiting 10 minutes before sending SELL message..."
    )

    time.sleep(600)

    # ==================================================
    # SEND SELL MESSAGE
    # ==================================================

    sell_message = build_message(
        "PSX Insider Transactions [SELL]",
        sells
    )

    print(
        "Sending SELL transactions to Discord..."
    )

    discord_response = requests.post(
        WEBHOOK_URL,
        json={
            "content": sell_message,
            "flags": 4
        },
        timeout=30
    )

    discord_response.raise_for_status()

    print(
        f"Sent {len(sells)} SELL transaction(s) to Discord."
    )

else:

    print(
        f"No insider SELL transactions for {today}"
    )


# ==================================================
# FINISHED
# ==================================================

print("--------------------------------")
print(
    "PSX Insider Transactions Alert Bot Finished"
)
print("--------------------------------")
