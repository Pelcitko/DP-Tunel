from django.db import models
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe



class Measurement(models.Model):
    id_measurement = models.AutoField(primary_key=True, verbose_name='id')
    title_cs = models.CharField(max_length=255, blank=True, null=True)
    description_cs = models.TextField(blank=True, null=True)
    code_cs = models.CharField(unique=True, max_length=32)
    title_en = models.CharField(max_length=255, blank=True, null=True)
    code_en = models.CharField(max_length=32, blank=True, null=True)
    description_en = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title_cs

    class Meta:
        app_label = 'mybox'
        managed = False
        db_table = 'measurement'
        verbose_name = 'Měření'
        verbose_name_plural = verbose_name


class Point(models.Model):
    id_point = models.AutoField(primary_key=True)
    point_cs = models.CharField(unique=True, max_length=255)
    lattitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    radius = models.FloatField(blank=True, null=True)
    position = models.FloatField(blank=True, null=True)
    point_en = models.CharField(max_length=255, blank=True, null=True)
    point_number = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.point_cs

    class Meta:
        app_label = 'mybox'
        managed = False
        db_table = 'point'
        verbose_name = 'pozice'
        verbose_name_plural = verbose_name

class Device(models.Model):
    id_device = models.AutoField(primary_key=True)
    device_cs = models.CharField(unique=True, max_length=255)
    device_en = models.CharField(max_length=255, blank=True, null=True)
    device_number = models.IntegerField(blank=True, null=True)
    serial_number = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return "[{}] {}".format(self.device_number, self.device_cs)

    class Meta:
        app_label = 'mybox'
        managed = False
        db_table = 'device'
        verbose_name = 'Zařízení'
        verbose_name_plural = verbose_name

class Magnitude(models.Model):
    id_magnitude = models.AutoField(primary_key=True)
    magnitude_cs = models.CharField(max_length=255)
    unit_cs = models.CharField(max_length=64, blank=True, null=True)
    magnitude_en = models.CharField(max_length=255, blank=True, null=True)
    unit_en = models.CharField(max_length=64, blank=True, null=True)
    type_number = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.magnitude_cs

    class Meta:
        app_label = 'mybox'
        managed = False
        db_table = 'magnitude'
        unique_together = (('magnitude_cs', 'unit_cs'),)
        verbose_name = u'Veličina'
        verbose_name_plural = u'Veličiny'


class Sensor(models.Model):
    id_sensor = models.AutoField(primary_key=True, verbose_name='id')
    id_device = models.ForeignKey(Device, models.DO_NOTHING,
                                  db_column='id_device', related_name='id_sensor', verbose_name='Přístroj')
    id_magnitude = models.ForeignKey(Magnitude, models.DO_NOTHING,
                                     db_column='id_magnitude', related_name='id_sensor', verbose_name='Veličina')
    id_magnitude_raw = models.ForeignKey(Magnitude, models.DO_NOTHING,
                                         blank=True, null=True,
                                         db_column='id_magnitude_raw', related_name='id_sensor_raw', verbose_name='Změřená veličina')
    id_point   = models.ForeignKey(Point, models.DO_NOTHING,
                                   related_name='id_sensor', db_column='id_point', verbose_name='Bod měření')
    exponent10 = models.IntegerField()
    valid_from = models.DateTimeField()
    valid_to   = models.DateTimeField(blank=True, null=True)
    id_measurement = models.ForeignKey(Measurement, models.DO_NOTHING,
                                       related_name='id_sensor', db_column='id_measurement', verbose_name='Měření')
    datasize = models.IntegerField(blank=True, null=True)
    sensor_number = models.IntegerField(blank=True, null=True, verbose_name='senzor')
    serial_number = models.CharField(max_length=250, blank=True, null=True)
    note = models.TextField(blank=True, null=True,verbose_name='Poznámka')

    def __str__(self):      # __unicode__ on Python 2
        note = self.note[-12:] if self.note else ""
        return "{} {}m {}{}".format(
            self.id_point.point_cs,
            self.id_point.position,
            self.id_magnitude.magnitude_cs,
            note,)

    class Meta:
        app_label = 'mybox'
        managed = False
        db_table = 'sensor'
        verbose_name = 'Senzor'
        verbose_name_plural = 'Senzory'

    def get_device_as_link(self):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:mybox_device_change", args=(self.id_device_id,)),
            escape(self.id_device.device_cs),))
    get_device_as_link.allow_tags = True
    get_device_as_link.short_description = "Přístroj"

    def get_point_as_link(self):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:mybox_point_change", args=(self.id_point_id,)),
            escape(self.id_point.point_cs),))
    get_point_as_link.allow_tags = True
    get_point_as_link.short_description = "Bod měření"

    def get_magnitude_as_link(self):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:mybox_magnitude_change", args=(self.id_magnitude_id,)),
            escape(self.id_magnitude.magnitude_cs),))
    get_magnitude_as_link.allow_tags = True
    get_magnitude_as_link.short_description = "Veličina"

    def get_measurement_as_link(self):
        return mark_safe('<a href="{}">{} ({})</a>'.format(
            reverse("admin:mybox_measurement_change", args=(self.id_measurement_id,)),
            escape(self.id_measurement.code_cs),
            escape(self.id_measurement.title_cs),))
    get_measurement_as_link.allow_tags = True
    get_measurement_as_link.short_description = "Výzkum"


