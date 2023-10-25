from rest_framework.routers import DefaultRouter
from markets.api.views import LoanViewSet, TetherDepositViewSet, CreateDepositViewSet, chargeFiatViewSet,\
                              SupportViewSet, CreditCardViewSet, TransferViewSet, BalanceViewSet,\
                              BalanceNotifViewSet, LoanNotifViewSet, UserRequestViewSet, TransactionViewSet,\
                              DshboardBalanceViewSet

router = DefaultRouter()
router.register(r'loan', LoanViewSet, basename="loan")
router.register(r'charge/tether', TetherDepositViewSet, basename="charge_tether")
router.register(r'charge/fiat', chargeFiatViewSet, basename="charge_fiat")
router.register(r'create/deposit', CreateDepositViewSet, basename="create_deposit")
router.register(r'support', SupportViewSet, basename="support")
router.register(r'create/creditcard', CreditCardViewSet, basename="credit_card")
router.register(r'transfer', TransferViewSet, basename="transfer")
router.register(r'get/balance', BalanceViewSet, basename="get_balance")
router.register(r'email/balance/code', BalanceNotifViewSet, basename="email_balance_code")
router.register(r'email/loan/code', LoanNotifViewSet, basename="email_loan_code")
router.register(r'user/requests', UserRequestViewSet, basename="user_request")
router.register(r'user/transaction', TransactionViewSet, basename="transaction")
router.register(r'get/balance/dashboard', DshboardBalanceViewSet, basename="dashboard_get_balance")