# from rest_framework.exceptions import NotFound
# from jalali_date import datetime2jalali, date2jalali
# from django.conf import settings
# from decimal import Decimal as D
# from django.core.cache import cache
# from managements.models import Converter, Coefficients

# def get_doc_or_404(collection, *args, **kwargs):
#     try:
#         doc = collection.objects(*args, **kwargs).get()
#     except:
#         raise NotFound({"error" : 'not found'})
#     return doc

# class PersianCalender:

#     def __init__(self, datetime):
#         self.datetime = datetime

#     def to_datetime(self):
#         return datetime2jalali(self.datetime).strftime(settings.DATE_TIME_FORMAT)
    
#     def to_date(self):
#         return date2jalali(self.datetime).strftime(settings.DATE_FORMAT)


# def remove_exponent(d):
#     return d.quantize(D(1)) if d == d.to_integral() else d.normalize()


# def translate_number(number):
#     fa_num = '۰١٢٣٤٥٦٧٨٩'
#     en_num = '0123456789'
#     table = str.maketrans(en_num, fa_num)
#     persian_number = str(number).translate(table)
#     return persian_number


# def get_tether_price():
#     if not (cache.get('usdt_sell') and cache.get('usdt_buy')):
#         converter = Converter.objects.last()
#         cache.set_many(
#             {
#                 'usdt_sell': converter.usdt_sell,
#                 'usdt_buy': converter.usdt_buy
#             }
#         )
#     result = cache.get_many(['usdt_sell', 'usdt_buy'])
#     result['symbol'] = 'USDT'
#     result['persian_symbol'] = 'تتر'
#     result['sell_price_tmn'] = str(result.pop('usdt_sell'))
#     result['buy_price_tmn'] = str(result.pop('usdt_buy'))
#     return result

# def prettify(number):
#     ponit_index = number.find('.')
#     if ponit_index < 0:
#         return number
#     elif not number.endswith("0"):
#         return number
#     else:
#         last_ponit_index = len(number) - ponit_index + 1
#         for i in range(-1,-last_ponit_index,-1):
#             if not number[i] == "0":
#                 if number[i] == ".":
#                     return number[0:i]
#                 else:
#                     return number[0:i+1]

# def get_coefficient(base):
#     if not cache.get('coefficients'):
#         Coefficients.cache_coefficient()
#     coefficients = cache.get('coefficients')
#     for coefficient in coefficients:
#         if coefficient['base'] == base:
#             result = {
#                 "sell_coefficient":coefficient["sell_coefficient"],
#                 "buy_coefficient":coefficient["buy_coefficient"]
#             }
#     return result


# def cache_get_or_set(key, value):
#     if cache.has_key(key=key):
#         return cache.get(key=key)
#     cache.set(key=key, value=value)


# def get_client_ip(request):
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]
#     else:
#         ip = request.META.get('REMOTE_ADDR')
#     return ip
