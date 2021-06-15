from datetime import datetime
from time import strptime

from django.db.models import Func


def sgn(x):
    # return 1 - (x <= 0)
    return int(x >= 0)

def positive_sgn(x):
    ### reurutn 0 or 1 for positive number ###
    return int(x > 0)

class Epoch(Func):
   function = 'EXTRACT'
   template = "%(function)s('epoch' from %(expressions)s)"


def fill_date(str_date):
    # if str_date is "-":
    #     return None
    # else:
    try:
        return datetime(*(strptime(str_date, '%d.%m.%Y'))[0:6])
    except:
        try:
            return datetime(*(strptime(str_date, '%Y-%m-%d'))[0:6])
        except:
            return None

def choose_period(t_from, t_to):
    # return one of: 'day', 'hour','minute'
    # Avilable chooses are: 'year','quarter','month','week','day','week_day','date','time', 'day', 'hour','minute','second'
    # neomezeno:
    if t_from is None or t_to is None:
        return 'day'
    # podle omezení:
    if (t_to - t_from).days <= 3:
        return 'minute'
    elif (t_to - t_from).days <= 14: # menší než 2 týdny
        return 'hour'
    else:
        return 'day'

def translate_period(period: str):
    period_dict = {'day':'dnech', 'hour':'hodinách', 'minute':'minutách'}
    return period_dict[period]