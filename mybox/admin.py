import sys
from datetime import timedelta, date
from math import sqrt
import json
from symbol import power

from daterangefilter.filters import PastDateRangeFilter
from django.contrib import admin, messages
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator
from django.db import transaction, connection, OperationalError
from django.db.models import Count, ExpressionWrapper, Avg, DateTimeField, Min, Max, Window, Q, F, FloatField, Case, \
    When
from django.db.models.functions import TruncDay, Trunc, Lag, Abs, Sqrt, Sign
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.datetime_safe import datetime
from django.utils.functional import cached_property
from import_export.admin import ImportExportMixin, ImportExportModelAdmin, ExportMixin, ExportActionMixin
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from admin_auto_filters.filters import AutocompleteFilter

from mybox.models import *
from mybox.tools import positive_sgn, Epoch, fill_date, translate_period, choose_period

# Register your models here.

admin.site.site_header = 'Vodárenský přivaděč Bedřichov'
admin.site.site_title = 'Přivaděč Bedřichově'
admin.site.index_title = "Výtejte v nahlžínení do tunelu"


# _________________akce____________________________

def recompute_value(self, request, queryset):
    """
    Přepočte měřené hodnoty na veličiny.
    value => value_calculated
    """

    # changed = queryset.update(value_calculated=8, delivery_date=timezone.now())  #
    # post_pay = queryset.filter(shipping=1).filter(payment=1).update(payment=2)

    def update_for(queryset, id, formula):
        changes = queryset.filter(id_sensor=id).update(
            value_calculated=ExpressionWrapper(
                formula,  #
                output_field=FloatField()
            ),
        )
        if changes:
            messages.add_message(request, messages.INFO,
                                 f"U senzoru {id} bylo provedeno {changes} změn")
        return queryset.exclude(id_sensor=id)

    def shift(on_field, step, Q_obj):
        return Window(
            expression=Lag(on_field, offset=step),
            # partition_by=Q_obj, # není nutné
            # default=None,   # výchozí hodnota
        )

    id_of_counter = [168, 184]
    step_for_counter = [3, 1]  # Lag je číslován od nuly. (Kork 1 provede skok o dva řádky.)
    volume_of_counter = [15, 6.66]
    if queryset.filter(id_sensor__in=id_of_counter).exists():
        for i, id in enumerate(id_of_counter):
            q_counter = queryset.filter(id_sensor=id)
            q_count_an = q_counter.annotate(  # alias for 3.2
                v_lag=shift('value', step_for_counter[i], Q(id_sensor=id)),
                t_lag=shift('time', step_for_counter[i], Q(id_sensor=id)),
            )
            q_count_an = q_count_an.annotate(
                numerator=volume_of_counter[i] * (F('value') - F('v_lag')),
                # numerator=F('value') - F('v_lag'),
                # denominator=Epoch(F('time') - F('t_lag')),
            )
            q_count_an = q_count_an.annotate(
                result=Case(
                    When(value__lte=step_for_counter[i],
                         then=ExpressionWrapper(
                             step_for_counter[i] * Sign(F('numerator')) * (-1) / Epoch(F('time') - F('t_lag')),
                             output_field=FloatField())
                         ),
                    When(v_lag__lte=step_for_counter[i],
                         then=ExpressionWrapper(
                             # F('value') / Epoch(F('time') - F('t_lag')),
                             step_for_counter[i] * Sign(F('numerator')) * (-1) / Epoch(F('time') - F('t_lag')),
                             output_field=FloatField())
                         ),
                    # When(numerator__isnull=True, then=0.0),
                    default=ExpressionWrapper(
                        F('numerator') / Epoch(F('time') - F('t_lag')),
                        output_field=FloatField()
                    ),
                ),
                # ).update(value_calculated=F('result'))
                # ).exclude(result__isnull=True)
                # ).exclude(result=0)
            )
            # objs = list(q_count_an)
            objs = []
            for x in q_count_an:
                if x.result:
                    x.value_calculated = x.result
                    objs.append(x)
            changes = Data.objects.bulk_update(objs, ['value_calculated'], 1000)
            # [(row.value_calculated) for row in objs if objs.result != None]
            # q_counter.update(value_calculated=q_count_an)
            # dict_count_an['value_calculated'] = dict_count_an.pop('result')
            # Data.objects.update(**dict_count_an)
            # Data.objects.bulk_update(list(q_counter), ['value_calculated'])
            # changes = len(objs)
            if changes:
                messages.add_message(request, messages.INFO,
                                     f"U senzoru {id} bylo provedeno {changes} změn.")
                messages.add_message(request, messages.WARNING,
                                     f'Pozor: Tento výpočet je prováděn přes okénko {step_for_counter[i] + 1} záznamů. První změněná položka je až {step_for_counter[i] + 1}. v pořadí.')
        # data = []
        # for entry in q_counter:
        #     data.append()
    queryset = queryset.exclude(id_sensor__in=id_of_counter)
    # _________________169, 182, 187____________________________
    queryset = queryset.exclude(id_sensor__in=[169, 182])  # podobné jako 164
    # _________________164____________________________
    queryset = queryset.exclude(id_sensor=164)  # zatím není vzorec
    # _________________178____________________________
    queryset = update_for(queryset, 178, 34.5 * Sqrt(F('value') / 1000))
    # _________________172____________________________
    queryset = update_for(queryset, 172,
                          82.2 * (
                                  Sqrt(F('value') / 1000)
                                  + 2 * Sqrt(((Sign(F('value') - 38) + 1) / 2) * ((F('value') - 38) / 1000))
                                  + Sqrt(((Sign(F('value') - 200) + 1) / 2) * ((F('value') - 200) / 1000))
                          )
                          )
    # _________________187____________________________
    queryset = update_for(queryset, 187, 7.95 * 10 ** (-5) * Abs(310.4 - F('value')) ** 2.3)
    # _________________ostatní____________________________
    changes = queryset.update(value_calculated=F('value'))
    if changes:
        messages.add_message(request, messages.INFO,
                             f"{changes} hodnot byo bylo pouze překopírováno beze změny.")


