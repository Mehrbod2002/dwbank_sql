import json
import requests
import base58
import base64
import collections
import statistics
import sys
from decimal import Decimal as D

from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.providers import HTTPProvider
import web3
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import Sum, Q
from rest_framework.exceptions import ValidationError

from markets.models import Wallets, CreditCard, FiatDepositHistory, InternalTransfers, Withdrawal, DepositHistory,\
                           FeeLimit, BlockFee, IntermediateWallet
from markets.choices import StateChoices, DepositStateChoices, StatusChoices
from users.models import UserModel
from users.utils import refrence_id_generate


class TronClient:

    def __init__(self) -> None:
        self.full_node = HTTPProvider(settings.FULL_NODE)
        self.solidity_node = HTTPProvider(settings.SOLIDITY_NODE)
        self.event_server = HTTPProvider(settings.EVENT_SERVER)
        self.token_address =  settings.TOKEN_ADDRESS
        self.client = Tron(provider=HTTPProvider(api_key=settings.TRONGRID_API_KEY))
        self.METHOD_BALANCE_OF = 'balanceOf(address)'
        self.METHOD_TRANSFER = 'transfer(address,uint256)'
        self.API_URL_BASE = settings.API_URL_BASE
        self.DEFAULT_FEE_LIMIT = 1_000_000  # 1 TRX


    def activate_account(self, to_address):
        wallet = IntermediateWallet.objects.last()
        from_address = wallet.address
        private_key = PrivateKey(bytes.fromhex(wallet.private_key))
        txn = (
            self.client.trx.transfer(from_=from_address, to=to_address,amount=100000).memo(
                "test_memo"
            ).build().sign(priv_key=private_key)
        )
        print(txn.txid)
        print(txn.broadcast().wait())
        return txn.txid

    
    def is_address(self, address):
        return self.client.is_address(address)

    def fee_limit(self, page=1, sun_price=420):
        CNTR = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
        PAGE = 1  # max 5
        PRICE = 420 #sun price
        # see https://github.com/tronprotocol/java-tron/issues/2982

        # if len(sys.argv) >= 2:
        #     CNTR = sys.argv[1]
        # if len(sys.argv) >= 3:
        #     PAGE = int(sys.argv[2])

        print(CNTR)
        url = f"https://api.trongrid.io/v1/accounts/{CNTR}/transactions?only_confirmed=true&only_to=true&limit=200&search_internal=false"

        resp = requests.get(url)
        print(resp)
        payload = resp.json()
        data = payload['data']

        for i in range(1, PAGE):
            print(f"paging ... {i}/{PAGE}")
            url = payload['meta']['links']['next']
            resp = requests.get(url)
            payload = resp.json()
            data += payload['data']
            print(data)


        stat = collections.defaultdict(list)

        txns = 0

        for txn in data:
            if (
                txn.get('energy_usage_total', 0) > 0
                and txn['raw_data']['contract'][0]['parameter']['value']['contract_address']
                == base58.b58decode_check(CNTR).hex()
            ):

                txns += 1
                stat[txn['ret'][0]['contractRet']].append(txn['energy_usage_total'])

        print("TXNs:", txns)
        print("RESULT_CODE\tMAX\tMIN\tMEAN\tMEDIAN\tRate")
        for state, values in stat.items():
            print(
                "%15s" % state,
                max(values),
                min(values),
                int(statistics.mean(values)),
                int(statistics.median(values)),
                "%.1f%%" % (len(values) / txns * 100),
                sep='\t',
            )

        print('Use fee_limit >', (max(stat['SUCCESS']) * PRICE) / 1_000_000, 'TRX')
        print((int((max(stat['SUCCESS']) * PRICE) / 1_000_000)+1) * 1000000)
        fee_limit = int((max(stat['SUCCESS']) * PRICE) / 1_000_000) +1
        self.save_fee_limit(fee_limit=fee_limit)
        return fee_limit * 1000000

    def save_fee_limit(self, fee_limit):
        if FeeLimit.objects.count() > 0:
            last_obj = FeeLimit.objects.last()
            pk = last_obj.id
            FeeLimit.objects.filter(id=pk).update(fee_limtt=fee_limit)
        else:
            FeeLimit.objects.create(fee_limtt=fee_limit)
    
    def get_trx_account_balance(self, address) -> D:
        """Get TRX balance of an account. Result in `TRX`."""

        return self.client.get_account_balance(addr=address)

    
    def transfer_trx(self, to_address, amount):
        wallet = IntermediateWallet.objects.last()
        from_address = wallet.address
        private_key = PrivateKey(bytes.fromhex(wallet.private_key))
        trx_amount = amount * 1000000
        txn = (
            self.client.trx.transfer(from_=from_address, to=to_address,amount=trx_amount).memo(
                "test_memo"
            ).build().sign(priv_key=private_key)
        )
        print(txn.txid)
        print(txn.broadcast().wait())
        return txn.txid

        
    def transfer_tether(self, from_address:str, to_address:str, amount:int,private_key:str):
        trx_balance = self.get_trx_account_balance(address=from_address)
        fee_limit = self.fee_limit()
        amount = ((fee_limit / 1000000) - int(trx_balance))
        transfer_trx(to_address=from_address, amount=amount)
        print(fee_limit, type(fee_limit))
        print(private_key)
        private_key = PrivateKey(bytes.fromhex(private_key))
        amount_in_wei = int(amount * 10 ** 6)
        token_contract = self.client.get_contract(self.token_address)
        # transaction = token_contract.functions.transfer(to_address, amount_in_wei).with_owner(from_address).fee_limit(5_000_000).build().sign(priv_key=private_key).broadcast()
        transaction = token_contract.functions.transfer(to_address, amount_in_wei).with_owner(from_address).fee_limit(value=fee_limit).build().sign(priv_key=private_key).broadcast()
        result = transaction.wait()
        print(result)
        return result  

    def get_balance(self, address):
        token_contract = self.client.get_contract(self.token_address)
        balance = token_contract.functions.balanceOf(address)
        return balance / 1000000

    def generate_address(self, user_id):
        try:
            wallet = get_object_or_404(Wallets, user__id=user_id)
            address = wallet.address
        except Exception as e:
            user = get_object_or_404(UserModel, pk=user_id)
            wallet = self.client.generate_address()
            address = wallet['base58check_address']
            private_key = wallet['private_key']
            public_key = wallet['public_key']
            result = self.activate_account(address)
            Wallets.objects.get_or_create(user=user, private_key=private_key, address=address, public_key=public_key, tx_id_activation=result)
        return address, 'trc20'
    
    def address_to_parameter(self, addr):
        return "0" * 24 + base58.b58decode_check(addr)[1:].hex()

    def amount_to_parameter(self, amount):
        return '%064x' % amount
    
    def transaction_history(self, address):
        url = f'https://api.trongrid.io/v1/accounts/{address}/transactions/trc20?'
        payload = {
            "sort": 'blockNumber',
            'limit':10,
        }
        res = requests.get(url,params=payload)
        obj = json.loads(res.text)
        data = obj['data']
        details = []
        for i in data:
            if i['to'] == address:
                if not DepositHistory.objects.filter(tx_id=i['transaction_id']).exists():
                    DepositHistory.objects.create(
                        to_address = i['to'],
                        value = i['value'],
                        tx_id = i['transaction_id'],
                        time = i['block_timestamp'],
                        from_address = i['from']
                    )

                details.append(i)
        return details
    
    # def get_balance(self, address):
    #     token_contract = self.client.get_contract(self.token_address)
    #     balance = token_contract.functions.balanceOf(address)
    #     url = "https://nile.trongrid.io" + 'wallet/triggerconstantcontract'
    #     payload = {
    #         'owner_address': base58.b58decode_check(address).hex(),
    #         'contract_address': base58.b58decode_check(self.token_address).hex(),
    #         'function_selector': self.METHOD_BALANCE_OF,
    #         'parameter': self.address_to_parameter(address),
    #     }
    #     resp = requests.post(url, json=payload)
    #     data = resp.json()
    #     if data['result'].get('result', None):
    #         val = data['constant_result'][0]
    #         balance = int(val, 16)
    #         return balance
    #     else:
    #         raise ValidationError('error')

    

