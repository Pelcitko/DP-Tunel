import sys
from datetime import timedelta
from math import sqrt
import json

from daterangefilter.filters import PastDateRangeFilter
from django.contrib import admin
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator
from django.db import transaction, connection, OperationalError
from django.db.models import Count, ExpressionWrapper, Avg, DateTimeField, Min, Max
from django.db.models.functions import TruncDay, Trunc
from django.utils import timezone
from django.utils.functional import cached_property
from import_export.admin import ImportExportMixin, ImportExportModelAdmin, ExportMixin, ExportActionMixin
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

from mybox.models import *
from mybox.tools import positive_sgn
# Register your models here.

admin.site.site_header = 'Vodárenský přivaděč Bedřichov'
admin.site.site_title = 'Přivaděč Bedřichově'
admin.site.index_title = "Výtejte v nahlžínení do tunelu"

#_________________custom_admin____________________________

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
        except: pass
        return super(DefaultFilterAdmin, self).changelist_view(request, *args, **kwargs)


class TimeLimitedPaginator(Paginator):
    """
    Paginator that enforces a timeout on the count operation.
    If the operations times out, a fake bogus value is
    returned instead.
    """
    @cached_property
    def count(self):
        # We set the timeout in a db transaction to prevent it from
        # affecting other transactions.
        if self.object_list.db is 'mybox':
            try:
                with connection.cursor() as cursor:
                    cursor.execute('SET LOCAL statement_timeout TO 1000;')
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

class ChartAdmin(ExportActionMixin, admin.ModelAdmin,):
    """
    This is intended to be mixed with django.contrib.admin.ModelAdmin
    https://docs.djangoproject.com/en/def/ref/contrib/admin/#modeladmin-objects
    """
    change_list_template = 'admin/change_list_chartjs.html'
    change_list_parent = 'admin/import_export/change_list_import_export.html'
    x_field = 'time'
    limit = None
    trunc_kind = 'day',  # 'year','quarter','month','week','day','week_day','date','time','hour','minute','second'

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            qs = response.context_data['cl'].queryset
            get_params = request.GET
        except (AttributeError, KeyError):
            return response

        # pokud není vybrán exaktně jeden sensor
        # if 'id_sensor__id_sensor__exact' not in get_params:
        enable_for = ('id_sensor__id_sensor__exact', 'id_sensor', )
        if all(param not in get_params for param in enable_for):
            # return response
            return super().changelist_view(request, extra_context)

        # # Aggregate new subscribers per day
        # Vlastní perioda: https://stackoverflow.com/a/56466800/9942866
        chart_data = qs\
            .annotate(
                period=Trunc(
                    self.x_field,
                    *self.trunc_kind,
                )
                    )\
            .values("period")\
            .annotate(y=Avg("value"), yMin=Min("value"), yMax=Max("value"))\
            .order_by("-period")
        chart_data = chart_data[:self.limit]

        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        context = {
            "chart_data": as_json,
            "parent_template": self.change_list_parent or 'change_list.html',
        }
        extra_context = extra_context or context
        # response.context_data.update(context)
        # response.context_data |= context  # Python 3.9+
        # return response
        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context)


#_________________register_models____________________________

@admin.register(ViewAllData)
class AllDataAdmin(ChartAdmin, DefaultFilterAdmin):
    # x_field = 'time'
    # change_list_template = 'admin/change_list_chartjs.html'
    list_per_page = 50
    # show_full_result_count = False
    # paginator = TimeLimitedPaginator
    default_filters = ('time__gte={}'.format(timezone.now().date()-timedelta(weeks=100)),)
    date_hierarchy = 'time'
    list_filter = [('time', DateRangeFilter), "id_sensor", "magnitude_cs", "point_number", 'device_number', 'sensor_number', ]
    # list_display = ['time','data_as_link','bin_data','point_number','type_number','sensor_number','device_number','point_number',]
    list_display = ['id_sensor', 'time', 'data_as_link', 'calculate_flow', 'point_number', 'type_number',
                    'id_sensor_as_link', 'sensor_as_link',  'device_number_as_link', 'point_number', ]


    def calculate_flow(self, obj:Data):

        unit = "ml/s"
        if   obj.id_sensor == 178:
            k = 34.5 #pro senzor 178
            comp_value = k * sqrt(obj.value/1000)
        elif obj.id_sensor == 172:
            val = obj.value
            # comp_value = positive_sgn(val-38)
            # unit = val-38
            comp_value = 82.2 * (
                    sqrt(val/1000) +
                    2*sqrt(0.5*(positive_sgn(val-38))*(val-38)/1000) +
                    sqrt(0.5*(positive_sgn(val-200))*(val-200)/1000)
            )
        else:
            return '{:.4} {}'.format(obj.value, obj.unit_cs)
        return '{:.4} {}'.format(comp_value, unit)
    calculate_flow.short_description = "hodnota"
    calculate_flow.admin_order_field = "value"


