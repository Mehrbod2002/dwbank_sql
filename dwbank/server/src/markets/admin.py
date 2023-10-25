from django.contrib import admin
from .models import Wage, Wallets, FiatDepositHistory, CreateDeposit, Support, CreditCard, Loan, DepositHistory, InternalTransfers,\
                    Withdrawal, BlockFee, FeeLimit, IntermediateWallet


admin.site.register(FeeLimit)
admin.site.register(IntermediateWallet)

@admin.register(Wallets)
class WalletAdmin(admin.ModelAdmin):
      list_display = ["id", 'user', 'address', 'network', 'tx_id_activation']
      search_fields = ["id__icontains","user__email__icontains", "address__icontains"]
      list_filter = ["id","user", "address", "created_at"]
      list_per_page =10


@admin.register(Loan)
class LoantAdmin(admin.ModelAdmin):
      list_display = ["id",'user', 'currency', 'loan_amount', 'state', "loan_amount"]
      search_fields = ["id__icontains","user__email__icontains", "loan_amount__icontains", "currency__icontains", "state__icontains"]
      list_filter = ["id","state", "created_at", "loan_amount", "currency"]
      list_per_page =10


@admin.register(FiatDepositHistory)
class FiatDepositHistorytAdmin(admin.ModelAdmin):
      list_display = ["id",'user', 'currency', 'amount', 'status']
      search_fields = ["id__icontains","user__email__icontains", "amount__icontains", "currency__icontains", "status__icontains"]
      list_filter = ["id","status", "created_at", "amount", "currency"]
      list_per_page =10


@admin.register(CreateDeposit)
class CreateDepositAdmin(admin.ModelAdmin):
      list_display = ["id",'user', 'currency', 'amount', 'state']
      search_fields = ["id__icontains","user__email__icontains", "amount__icontains", "currency__icontains", "state__icontains"]
      list_filter = ["id","state", "created_at", "amount", "currency"]
      list_per_page =10


@admin.register(Support)
class SupportAdmin(admin.ModelAdmin):
      list_display = ["id",'user', 'subject', 'state', 'title']
      search_fields = ["id__icontains","user__email__icontains", "subject__icontains", "title__icontains", "state__icontains"]
      list_filter = ["id","state", "created_at", "subject"]
      list_per_page =10


@admin.register(CreditCard)
class CreditCardAdmin(admin.ModelAdmin):
      list_display = ["id",'user', 'currency', 'amount', 'state',"card_type","card_level"]
      search_fields = ["id__icontains","user__email__icontains", "amount__icontains", "currency__icontains", "state__icontains","card_type__icontains",
      "card_level__icontains"]
      list_filter = ["id","state", "created_at", "amount", "currency","card_type","card_level"]
      list_per_page =10


@admin.register(Wage)
class WageAdmin(admin.ModelAdmin):
      list_display = ["id",'loan_wage', 'transfer_wage']
      search_fields = ["id__icontains","transfer_wage__icontains", "loan_wage__icontains"]
      list_filter = ["id","loan_wage", "transfer_wage", "created_at"]
      list_per_page =10


@admin.register(DepositHistory)
class DepositHistoryAdmin(admin.ModelAdmin):
      list_display = ["id",'to_address', 'state']
      search_fields = ["id__icontains","to_address__email__icontains", "state__icontains"]
      list_filter = ["id",'to_address', 'state', "created_at"]
      list_per_page =10


@admin.register(InternalTransfers)
class InternalTransfersAdmin(admin.ModelAdmin):
      list_display = ["id",'from_user', 'to_user', 'currency']
      search_fields = ["id__icontains","from_user__email__icontains", "currency__icontains", "to_user__email__icontains",]
      list_filter = ["id","amount", "currency", "created_at"]
      list_per_page =10


@admin.register(BlockFee)
class BlockFeeAdmin(admin.ModelAdmin):
      list_display = ["id",'user', 'currency', 'amount', 'status']
      search_fields = ["id__icontains","user__email__icontains", "amount__icontains", "currency__icontains"]
      list_filter = ["id","created_at", "amount", "currency", 'status']
      list_per_page =10



@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
      list_display = ["id",'user', 'currency', 'amount', 'status']
      search_fields = ["id__icontains","user__email__icontains", "amount__icontains", "currency__icontains", 'status__icontains']
      list_filter = ["id","created_at", "amount", "currency",  'status']
      list_per_page =10

