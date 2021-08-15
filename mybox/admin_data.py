from datetime import timedelta

from admin_auto_filters.filters import AutocompleteFilter
from advanced_filters.admin import AdminAdvancedFiltersMixin
from django.contrib import messages, admin
from django.core.cache import cache
from django.db.models import F, Q, Case, When, FloatField, ExpressionWrapper, Window
from django.db.models.functions import Sqrt, Sign, Abs, Lag
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.datetime_safe import datetime
from django.utils.safestring import mark_safe
from import_export.admin import ExportActionMixin, ImportExportMixin
from rangefilter.filters import DateRangeFilter

from mybox.default_filter import DefaultFilterAdmin
from mybox.models import Data, Sensor
from mybox.tools import Epoch, fill_date, translate_period, choose_period


###_________________operce____________________________


def recompute_value(self, request, queryset):
    """
    Přepočte měřené hodnoty na veličiny.
    value => value_calculated
    """

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

    # _________________sklopky____________________________
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
                             step_for_counter[i] * Sign(F('numerator')) * (-1) / Epoch(F('time') - F('t_lag')),
                             output_field=FloatField())
                         ),
                    default=ExpressionWrapper(
                        F('numerator') / Epoch(F('time') - F('t_lag')),
                        output_field=FloatField()
                    ),
                ),
            )

            objs = []
            for x in q_count_an:
                if x.result:
                    x.value_calculated = x.result
                    objs.append(x)
            changes = Data.objects.bulk_update(objs, ['value_calculated'], 1000)

            if changes:
                messages.add_message(request, messages.INFO,
                                     f"U senzoru {id} bylo provedeno {changes} změn.")
                messages.add_message(request, messages.WARNING,
                                     f'Pozor: Tento výpočet je prováděn přes okénko {step_for_counter[i] + 1} záznamů. První změněná položka je až {step_for_counter[i] + 1}. v pořadí.')

    queryset = queryset.exclude(id_sensor__in=id_of_counter)

    # _________________není vzorec____________________________
    queryset = queryset.exclude(id_sensor__in=[169, 182])  # podobné jako 164? ...není vzorec
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

    # _________________ostatní (stačí přeuložit)____________________________
    changes = queryset.update(value_calculated=F('value'))
    if changes:
        messages.add_message(request, messages.INFO,
                             f"{changes} hodnot bylo pouze překopírováno beze změny.")
    cache.clear()


recompute_value.allowed_permissions = ['change']
recompute_value.short_description = "Přepočíst"

###________________end_operce____________________________

class SensorFilter(AutocompleteFilter):
    title = 'Sensor'
    field_name = 'id_sensor'

# class PointFilter(AutocompleteFilter):
#     title = 'Point'
#     field_name = 'point_number'

# class MagnitudeFilter(AutocompleteFilter):
#     title = 'Magnitude'
#     field_name = 'id_magnitude'


#_________________custom_admin____________________________

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
            else:
                sensor_id = get_params['q']

        for param in enable_for:
            if param in get_params:
                sensor_id = get_params[param]
                break

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

# _________________custom_admin____________________________
# @admin.register(Data)
class DataAdmin(AdminAdvancedFiltersMixin, ImportExportMixin, ExportActionMixin, HCHAdmin, DefaultFilterAdmin, ):
    change_list_template = 'admin/change_list_hch_cached.html'
    list_per_page = 40
    show_full_result_count = False

    # search_fields = ["id_sensor__note", 'id_sensor__pk', "id_sensor__id_magnitude__unit_cs"] #Zapíná vyhledávání ve zvolených polých
    # date_hierarchy = 'time' # zapíná vrchní hierarchické filtrování podle roků/měsíců
    list_display = ['__str__', 'time_received', 'sensor_time', 'value_with_unit', 'v_calc_4d', 'point', 'data_actions', ]
    # 'sensor_link', 'type_number', 'point_number', 'sensor_number', 'device_number', 'calculate_flow',  '__change_icon__', 'unit',  ... ]
    # list_display_links = ['time_received']  # odkaz v času
    # list_display_links = ['__change_icon__']    # odkaz v tužtičce
    list_display_links = None    # odkaz v tužtičce


    list_filter = [
        ('time', DateRangeFilter), SensorFilter, "id_sensor__id_magnitude", "id_sensor__id_point",
        # ('time', PastDateRangeFilter), 'device_number', 'sensor_number', "point_number",
    ]
    list_filter = ('time', "id_sensor__id_magnitude", "id_sensor__id_point", )
    autocomplete_fields = ['id_sensor']
    list_select_related = ('id_sensor', 'id_sensor__id_magnitude', 'id_sensor__id_point')
    actions = ExportActionMixin.actions + [recompute_value, ]
    default_filters = (
        f'time__range__gte={(datetime.today() - timedelta(days=7)):%d.%m.%Y}',
        f'time__range__lte={datetime.today():%d.%m.%Y}'
    )

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
        '''
        if it possible ruturn sensor neme (__str__) as link to list of data of sensor
        else return only sensor name
        '''
        if "id_sensor__pk" in self.full_path:
            return obj
        else:
            return mark_safe(
                '<a href="{}&id_sensor__pk__exact={}">{}</a>'.format(self.full_path, obj.id_sensor.pk, obj))

    sensor_link.short_description = "senzor"
    sensor_link.admin_order_field = "id_sensor"

    @mark_safe
    def data_actions(self, obj: Data):
        '''
        if it possible ruturn sensor neme (__str__) as link to list of data of sensor
        else return only sensor name
        '''
        pills = '<ul class="object-tools" style="margin: -5px 0; padding: 0; float: inherit">'
        pills += '<li><a href="{}"> 🖉 </a></li>'.format(
            reverse("admin:mybox_data_change", args=(obj.pk,))
        )
        if "id_sensor__pk" not in self.full_path:
            pills += '<li><a href="{}&id_sensor__pk__exact={}"> 📉 </a></li>'.format(
                    self.full_path, obj.id_sensor.pk
            )
        return pills + "</ul>"

    data_actions.short_description = "Akce"

    def sensor_time(self, obj: Data):
        return obj.time.strftime('%H:%M:%S.%f')[:-4]

    sensor_time.short_description = "čas senzoru"
    sensor_time.admin_order_field = "time"

    def value_with_unit(self, obj: Data):
        return f'{obj.value} {obj.id_sensor.id_magnitude.unit_cs}'

    value_with_unit.short_description = "Změřeno"
    value_with_unit.admin_order_field = "value"

    def unit(self, obj: Data):
        return obj.id_sensor.id_magnitude.unit_cs

    unit.short_description = "jednotka"
    unit.admin_order_field = "id_sensor__id_magnitude__unit_cs"

    def point(self, obj: Data):
        return obj.id_sensor.id_point.point_cs

    point.short_description = "pozice"
    point.admin_order_field = "id_sensor__id_point__point_cs"