recompute_value.allowed_permissions = ['change']
recompute_value.short_description = "Přepočíst"


# _________________custom_admin____________________________

class DefaultFilterAdmin(admin.ModelAdmin):
    def changelist_view(self, request, *args, **kwargs):
        # from django.http import HttpResponseRedirect
        # if self.default_filters:
        try:
            test = request.META['HTTP_REFERER'].split(request.META['PATH_INFO'])
            if test and test[-1] and not test[-1].startswith('?'):
                url = reverse('admin:%s_%s_changelist' % (self.opts.app_label, self.opts.model_name))
                filters = []
                for filter in self.default_filters:
                    key = filter.split('=')[0]
                    # if not request.GET.has_key(key):
                    if not key in request.GET:
                        filters.append(filter)
                if filters:
                    from django.http import HttpResponseRedirect
                    return HttpResponseRedirect("%s?%s" % (url, "&".join(filters)))
        except:
            pass
        return super(DefaultFilterAdmin, self).changelist_view(request, *args, **kwargs)


class TimeLimitedPaginator(Paginator):
    """
    Paginator that enforces a timeout on the count operation.
    If the operations times out, a fake bogus value is
    returned instead.
    """

    @cached_property
    def count(self):
        # endless paging
        if self.object_list.db is 'mybox':
            try:
                with connection.cursor() as cursor:
                    # cursor.execute('SET LOCAL statement_timeout TO 10000;')
                    return super().count
            except OperationalError:
                print('Paginátoru skončil limit ({})'.format(self.object_list))
                return 99999999
            except SyntaxError:
                print('SyntaxError db:{}'.format(self.object_list.db))
                return super().count
        else:
            print('Není MyBox')
            return super().count

    # @cached_property
    # def count(self):
          #  estimated paging -- I do not have access
    #     try:
    #         if not self.object_list.query.where:
    #             # estimates COUNT: https://djangosnippets.org/snippets/2593/
    #             cursor = connection.cursor()
    #             cursor.execute('SELECT reltuples FROM pg_class WHERE relname = %s',
    #                            [self.object_list.query.model._meta.db_table])
    #             print('Using the reltuples')
    #
    #             ret = int(cursor.fetchone()[0])
    #         else:
    #             return self.object_list.count()
    #     except:
    #         import traceback
    #         traceback.print_exc()
    #         # AttributeError if object_list has no count() method.
    #         return len(self.object_list)

