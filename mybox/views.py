from datetime import date, datetime
from time import strptime

from django.db.models import Avg, Min, Max
from django.db.models.functions import Trunc
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.utils.dateparse import parse_date

from mybox.models import Data

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




def chart_data(request, id, gte, lte):
    print(id, gte, lte)
    id_sensor = id
    fr = fill_date(gte)
    to = fill_date(lte)
    x_field = 'time'
    y_field = 'value_calculated'
    limit = None
    trunc_kind = 'day',  # 'year','quarter','month','week','day','week_day','date','time','hour','minute','second'

    print(id, fr, to)

    # .extra('time', 'value_calculated')\
    queryset = Data.objects.filter(id_sensor=id_sensor)
    if fr:
        queryset = queryset.filter(time__gte=fr)
    if to:
        queryset = queryset.filter(time__lte=to)
    queryset = queryset.annotate(
        period=Trunc(
                x_field,
                *trunc_kind,
            )
        ).values("period").annotate(
            y=Avg(y_field), yMin=Min(y_field), yMax=Max(y_field)
        ).order_by("period")

    time = []
    range = []
    average = []
    for entry in queryset:
        stamp = entry['period'].timestamp()*1000
        range.append([stamp,entry['yMin'], entry['yMax']])
        average.append([stamp,entry['y']])
    # print(time)
    # print(range)


    # return JsonResponse(data=[queryset])
    return JsonResponse({'range':range, 'average':average}, safe=False)