@admin.register(Data)
class DataAdmin(ChartAdmin, DefaultFilterAdmin):
    # change_list_template = 'admin/change_list_chartjs.html'
    list_per_page = 50
    # show_full_result_count = False
    # paginator = TimeLimitedPaginator
    default_filters = ('time__gte={}'.format(timezone.now().date()-timedelta(weeks=100)),)
    date_hierarchy = 'time'
    list_display = ['id_sensor', 'time', 'value', 'unit', 'calculate_flow', 'type_number', 'point_number',
                    'sensor_number', 'device_number', ]
    list_filter = [
        ('time', DateRangeFilter), "id_sensor", "id_sensor__id_magnitude", "point_number",
        # ('time', PastDateRangeFilter), 'device_number', 'sensor_number',
                  ]
    # list_select_related = ('id_sensor',) # -[list_per_page] query
    list_select_related = ('id_sensor', 'id_sensor__id_magnitude') # -[list_per_page] query



    def unit(self, obj:Data):
        return obj.id_sensor.id_magnitude.unit_cs
    unit.short_description = "jednotka"
    unit.admin_order_field = "id_sensor__id_magnitude__unit_cs"

    def calculate_flow(self, obj:Data):

        unit = "ml/s"
        if   obj.id_sensor.id_sensor == 178:
            k = 34.5 #pro senzor 178
            comp_value = k * sqrt(obj.value/1000)
        elif obj.id_sensor.id_sensor == 172:
            val = obj.value
            # comp_value = positive_sgn(val-38)
            # unit = val-38
            comp_value = 82.2 * (
                    sqrt(val/1000) +
                    2*sqrt(0.5*(positive_sgn(val-38))*(val-38)/1000) +
                    sqrt(0.5*(positive_sgn(val-200))*(val-200)/1000)
            )
        else:
            return '{:.4} {}'.format(obj.value, obj.id_sensor.id_magnitude.unit_cs)
        return '{:.4} {}'.format(comp_value, unit)
    calculate_flow.short_description = "hodnota"
    calculate_flow.admin_order_field = "value"


class SensorInline(admin.StackedInline):
    model = Sensor
    extra = 0
    show_change_link = True


@admin.register(Magnitude)
class SensorAdmin(ImportExportModelAdmin):
    inlines = [SensorInline, ]


class MagnitudeInline(admin.TabularInline):
    model = Magnitude


class DataInline(admin.StackedInline):  # CompactInline //jet
    model = Data
    extra = 0
    show_change_link = True


@admin.register(Sensor)
class SensorAdmin(ImportExportMixin, DefaultFilterAdmin):
    change_list_template = 'admin/changelist_with_model.html'
    list_filter   = ['id_sensor', 'id_device', 'id_magnitude', 'id_point', 'id_measurement', ]
    list_select_related = ('id_device', 'id_magnitude', 'id_point', 'id_measurement', )
    # list_select_related = ('id_sensor','id_sensor__id_point')
    # list_select_related = ('id_sensor__id_point',)
    list_per_page = 25
    show_full_result_count = False
    # paginator = TimeLimitedPaginator
    list_display = ['id_sensor', 'sensor_number', 'note', 'get_device_as_link',
                    'get_magnitude_as_link', 'get_point_as_link', 'get_measurement_as_link', ]
    # inlines = [DataInline, ]


# admin.site.register(Data)
admin.site.register(DataOld)
# admin.site.register(ViewAllData)
admin.site.register(Device)
admin.site.register(Logs)
# admin.site.register(Magnitude)
admin.site.register(Measurement)
admin.site.register(Point)
# admin.site.register(Sensor)
admin.site.register(Uzivatel)