class PayPalClient:

    def __init__(self) -> None:
        self.client_id = settings.CLIENT_ID
        self.client_secret = settings.CLIENT_SECRET

    def access_token(self):
        url = "https://api.sandbox.paypal.com/v1/oauth2/token"
        data = {
                    "client_id":self.client_id,
                    "client_secret":self.client_secret,
                    "grant_type":"client_credentials"
                }
        headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": "Basic {0}".format(base64.b64encode((self.client_id + ":" + self.client_secret).encode()).decode())
                }

        token = requests.post(url, data, headers=headers)
        return token.json()['access_token']

    def generate_link(self, fiat_deposit_obj):
        try:
            token = self.access_token()
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer '+token,
            }
            json_data = {
                "intent": "CAPTURE",
                "application_context": {
                    "notify_url": "https://dwbank.org",
                    "return_url": "https://dwbank.org",#change to your domain
                    "cancel_url": "https://dwbank.org", #change to your domain
                    "brand_name": "dwbank",
                    "landing_page": "BILLING",
                    "shipping_preference": "NO_SHIPPING",
                    "user_action": "CONTINUE"
                },
                "purchase_units": [
                    {
                        "reference_id": refrence_id_generate(),
                        "description": "dwbank",

                        "custom_id": "dwbank",
                        "soft_descriptor": "dwbank",
                        "amount": {
                            "currency_code": fiat_deposit_obj.currency,
                            "value": fiat_deposit_obj.amount #amount,
                        },
                    }
                ]
            }
            response = requests.post('https://api-m.sandbox.paypal.com/v2/checkout/orders', headers=headers, json=json_data)
            order_id = response.json()['id']
        except Exception as e:
            raise ValidationError(e)
        fiat_deposit_obj.deposit_id = order_id
        fiat_deposit_obj.save()
        linkForPayment = response.json()['links'][1]['href']
        return linkForPayment

    def order_id_details(self, order_id):
        token = self.access_token()
        captureurl = f'https://api.sandbox.paypal.com/v2/checkout/orders/{id}'#see transaction status
        headers = {"Content-Type": "application/json", "Authorization": "Bearer "+token}
        response = requests.get(captureurl, headers=headers)
        return response.json()

    def check_balance(self, order_id):
        token = self.access_token()
        captureurl = f'https://api.sandbox.paypal.com/v2/checkout/orders/{order_id}'#see transaction status
        headers = {"Content-Type": "application/json", "Authorization": "Bearer "+token}
        response = requests.get(captureurl, headers=headers)
        value = '0'
        if response.status_code == 200:
            data = response.json()
            if data.get('status'):
                if data['status'] == 'COMPLETED':
                    value = data["purchase_units"][0]['amount']['value']
        elif response.status_code == 404:
            ...
        else:
            raise ValidationError('error')
        return value

    def transfer(self):
        token = self.access_token()
        headers = {"Content-Type": "application/json", "Authorization": "Bearer "+token}
        data = '{ "sender_batch_header": { "sender_batch_id": "Payouts_2020_100007", "email_subject": "You have a payout!", "email_message": "You have received a payout! Thanks for using our service!" }, "items": [ { "recipient_type": "EMAIL", "amount": { "value": "9.87", "currency": "USD" }, "note": "Thanks for your patronage!", "sender_item_id": "201403140001", "receiver": "receiver@example.com", "recipient_wallet": "RECIPIENT_SELECTED" } ] }'
        response = requests.post('https://api-m.sandbox.paypal.com/v1/payments/payouts', headers=headers, data=data)
        return response.json()


    def transfer_detail(self, transfer_id):
        import requests

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer A101.OLQiCyqOpVwigKQQDu3CYlamZ1KTKQmhrbAZK85RIy4IiWh9d_up_lTrem_lfXdV.P3gvkY3PO28akjKYaDorm12QdfK',
        }

        response = requests.get('https://api-m.sandbox.paypal.com/v1/payments/payouts-item/8AELMXH8UB2P8', headers=headers)


