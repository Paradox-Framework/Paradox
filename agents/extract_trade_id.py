import requests

def extract_trade_id(trade_api_url):
    try:
        trade_id = trade_api_url.rstrip('/').split('/')[-1]
        return trade_id if trade_id else None
    except Exception as e:
        print(f"Error extracting trade ID: {e}")
        return None

async def get_trade_details(trade_id):
    url = f"https://pro-api.solscan.io/v2.0/transaction/detail?tx={trade_id}"
    headers = {"token": os.getenv("SOLSCAN_API_KEY")}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("parsedInstruction")  # Adjust depending on response structure
    else:
        raise Exception(f"Failed to fetch trade details: {response.status_code}")

async def send_message(platform_api, message_text):
    try:
        response = platform_api.post_message(message_text)
        return {"status": "success", "link": response.get("permalink")}
    except Exception as e:
        raise Exception(f"Failed to post message: {e}")
