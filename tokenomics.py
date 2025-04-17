import requests

def getTokenPrice(ca, solscanAPIKEY):

    url = f'https://pro-api.solscan.io/v2.0/token/price?address={ca}'
    headers = {
        'token': solscanAPIKEY
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if data['success'] == True:
            price = data['data'][0]['price']
            return price
        else:
            return -1

    except:
        return 'Exit code -1: Make sure CA and Solscan API Key are correct.'

def getSolPrice(solscanAPIKEY):

    sol_address = 'So11111111111111111111111111111111111111112'
    return getTokenPrice(sol_address, solscanAPIKEY)


def getPrice(ca, solscanAPIKEY):

    tokenPrice = getTokenPrice(ca, solscanAPIKEY)
    solPrice = getSolPrice(solscanAPIKEY)
    return tokenPrice / solPrice


def getTokenMarketCap(ca, solscanAPIKEY):

    url = f'https://pro-api.solscan.io/v2.0/token/meta?address={ca}'
    headers = {
        'token': solscanAPIKEY
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if data['success'] == True:
            return data['data']['market_cap']
        else:
            return -1

    except:
        return 'Exit code -1: Make sure CA and Solscan API Key are correct.'


def getMarketCap(ca, solscanAPIKEY):

    tokenMarketCap = getTokenMarketCap(ca, solscanAPIKEY)
    solPrice = getSolPrice(solscanAPIKEY)
    return tokenMarketCap / solPrice

def getTokenSupply(ca, solscanAPIKEY):

    url = f'https://pro-api.solscan.io/v2.0/token/meta?address={ca}'
    headers = {
        'token': solscanAPIKEY
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if data['success'] == True:
            return data['data']['supply']
        else:
            return -1

    except:
        return 'Exit code -1: Make sure CA and Solscan API Key are correct.'

def getTokenName(ca, solscanAPIKEY):

    url = f'https://pro-api.solscan.io/v2.0/token/meta?address={ca}'
    headers = {
        'token': solscanAPIKEY
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if data['success'] == True:
            return data['data']['name']
        else:
            return -1

    except:
        return 'Exit code -1: Make sure CA and Solscan API Key are correct.'

def getTokenSymbol(ca, solscanAPIKEY):

    url = f'https://pro-api.solscan.io/v2.0/token/meta?address={ca}'
    headers = {
        'token': solscanAPIKEY
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if data['success'] == True:
            return data['data']['symbol']
        else:
            return -1

    except:
        return 'Exit code -1: Make sure CA and Solscan API Key are correct.'

def getTokenTwitter(ca, solscanAPIKEY):

    url = f'https://pro-api.solscan.io/v2.0/token/meta?address={ca}'
    headers = {
        'token': solscanAPIKEY
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if data['success'] == True:

            try:
                return data['data']['metadata']['twitter']
            except:
                return f'Exit code -1: Could not access Token Twitter'

        else:
            return -1

    except:
        return 'Exit code -1: Make sure CA and Solscan API Key are correct.'

def getTokenHolderCount(ca, solscanAPIKEY):

    url = f'https://pro-api.solscan.io/v2.0/token/holders?address={ca}&page=1&page_size=10'
    headers = {
        'token': solscanAPIKEY
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if data['success'] == True:
            return data['data']['total']
        else:
            return -1
    except:
        return 'Exit code -1: Make sure CA and Solscan API Key are correct.'

def getTokenCreator(ca, solscanAPIKEY):

    url = f'https://pro-api.solscan.io/v2.0/token/meta?address={ca}'
    headers = {
        'token': solscanAPIKEY
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if data['success'] == True:
            return data['data']['creator']
        else:
            return -1

    except:
        return 'Exit code -1: Make sure CA and Solscan API Key are correct.'