class ERC20:

    def __init__(self):
        INFURA_URL = settings.INFURA_URL
        INFURA_KEY = settings.INFURA_KEY
        self.web3 = Web3(Web3.HTTPProvider(INFURA_URL + INFURA_KEY))

    def generate_address(self):
        key = '0xc3182acb87100727e505dce15b132a8e95cdb1d70a92548fbf57d0724bcc46e4'
        w = web3.Account.create()
        print(w.key)
        w = self.web3.eth.account.privateKeyToAccount(key)
        w.address
        return w.address

    def get_balance():
        ...
    
    def transfer():
        ...


def get_usdt_balance(user):
    wallet = get_object_or_404(Wallets, user=user)
    address = wallet.address
    tron_client = TronClient()
    tether_balance  = tron_client.get_balance(address=address)
    creditcards = CreditCard.objects.filter(Q(user=user) & ~Q(state=StateChoices.Not_Accepted) & Q(currency='USDT')).aggregate(Sum("amount"))['amount__sum'] or D('0')
    block_balance = BlockFee.objects.filter(user=user, status__in=[StatusChoices.PENDING, StatusChoices.TO_ACT], currency='USDT').aggregate(Sum("amount"))['amount__sum'] or D('0')
    balance = D(str(tether_balance)) - creditcards - block_balance
    return balance