class Data(models.Model):
    id_data         = models.BigAutoField(primary_key=True, verbose_name='ID')
    time            = models.DateTimeField()
    time_received   = models.DateTimeField(verbose_name="Čas příchodu")
    value           = models.FloatField(verbose_name='změřeno')
    value_calculated= models.FloatField(blank=True, null=True, verbose_name='hodnota')
    value_raw       = models.FloatField(blank=True, null=True, verbose_name='změřeno (RAW)')
    bin_data        = models.BinaryField(blank=True, null=True)
    type_number     = models.IntegerField(blank=True, null=True)
    point_number    = models.IntegerField(blank=True, null=True, verbose_name='body měření')
    device_number   = models.IntegerField(blank=True, null=True, verbose_name='čísla zařízení')
    sensor_number   = models.IntegerField(blank=True, null=True, verbose_name="čísla senzorů")
    id_sensor       = models.ForeignKey(Sensor, models.DO_NOTHING, related_name='id_data', db_column='id_sensor',
                                        blank=True, null=True, verbose_name='senzor')

    def __str__(self):      # __unicode__ on Python 2
        # return str(self.id_sensor) if self.id_sensor else ''
        note = self.id_sensor.note or ""
        if len(note) > 21:
            note = "{} …{}".format(note[:7], note[-13:])
        return "{} {}".format(self.id_sensor.pk, note)

    def __change_icon__(self):      # __unicode__ on Python 2
        '''returning only change button'''
        # if "id_sensor__pk" in self.full_path: ...není tu dostupné
        #     return " 🖉 📉 "
        return "🖉 "

    __change_icon__.short_description = "Zmenit"

    class Meta:
        app_label = 'mybox'
        managed = False     # Django nebude pomocí manage.py ovlivňovat tuto tabulku
        db_table = 'data'
        verbose_name = 'Data'
        verbose_name_plural = 'Data'

    def v_calc_4d(self):
        ''' Returns the converted value from the database and its unit '''
        # return f"{(self.value_calculated or -1):.6f}".rstrip('0').rstrip('.').replace(".", ",")
        if self.value_calculated is None:
            return " ➖ "
        else:
            return f"{self.value_calculated:.4g}"[:12] + f" {self.id_sensor.id_magnitude_raw.unit_cs}"
    v_calc_4d.short_description = "Hodnota"
    v_calc_4d.admin_order_field = "value_calculated"

class DataOld(models.Model):
    id_sensor = models.IntegerField(blank=True, null=True)
    time = models.DateTimeField()
    value = models.FloatField()
    id_data = models.AutoField(primary_key=True)
    type_number = models.IntegerField(blank=True, null=True)
    point_number = models.IntegerField(blank=True, null=True)
    sensor_number = models.IntegerField(blank=True, null=True)
    bin_data = models.BinaryField(blank=True, null=True)
    device_number = models.IntegerField(blank=True, null=True)
    value_raw = models.FloatField(blank=True, null=True)

    class Meta:
        app_label = 'mybox'
        managed = False
        db_table = 'data_old'
        verbose_name = 'Starší data'
        verbose_name_plural = 'Starší data'


class Logs(models.Model):
    id_log = models.AutoField(primary_key=True)
    datetime = models.DateTimeField()
    message = models.TextField()
    level = models.CharField(max_length=10, blank=True, null=True)
    location = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        app_label = 'mybox'
        managed = False
        db_table = 'logs'
        verbose_name = 'Log'
        verbose_name_plural = 'Logy'



class Uzivatel(models.Model):
    iduzivatel = models.AutoField(primary_key=True)
    username = models.CharField(max_length=60)
    password = models.CharField(max_length=35)
    jmeno = models.CharField(max_length=50)
    prijmeni = models.CharField(max_length=50)
    email = models.CharField(max_length=90)

    class Meta:
        app_label = 'mybox'
        managed = False
        db_table = 'uzivatel'
        verbose_name = 'Uživatel'
        verbose_name_plural = 'Uživatelé'