class ChartAdmin(admin.ModelAdmin, ):
    """
    This is intended to be mixed with django.contrib.admin.ModelAdmin
    https://docs.djangoproject.com/en/def/ref/contrib/admin/#modeladmin-objects
    """
    change_list_template = 'admin/change_list_chartjs.html'
    change_list_parent = 'admin/import_export/change_list_import_export.html'
    x_field = 'time'
    y_field = 'value_calculated'
    limit = None
    trunc_kind = 'day',  # 'year','quarter','month','week','day','week_day','date','time','hour','minute','second'

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            qs = response.context_data['cl'].queryset
            get_params = request.GET
        except (AttributeError, KeyError):
            # messages.add_message(request, messages.ERROR, "Nevrací queryset")
            return response

        # pokud není vybrán exaktně jeden sensor
        # if 'id_sensor__id_sensor__exact' not in get_params:
        enable_for = ('id_sensor__id_sensor', 'id_sensor__id_sensor__exact', 'id_sensor__pk__exact', 'id_sensor', 'q')
        if all(param not in get_params for param in enable_for):
            messages.add_message(request, messages.INFO, "Aby bylo možné zbrazit graf, vyberte prosím poze jeden senzor.")
            return response

        if 'q' in get_params:
            ids = qs.values('id_sensor').distinct().count()
            if ids != 1:
                messages.add_message(request, messages.INFO, f"Počet zobrazených senzorů je {ids}. Aby bylo možné zbrazit graf, vyberte prosím pouze jeden.")
                return response

        # # Aggregate new subscribers per day
        # Vlastní perioda: https://stackoverflow.com/a/56466800/9942866
        chart_data = qs \
            .annotate(
                period=Trunc(
                    self.x_field,
                    *self.trunc_kind,
                )
            ).values("period") \
            .annotate(y=Avg(self.y_field), yMin=Min(self.y_field), yMax=Max(self.y_field)) \
            .order_by("-period")
        chart_data = chart_data[:self.limit]

        cached_data = cache.get(get_params)
        if cached_data:
            as_json = json.dumps(cached_data, cls=DjangoJSONEncoder)
        else:
            as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
            cache.set(get_params, list(chart_data), 300)
        context = {
            "chart_data": as_json,
            # "parent_template": self.change_list_parent or 'change_list.html',
            "parent_template": 'admin/import_export/change_list_import_export.html',
        }
        # extra_context = extra_context or context
        response.context_data.update(context)
        # response.context_data |= context  # Python 3.9+
        return response

class HCHAdmin(admin.ModelAdmin, ):
    """
    This is intended to be mixed with django.contrib.admin.ModelAdmin
    https://docs.djangoproject.com/en/def/ref/contrib/admin/#modeladmin-objects
    """
    change_list_template = 'admin/change_list_hch_cached.html'
    x_field = 'time'
    y_field = 'value_calculated'
    limit = None
    trunc_kind = 'day',  # 'year','quarter','month','week','day','week_day','date','time','hour','minute','second'

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            qs = response.context_data['cl'].queryset
            get_params = request.GET
        except (AttributeError, KeyError):
            # messages.add_message(request, messages.ERROR, "Nevrací queryset")
            return response

        # pokud není vybrán exaktně jeden sensor
        # if 'id_sensor__id_sensor__exact' not in get_params:
        enable_for = ('id_sensor__id_sensor', 'id_sensor__id_sensor__exact', 'id_sensor__pk__exact', 'id_sensor', 'q')
        if all(param not in get_params for param in enable_for):
            messages.add_message(request, messages.INFO, "Aby bylo možné zbrazit graf, vyberte prosím pouze jeden senzor.")
            return response

        if 'q' in get_params:
            ids = qs.values('id_sensor').distinct().count()
            if ids != 1:
                messages.add_message(request, messages.INFO, f"Počet zobrazených senzorů je {ids}. Aby bylo možné zbrazit graf, vyberte prosím pouze jeden.")
                return response

        for param in get_params:
            if get_params[param].isnumeric():
                sensor_id = get_params[param]
                break
        try:
            my_sensor = Sensor.objects.select_related("id_magnitude")\
                .only("note", "id_magnitude__magnitude_cs", "id_magnitude__unit_cs")\
                .get(pk = sensor_id)
        except Sensor.DoesNotExist:
            messages.add_message(request, messages.WARNING, f"Patřičný senzor pro graf nenalezen")
            return response

        cached_sensor = cache.get(get_params)
        if cached_sensor:
            pass
        else:
            try:
                cached_sensor = Sensor.objects.select_related("id_magnitude") \
                    .only("note", "id_magnitude__magnitude_cs", "id_magnitude__unit_cs") \
                    .get(pk=sensor_id)
            except Sensor.DoesNotExist:
                messages.add_message(request, messages.WARNING, f"Patřičný senzor pro graf nenalezen")
                return response
            cache.set(get_params, cached_sensor, 300)
        try:
            fr = fill_date(request.GET['time__range__gte'])
            to = fill_date(request.GET['time__range__lte'])
        except MultiValueDictKeyError:
            fr = to = None

        agregate_period = translate_period(choose_period(fr, to))

        context = {
            "magn": cached_sensor.id_magnitude.magnitude_cs,
            "unit": cached_sensor.id_magnitude.unit_cs,
            "note": cached_sensor.note,
            "agre": agregate_period,
        }
        # print(context)
        response.context_data.update(context)
        # response.context_data |= context  # Python 3.9+
        return response