def get_usd_balance(user):
    paypal_client = PayPalClient()
    orders_id = FiatDepositHistory.objects.filter(user=user, currency='USD').values_list('deposit_id', flat=True)
    values = '0'
    for order_id in orders_id:
        try:
            value = paypal_client.check_balance(order_id=order_id)
        except Exception as e:
            raise ValidationError(e)
        values = D(value) + D(values)
    creditcards = CreditCard.objects.filter(user=user, state=StateChoices.Success, currency='USD').aggregate(Sum("amount"))['amount__sum'] or 0
    withdrawals = Withdrawal.objects.filter(user=user, status=StatusChoices.COMPLETED, currency='USD').aggregate(Sum("amount"))['amount__sum'] or 0
    internal_withdrawals = InternalTransfers.objects.filter(from_user=user,currency='USD').aggregate(Sum("amount"))['amount__sum'] or 0
    internal_deposits = InternalTransfers.objects.filter(to_user=user,currency='USD').aggregate(Sum("amount"))['amount__sum'] or 0
    balance = (D(values) + internal_deposits) - (withdrawals + internal_withdrawals + creditcards)
    return balance

def get_euro_balance(user):
    paypal_client = PayPalClient()
    orders_id = FiatDepositHistory.objects.filter(user=user, currency='EURO').values_list('deposit_id', flat=True)
    values = '0'
    for order_id in orders_id:
        try:
            value = paypal_client.check_balance(order_id=order_id)
        except Exception as e:
            raise ValidationError(e)
        values = D(value) + D(values)
    creditcards = CreditCard.objects.filter(user=user, state=StateChoices.Success, currency='EURO').aggregate(Sum("amount"))['amount__sum'] or 0
    withdrawals = Withdrawal.objects.filter(user=user, status=StatusChoices.COMPLETED, currency='EURO').aggregate(Sum("amount"))['amount__sum'] or 0
    internal_withdrawals = InternalTransfers.objects.filter(from_user=user,currency='EURO').aggregate(Sum("amount"))['amount__sum'] or 0
    internal_deposits = InternalTransfers.objects.filter(to_user=user,currency='EURO').aggregate(Sum("amount"))['amount__sum'] or 0
    balance = (D(values) + internal_deposits) - (withdrawals + internal_withdrawals + creditcards)
    return balance



# example = {'id': '5c7b1c527ea01c37986ee582f49cd985a09f22217a65a610d87774c3a71a61ca', 'fee': 27600900, 'blockNumber': 55052062,
#  'blockTimeStamp': 1695787101000, 'contractResult': ['0000000000000000000000000000000000000000000000000000000000000000'],
#   'contract_address': 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',
#    'receipt': {'energy_fee': 27255900, 'energy_usage_total': 64895, 'net_fee': 345000, 'result': 'SUCCESS', 'energy_penalty_total': 35245}, 
#    'log': [{'address': 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t', 'topics': ['ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef', 
#    '000000000000000000000000fd8dbf54234d06bd5a6cf163de101eeaaec6e018', '0000000000000000000000005d0b6e7052dc86f129353d1886b97bc9c385aaa4'],
#     'data': '00000000000000000000000000000000000000000000000000000000003d0900'}]}
