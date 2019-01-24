#!/usr/bin/env python
import os
import sys
import inspect
from datetime import datetime, timedelta
# add project dir to sys path
cmd_folder = os.path.split(os.path.split(inspect.getfile(inspect.currentframe()))[0])[0]
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

os.environ.setdefault("DJANGO_SETTINGS_MODULE",  "fclub.settings")

from contract.models import *

# close contract freeze by date end

# close contract by date end
for c in Contract.objects.filter(is_current=1, date_end__lte=datetime.now()):
    c.close()
    print 'Close contract: ', c.client, c.number
    # change contact date for the client prospect contracts
    for p in Contract.objects.filter(is_current=2, client=c.client
                                     ).order_by('date_joined'):
        p.date = c.date_end + timedelta(days=1)
        p.save()

# activate contract by end activate period
for c in Contract.objects.filter(is_current=2):
    try:
        curr_c = Contract.objects.get(client=c.client, is_current=1)
    except Contract.DoesNotExist:
        # added logic for reissue contracts it should be activated first
        reissue = Contract.objects.filter(client=c.client, number__startswith='O-')
        if len(reissue):
            contract = Contract.objects.get(pk=reissue.pk)
        else:
            contract = Contract.objects.get(pk=c.pk)
        period = timedelta(days=contract.contract_type.period_activation)
        date_to_active = contract.date + period
        if date_to_active.date() <= datetime.now().date():
            contract.activate()
            print 'Activate contract: ', contract.client, contract.number