# _________________register_models____________________________

@admin.register(ViewAllData)
class AllDataAdmin(ChartAdmin, DefaultFilterAdmin):
    change_list_template = 'admin/change_list_chartjs.html'
    list_per_page = 50
    # show_full_result_count = False
    # paginator = TimeLimitedPaginator
    default_filters = ('time__gte={}'.format(timezone.now().date() - timedelta(weeks=4)),)
    date_hierarchy = 'time'
    list_filter = [('time', DateRangeFilter), "id_sensor", "magnitude_cs", "point_number", 'device_number',
                   'sensor_number', ]
    # list_display = ['time','data_as_link','bin_data','point_number','type_number','sensor_number','device_number','point_number',]
    list_display = ['id_sensor', 'time', 'data_as_link', 'calculate_flow', 'point_number', 'type_number',
                    'sensor_as_link', 'device_number_as_link', 'point_number', ]

    def calculate_flow(self, obj: Data):

        unit = "ml/s"
        if obj.id_sensor == 178:
            k = 34.5  # pro senzor 178
            comp_value = k * sqrt(obj.value / 1000)
        elif obj.id_sensor == 172:
            val = obj.value
            # comp_value = positive_sgn(val-38)
            # unit = val-38
            comp_value = 82.2 * (
                    sqrt(val / 1000) +
                    2 * sqrt(0.5 * (positive_sgn(val - 38)) * (val - 38) / 1000) +
                    sqrt(0.5 * (positive_sgn(val - 200)) * (val - 200) / 1000)
            )
        else:
            return '{:.4} {}'.format(obj.value, obj.unit_cs)
        return '{:.4} {}'.format(comp_value, unit)

    calculate_flow.short_description = "hodnota"
    calculate_flow.admin_order_field = "value"


class SensorFilter(AutocompleteFilter):
    title = 'Sensor'
    field_name = 'id_sensor'


# class PointFilter(AutocompleteFilter):
#     title = 'Point'
#     field_name = 'point_number'

# class MagnitudeFilter(AutocompleteFilter):
#     title = 'Magnitude'
#     field_name = 'id_magnitude'

@admin.register(Sensor)
class SensorAdmin(ImportExportMixin, DefaultFilterAdmin):
    # class SensorAdmin(admin.ModelAdmin):
    change_list_template = 'admin/change_list_with_hch.html'
    list_filter = [('id_data__time', DateRangeFilter), 'id_data__time', 'id_device', 'id_magnitude', 'id_point', 'id_measurement', ]
    list_select_related = ('id_device', 'id_magnitude', 'id_point', 'id_measurement',)
    # list_select_related = ('', )
    list_per_page = 32
    show_full_result_count = False
    search_fields = ['id_sensor', 'note', 'sensor_number', ]
    # paginator = TimeLimitedPaginator
    list_display = ['id_sensor', 'sensor_number', 'note', 'get_device_as_link',
                    'get_magnitude_as_link', 'get_point_as_link', 'get_measurement_as_link', ]
    # inlines = [DataInline, ]


