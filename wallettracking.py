import requests, json

def get_latest_transaction(wallet_address, solscan_APIKEY):

    url = f'https://pro-api.solscan.io/v2.0/account/transactions?address={wallet_address}&limit=10'
    headers = {
        'token': solscan_APIKEY
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data
    except:
        print(f'Error Code 1100: Invalid wallet address: {wallet_address}')


def list_transactions(wallet_address, solscan_APIKEY, limit=10):

    url = f'https://pro-api.solscan.io/v2.0/account/transactions?address={wallet_address}&limit={limit}'
    headers = {
        'token': solscan_APIKEY
    }
    try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if "data" in data and isinstance(data["data"], list):
                return data["data"]
            else:
                print("No transaction data found.")
                return []
    except requests.RequestException as e:
            print(f"Error fetching transactions: {e}")
            return []


def get_solana_transactions(wallet_address: str, limit: int = 10):

    url = "https://api.mainnet-beta.solana.com"
    headers = {"Content-Type": "application/json"}

    # RPC payload to get confirmed transactions
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            wallet_address,
            {"limit": limit}
        ]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise error for bad responses
        data = response.json()

        if "result" in data and isinstance(data["result"], list):
            return data["result"]  # List of transactions
        else:
            print("No transaction data found.")
            return []
    except requests.RequestException as e:
        print(f"Error fetching transactions: {e}")
        return []


