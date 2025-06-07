
from binance.cm_futures import CMFutures

cm_futures_client = CMFutures()

# get server time
print(cm_futures_client.time())

client = CMFutures(
    key='cbZ1BYC8pvpFTlBFu6sXEadeTPzdEw3u7SgqC7RxCcFyJWx57m09mFqxhlS0cSSj',
    secret='w2le7dkibjAQ4i1RgKUOqk0lAIDALzGoayU827yLJE150iliAsnC5CMpQHUdDAG3'
)

params = {
    'symbol': 'BTCUSDT',
    'recvWindow': 5000,
    'timestamp': cm_futures_client.time()['serverTime']
}

open_orders = client.get_open_orders(**params)

print(open_orders)