@admin.register(Data)
# class DataAdmin(ImportExportMixin, ExportActionMixin, ChartAdmin, DefaultFilterAdmin, ):
class DataAdmin(ImportExportMixin, ExportActionMixin, HCHAdmin, DefaultFilterAdmin, ):
# class DataAdmin(ExportActionMixin,  admin.ModelAdmin):
    # class DataAdmin(admin.ModelAdmin):

    change_list_template = 'admin/change_list_hch_cached.html'
    list_per_page = 40
    show_full_result_count = False
    # paginator = TimeLimitedPaginator
    # search_fields = ["id_sensor__note", 'id_sensor__pk', "id_sensor__id_magnitude__unit_cs"]
    default_filters = (
        f'time__range__gte={(datetime.today() - timedelta(days=7)):%d.%m.%Y}',
        f'time__range__lte={datetime.today():%d.%m.%Y}'
    )
    # date_hierarchy = 'time'
    list_display = ['sensor_link', 'time_received', 'sensor_time', 'value', 'v_calc_4d', 'unit', 'point']
                    #'type_number', 'point_number', 'sensor_number', 'device_number', 'calculate_flow', ]
    list_display_links = ['time_received']
    list_filter = [
        ('time', DateRangeFilter), SensorFilter, "id_sensor__id_magnitude", "id_sensor__id_point",
        # ('time', PastDateRangeFilter), 'device_number', 'sensor_number', "point_number",
    ]
    autocomplete_fields = ['id_sensor']
    # list_select_related = ('id_sensor',) # -[list_per_page] query
    #list_select_related = ('id_sensor', 'id_sensor__id_magnitude')  # -[list_per_page] query
    list_select_related = ('id_sensor', 'id_sensor__id_magnitude', 'id_sensor__id_point')  # -[list_per_page] query
    actions = ExportActionMixin.actions + [recompute_value, ]
    # actions = [recompute_value, ]

    # ...implementováno default filterem
    # def get_rangefilter_time_default(self, request):
    #     return (
    #         datetime.today() - timedelta(days=7),
    #         datetime.today()
    #     )

    def get_rangefilter_time_title(self, request, field_path):
        return 'Časové období:'


    def get_queryset(self, request):
        self.full_path = request.get_full_path()
        return super().get_queryset(request)

    def sensor_link(self, obj: Data):
        if "id_sensor__pk" in self.full_path:
            return obj
        else:
            return mark_safe('<a href="{}&id_sensor__pk__exact={}">{}</a>'.format(self.full_path, obj.id_sensor.pk, obj))

    sensor_link.short_description = "senzor"
    sensor_link.admin_order_field = "id_sensor"

    def sensor_time(self, obj: Data):
        return obj.time.strftime('%H:%M:%S.%f')[:-4]

    sensor_time.short_description = "čas senzoru"
    sensor_time.admin_order_field = "time"

    def unit(self, obj: Data):
        return obj.id_sensor.id_magnitude.unit_cs

    unit.short_description = "jednotka"
    unit.admin_order_field = "id_sensor__id_magnitude__unit_cs"

    def point(self, obj: Data):
        return obj.id_sensor.id_point.point_cs

    point.short_description = "pozice"
    point.admin_order_field = "id_sensor__id_point__point_cs"

    def calculate_flow(self, obj: Data):

        unit = "ml/s"
        if obj.id_sensor.id_sensor == 178:
            k = 34.5  # pro senzor 178
            comp_value = k * sqrt(obj.value / 1000)
        elif obj.id_sensor.id_sensor == 172:
            val = obj.value
            # comp_value = positive_sgn(val-38)
            # unit = val-38
            comp_value = 82.2 * (
                    sqrt(val / 1000) +
                    2 * sqrt(0.5 * (positive_sgn(val - 38)) * (val - 38) / 1000) +
                    sqrt(0.5 * (positive_sgn(val - 200)) * (val - 200) / 1000)
            )
        else:
            return '{:.4} {}'.format(obj.value, obj.id_sensor.id_magnitude.unit_cs)
        return '{:.4} {}'.format(comp_value, unit)

    calculate_flow.short_description = "hodnota"
    calculate_flow.admin_order_field = "value"


class SensorInline(admin.TabularInline):
    model = Sensor
    extra = 0
    show_change_link = True
    readonly_fields = ('id_device','id_point',)
    # can_delete = False


@admin.register(Magnitude)
class MagnitudeAdmin(ImportExportModelAdmin):
    inlines = [SensorInline, ]
    search_fields = ["id_magnitude", "magnitude_cs"]


class MagnitudeInline(admin.TabularInline):
    model = Magnitude


class DataInline(admin.StackedInline):  # CompactInline //jet
    model = Data
    extra = 0
    show_change_link = True


@admin.register(Point)
class PointAdmin(ImportExportModelAdmin):
    inlines = [SensorInline, ]
    search_fields = ["id_point", "point_cs", "point_number"]


# admin.site.register(Data)
admin.site.register(DataOld)
# admin.site.register(ViewAllData)
admin.site.register(Device)
admin.site.register(Logs)
# admin.site.register(Magnitude)
admin.site.register(Measurement)
# admin.site.register(Point)
# admin.site.register(Sensor)
admin.site.register(Uzivatel)