#-------- VIEW - Není potřeba používat -------------------↴


class ViewOdbcData(models.Model):
    sensor_number = models.IntegerField(blank=True, null=True, verbose_name='senzor')
    time = models.DateTimeField(unique=True)
    value = models.FloatField()
    device_number = models.IntegerField(blank=True, null=True)

    def __str__(self):      # __unicode__ on Python 2
        return "{:.2f} {}".format(self.value, self.device_number)

    class Meta:
        app_label = 'mybox'
        managed = False     # Django nebude pomocí manage.py ovlivňovat tuto tabulku
        db_table = 'view_odbc_data'
        # unique_together = ['time', 'sensor_number'] #Django neumí složené klíče
        verbose_name = 'Pohled odbc data'
        verbose_name_plural = 'Pohled odbc data'

class ViewAllData(models.Model):
    """
    Jedná se o pohled nad všemi daty z databáze. Není materializovaný, hodnoty zde nelze měnit.
    """
    time = models.DateTimeField()
    value = models.FloatField()
    id_data = models.IntegerField(unique=True, primary_key=True)
    type_number = models.IntegerField(blank=True, null=True)
    point_number = models.IntegerField(blank=True, null=True)
    bin_data = models.BinaryField(blank=True, null=True)
    device_number = models.IntegerField(blank=True, null=True)
    exponent10 = models.IntegerField()
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField(blank=True, null=True)
    datasize = models.IntegerField(blank=True, null=True)
    sensor_number = models.IntegerField(blank=True, null=True, verbose_name='senzor')
    point_cs = models.CharField(max_length=255)
    code_cs = models.CharField(max_length=32)
    title_cs = models.CharField(max_length=255, blank=True, null=True)
    device_cs = models.CharField(max_length=255, verbose_name='přístroj')
    magnitude_cs = models.CharField(max_length=255, verbose_name='veličina')
    unit_cs = models.CharField(max_length=64, blank=True, null=True, verbose_name='jednotka')
    id_sensor = models.IntegerField('Sensor', blank=True, null=True)


    def __str__(self):      # __unicode__ on Python 2
        return "{:.2f} {}".format(10**self.exponent10*self.value, self.unit_cs)

    class Meta:
        app_label = 'mybox'
        managed = False     # Django nebude pomocí manage.py ovlivňovat tuto tabulku
        db_table = 'view_all_data'
        verbose_name = 'Všechna data'
        verbose_name_plural = 'Všechna data'

    def _get_data_as_link(self):
        return mark_safe('<a href="{}">{} {}</a>'.format(
            reverse("admin:mybox_data_change", args=(self.id_data,)),
            self.value, self.unit_cs
        ))
    _get_data_as_link.allow_tags = True
    _get_data_as_link.short_description = "Data"
    data_as_link = property(_get_data_as_link) # mělo by být asi rychlejší

    # def id_sensor_as_link(self):
    #     return mark_safe('<a href="/mybox/sensor/{}/">{} – {}</a>'
    #                      .format(self.id_sensor, self.id_sensor, self.sensor_number))
    # id_sensor_as_link.allow_tags = True
    # id_sensor_as_link.short_description = "Senzor (num)"
    # id_sensor_as_link.admin_order_field = "id_sensor"


    def sensor_as_link(self):
        return mark_safe('<a href="{}">{}/{}</a>'.format(
            reverse("admin:mybox_sensor_change", args=(self.id_sensor,)),
            self.id_sensor, self.sensor_number))
    sensor_as_link.allow_tags = True
    sensor_as_link.short_description = "Senzor/num"
    sensor_as_link.admin_order_field = "id_sensor"

    # násobně více dotazů
    def id_sensor_as_link(self):
        sen = Sensor.objects.get(pk=self.id_sensor)
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:mybox_sensor_change", args=(sen.id_sensor,)),
            sen,))
    id_sensor_as_link.allow_tags = True
    id_sensor_as_link.short_description = "Senzor"
    id_sensor_as_link.admin_order_field = "id_sensor"

    def device_number_as_link(self):
        return mark_safe('<a href="/mybox/device/{}/">{} – {}</a>'.format(
            self.device_number, self.device_number, self.device_cs))
    device_number_as_link.allow_tags = True
    device_number_as_link.short_description = "Přístroj (num)"

    def device_as_link(self):
        devices = Device.objects.get(pk=self.device_number)
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:mybox_device_change", args=(devices.id_device,)),
            devices))
    device_as_link.allow_tags = True
    device_as_link.short_description = "Přístroj"