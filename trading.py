from solana.rpc.api import Client
from solders.transaction import VersionedTransaction
from solana.rpc.types import TxOpts
from solana.rpc.types import MemcmpOpts, TokenAccountOpts
from solders.pubkey import Pubkey
import requests, base58, base64, json, sys, os, time

def getQuote(inputMint, outputMint, amount, slippage=1000):

    url = 'https://api.jup.ag/swap/v1/quote'
    params = {
        'inputMint': inputMint,
        'outputMint': outputMint,
        'amount': amount,
        'slippageBps': slippage,
        'restrictIntermediateTokens': 'true'
    }

    r = requests.get(url, params=params)
    if r.status_code == 200:
        return r.json()
    else:
        print(f"Error: {r.status_code} - {r.text} - {amount}")
        r.raise_for_status()


def buildSwap(quote, pubkey):

    url = 'https://quote-api.jup.ag/v6/swap'
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'quoteResponse': quote,
        'userPublicKey': str(pubkey),
        'wrapUnwrapSOL': False,
        'computeUnitPriceMicroLamports': 0
    }

    r = requests.post(url, headers=headers, data=json.dumps(payload))
    return r.json()


def signTransaction(transaction_base64, keypair, client: Client):

    #blockhash_response = client.get_latest_blockhash()
    #recent_blockhash = blockhash_response.value.blockhash

    transaction_bytes = base64.b64decode(transaction_base64)

    transaction = VersionedTransaction.from_bytes(transaction_bytes)

    signed_transaction = VersionedTransaction(transaction.message, [keypair])

    return bytes(signed_transaction)


def sendSwap(signedTransaction):


    client = Client('https://api.mainnet-beta.solana.com')
    options = {
        'skip_preflight': False,
        'max_retries': 2
    }
    tx_opts = TxOpts(skip_preflight=True, max_retries=2)
    r = client.send_transaction(signedTransaction, opts=tx_opts)
    return r


def buy(ca, amount, keypair, client):

    SOL_MINT = "So11111111111111111111111111111111111111112"

    try:

        quote = getQuote(SOL_MINT, ca, amount)
        #print("Quote received:")
        #print(quote)

        swaptransaction = buildSwap(quote, keypair.pubkey())
        #print("swap built:")

        signedTransaction = signTransaction(swaptransaction['swapTransaction'], keypair, client)
        #print("transaction signed:")
        #print(signedTransaction)

        sentswap = sendSwap(signedTransaction)
        #print("swap sent:")
        #print(sentswap)
        return sentswap

    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


def getTokenBalance(pubkey: Pubkey, tokenMint: str, client: Client) -> int:

    response = client.get_token_accounts_by_owner(
        pubkey,
        TokenAccountOpts(
            mint=Pubkey.from_string(tokenMint)
        )
    )

    token_accounts = response.value

    if not token_accounts:
        print(f"No {tokenMint} tokens found for this wallet.")
        return 0

    account_pubkey = token_accounts[0].pubkey
    balance_response = client.get_token_account_balance(account_pubkey)

    if balance_response.value:
        return int(balance_response.value.amount)

    return 0


def sell(ca, amount, keypair, client):

    SOL_MINT = "So11111111111111111111111111111111111111112"

    balance = (int)(getTokenBalance(keypair.pubkey(), ca, client))

    if balance == 0:
        #print(f"No {ca} tokens available to swap.")
        return

    if amount >= balance:
        amtToTrade = balance
    else:
        amtToTrade = amount
    print(f'balance = {balance} amount = {amount} amttotrade = {amtToTrade}')
    #print(f"Swapping {balance} of {ca} to SOL...")

    try:

        quote = getQuote(ca, SOL_MINT, amtToTrade)
        #print("Quote received:", quote)

        swap_transaction = buildSwap(quote, keypair.pubkey())
        #print("Swap transaction built:", swap_transaction)

        signedTransaction = signTransaction(swap_transaction['swapTransaction'], keypair, client)
        #print("Transaction signed.")

        swap_result = sendSwap(signedTransaction)
        #print("Swap sent:", swap_result)
        return swap_result

    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

