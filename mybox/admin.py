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
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from admin_auto_filters.filters import AutocompleteFilter

# from mybox.admin_data import recompute_value, HCHAdmin
from mybox.default_filter import DefaultFilterAdmin
from mybox.admin_data import DataAdmin
from mybox.models import *
# from mybox.tools import positive_sgn, Epoch, fill_date, translate_period, choose_period


admin.site.site_header = 'Vodárenský přivaděč Bedřichov'
admin.site.site_title = 'Přivaděč Bedřichov'
admin.site.index_title = "Vítejte v nahlížení do tunelu"





# _________________custom_admin____________________________


# class ChartAdmin(admin.ModelAdmin, ):
#     """
#     This is intended to be mixed with django.contrib.admin.ModelAdmin
#     https://docs.djangoproject.com/en/def/ref/contrib/admin/#modeladmin-objects
#     """
#     change_list_template = 'admin/change_list_chartjs.html'
#     change_list_parent = 'admin/import_export/change_list_import_export.html'
#     x_field = 'time'
#     y_field = 'value_calculated'
#     limit = None
#     trunc_kind = 'day',  # 'year','quarter','month','week','day','week_day','date','time','hour','minute','second'
#
#     def changelist_view(self, request, extra_context=None):
#         response = super().changelist_view(request, extra_context=extra_context)
#         try:
#             qs = response.context_data['cl'].queryset
#             get_params = request.GET
#         except (AttributeError, KeyError):
#             # messages.add_message(request, messages.ERROR, "Nevrací queryset")
#             return response
#
#         # pokud není vybrán exaktně jeden sensor
#         # if 'id_sensor__id_sensor__exact' not in get_params:
#         enable_for = ('id_sensor__id_sensor', 'id_sensor__id_sensor__exact', 'id_sensor__pk__exact', 'id_sensor', 'q')
#         if all(param not in get_params for param in enable_for):
#             messages.add_message(request, messages.INFO, "Aby bylo možné zbrazit graf, vyberte prosím poze jeden senzor.")
#             return response
#
#         if 'q' in get_params:
#             ids = qs.values('id_sensor').distinct().count()
#             if ids != 1:
#                 messages.add_message(request, messages.INFO, f"Počet zobrazených senzorů je {ids}. Aby bylo možné zbrazit graf, vyberte prosím pouze jeden.")
#                 return response
#
#         # # Aggregate new subscribers per day
#         # Vlastní perioda: https://stackoverflow.com/a/56466800/9942866
#         chart_data = qs \
#             .annotate(
#                 period=Trunc(
#                     self.x_field,
#                     *self.trunc_kind,
#                 )
#             ).values("period") \
#             .annotate(y=Avg(self.y_field), yMin=Min(self.y_field), yMax=Max(self.y_field)) \
#             .order_by("-period")
#         chart_data = chart_data[:self.limit]
#
#         cached_data = cache.get(get_params)
#         if cached_data:
#             as_json = json.dumps(cached_data, cls=DjangoJSONEncoder)
#         else:
#             as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
#             cache.set(get_params, list(chart_data), 300)
#         context = {
#             "chart_data": as_json,
#             # "parent_template": self.change_list_parent or 'change_list.html',
#             "parent_template": 'admin/import_export/change_list_import_export.html',
#         }
#         # extra_context = extra_context or context
#         response.context_data.update(context)
#         # response.context_data |= context  # Python 3.9+
#         return response


# _________________register_models____________________________

# @admin.register(ViewAllData)
# class AllDataAdmin(ChartAdmin, DefaultFilterAdmin):
#     change_list_template = 'admin/change_list_chartjs.html'
#     list_per_page = 50
#     # show_full_result_count = False
#     # paginator = TimeLimitedPaginator
#     default_filters = ('time__gte={}'.format(timezone.now().date() - timedelta(weeks=4)),)
#     date_hierarchy = 'time'
#     list_filter = [('time', DateRangeFilter), "id_sensor", "magnitude_cs", "point_number", 'device_number',
#                    'sensor_number', ]
#     # list_display = ['time','data_as_link','bin_data','point_number','type_number','sensor_number','device_number','point_number',]
#     list_display = ['id_sensor', 'time', 'data_as_link', 'calculate_flow', 'point_number', 'type_number',
#                     'sensor_as_link', 'device_number_as_link', 'point_number', ]
#
#     def calculate_flow(self, obj: Data):
#
#         unit = "ml/s"
#         if obj.id_sensor == 178:
#             k = 34.5  # pro senzor 178
#             comp_value = k * sqrt(obj.value / 1000)
#         elif obj.id_sensor == 172:
#             val = obj.value
#             # comp_value = positive_sgn(val-38)
#             # unit = val-38
#             comp_value = 82.2 * (
#                     sqrt(val / 1000) +
#                     2 * sqrt(0.5 * (positive_sgn(val - 38)) * (val - 38) / 1000) +
#                     sqrt(0.5 * (positive_sgn(val - 200)) * (val - 200) / 1000)
#             )
#         else:
#             return '{:.4} {}'.format(obj.value, obj.unit_cs)
#         return '{:.4} {}'.format(comp_value, unit)
#
#     calculate_flow.short_description = "hodnota"
#     calculate_flow.admin_order_field = "value"



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




class SensorInlineMag(admin.TabularInline):
    model = Sensor
    fk_name = "id_magnitude"
    extra = 0
    show_change_link = True
    readonly_fields = ('id_device','id_point',)
    # can_delete = False

class SensorInlinePoint(admin.TabularInline):
    model = Sensor
    extra = 0
    show_change_link = True
    readonly_fields = ('id_device','id_point',)


@admin.register(Magnitude)
class MagnitudeAdmin(ImportExportModelAdmin):
    inlines = [SensorInlineMag, ]
    search_fields = ["id_magnitude", "magnitude_cs"]


class MagnitudeInline(admin.TabularInline):
    model = Magnitude


class DataInline(admin.StackedInline):  # CompactInline //jet
    model = Data
    extra = 0
    show_change_link = True


@admin.register(Point)
class PointAdmin(ImportExportModelAdmin):
    inlines = [SensorInlinePoint, ]
    search_fields = ["id_point", "point_cs", "point_number"]


admin.site.register(Data, DataAdmin)
admin.site.register(DataOld)
admin.site.register(Device)
admin.site.register(Logs)
admin.site.register(Measurement)
admin.site.register(Uzivatel)
