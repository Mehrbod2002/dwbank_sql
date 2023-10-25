import requests
import json
from decimal import Decimal as D
from datetime import timedelta

from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from dwbank.celery import celery_app
from markets.models import BlockFee, Withdrawal
from markets.choices import StatusChoices

logger = get_task_logger(__name__)

celery_app.conf.beat_schedule = {
    # executes every 120 seconds
    'check_tx_id_every_60_seconds': {
        'task': 'check_tx_id',
        'schedule': timedelta(seconds=60),
    }
}

@shared_task(name='check_tx_id')
def check_tx_id():
    transfer_objects = Withdrawal.objects.filter(status=StatusChoices.PENDING)
    for i in transfer_objects:
            tx_id = i.tx_id
            data = {"value": tx_id}
            response = requests.post(url='https://api.trongrid.io/wallet/gettransactioninfobyid', json=data)
            if response.status_code == 200:
                response_data = response.json()
                receipt = response_data.get('receipt')
                if receipt:
                    result = receipt.get('result')
                    if result == 'SUCCESS':
                        with transaction.atomic():
                            i.status = StatusChoices.COMPLETED
                            i.save()
                            BlockFee.objects.filter(reason_object_id=i.id).update(
                                status=StatusChoices.TO_ACT
                            )
                        
                    elif result == 'FAILED':
                        with transaction.atomic():
                            i.status = StatusChoices.FAILED
                            i.save()
                            BlockFee.objects.filter(reason_object_id=i.id).update(
                                status=StatusChoices.FAILED
                            )