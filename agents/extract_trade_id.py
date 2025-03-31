import os
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("paradox-trade")

def extract_trade_id(trade_api_url):
    try:
        trade_id = trade_api_url.rstrip('/').split('/')[-1]
        if not trade_id or len(trade_id) < 20:
            logger.warning(f"Extracted trade ID '{trade_id}' appears invalid.")
            return None
        return trade_id
    except Exception as e:
        logger.error(f"Error extracting trade ID: {e}")
        return None

async def get_trade_details(trade_id):
    if not trade_id:
        raise ValueError("No trade ID provided.")

    url = f"https://pro-api.solscan.io/v2.0/transaction/detail?tx={trade_id}"
    headers = {"token": os.getenv("SOLSCAN_API_KEY")}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raises HTTPError for bad status codes
        data = response.json()

        if "parsedInstruction" in data:
            return data["parsedInstruction"]
        else:
            logger.warning(f"'parsedInstruction' not found in response for trade ID: {trade_id}")
            return data  # Return full response for debugging fallback
    except requests.exceptions.Timeout:
        logger.error("Request timed out when contacting Solscan API.")
        raise
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error from Solscan API: {http_err}")
        raise
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request exception: {req_err}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching trade details: {e}")
        raise

async def send_message(platform_api, message_text):
    try:
        response = platform_api.post_message(message_text)

        if not isinstance(response, dict) or "permalink" not in response:
            logger.warning(f"Unexpected platform API response format: {response}")
            return {"status": "partial", "message": "Posted, but no permalink returned."}

        return {"status": "success", "link": response["permalink"]}
    except AttributeError:
        logger.error("The platform API object may be improperly configured or missing 'post_message'.")
        raise
    except Exception as e:
        logger.error(f"Failed to post message: {e}")
        raise
