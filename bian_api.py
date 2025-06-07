
from binance.cm_futures import CMFutures

cm_futures_client = CMFutures()

# get server time
print(cm_futures_client.time())

cm_futures_client = CMFutures(
    key='cbZ1BYC8pvpFTlBFu6sXEadeTPzdEw3u7SgqC7RxCcFyJWx57m09mFqxhlS0cSSj',
    secret='w2le7dkibjAQ4i1RgKUOqk0lAIDALzGoayU827yLJE150iliAsnC5CMpQHUdDAG3'
)

# Get account information
print(cm_futures_client.account())

# Post a new order
# params = {
#     'symbol': 'BTCUSDT',
#     'side': 'SELL',
#     'type': 'LIMIT',
#     'timeInForce': 'GTC',
#     'quantity': 0.002,
#     'price': 59808
# }
#
# response = cm_futures_client.new_order(**params)
# print(response)