# Generated by Django 3.1.7 on 2021-03-17 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Data',
            fields=[
                ('time', models.DateTimeField()),
                ('value', models.FloatField()),
                ('id_data', models.AutoField(primary_key=True, serialize=False)),
                ('type_number', models.IntegerField(blank=True, null=True)),
                ('point_number', models.IntegerField(blank=True, null=True)),
                ('sensor_number', models.IntegerField(blank=True, null=True)),
                ('bin_data', models.BinaryField(blank=True, null=True)),
                ('device_number', models.IntegerField(blank=True, null=True)),
                ('value_raw', models.FloatField(blank=True, null=True)),
                ('time_received', models.DateTimeField(verbose_name='Čas příchodu')),
            ],
            options={
                'verbose_name': 'Data',
                'verbose_name_plural': 'Data',
                'db_table': 'data',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DataOld',
            fields=[
                ('id_sensor', models.IntegerField(blank=True, null=True)),
                ('time', models.DateTimeField()),
                ('value', models.FloatField()),
                ('id_data', models.AutoField(primary_key=True, serialize=False)),
                ('type_number', models.IntegerField(blank=True, null=True)),
                ('point_number', models.IntegerField(blank=True, null=True)),
                ('sensor_number', models.IntegerField(blank=True, null=True)),
                ('bin_data', models.BinaryField(blank=True, null=True)),
                ('device_number', models.IntegerField(blank=True, null=True)),
                ('value_raw', models.FloatField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Starší data',
                'verbose_name_plural': 'Starší data',
                'db_table': 'data_old',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id_device', models.AutoField(primary_key=True, serialize=False)),
                ('device_cs', models.CharField(max_length=255, unique=True)),
                ('device_en', models.CharField(blank=True, max_length=255, null=True)),
                ('device_number', models.IntegerField(blank=True, null=True)),
                ('serial_number', models.CharField(blank=True, max_length=250, null=True)),
            ],
            options={
                'verbose_name': 'Typ senzoru',
                'verbose_name_plural': 'Typy senzorů',
                'db_table': 'device',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Logs',
            fields=[
                ('id_log', models.AutoField(primary_key=True, serialize=False)),
                ('datetime', models.DateTimeField()),
                ('message', models.TextField()),
                ('level', models.CharField(blank=True, max_length=10, null=True)),
                ('location', models.CharField(blank=True, max_length=250, null=True)),
            ],
            options={
                'verbose_name': 'Log',
                'verbose_name_plural': 'Logy',
                'db_table': 'logs',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Magnitude',
            fields=[
                ('id_magnitude', models.AutoField(primary_key=True, serialize=False)),
                ('magnitude_cs', models.CharField(max_length=255)),
                ('unit_cs', models.CharField(blank=True, max_length=64, null=True)),
                ('magnitude_en', models.CharField(blank=True, max_length=255, null=True)),
                ('unit_en', models.CharField(blank=True, max_length=64, null=True)),
                ('type_number', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Veličina',
                'verbose_name_plural': 'Veličiny',
                'db_table': 'magnitude',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Measurement',
            fields=[
                ('id_measurement', models.AutoField(primary_key=True, serialize=False)),
                ('title_cs', models.CharField(blank=True, max_length=255, null=True)),
                ('description_cs', models.TextField(blank=True, null=True)),
                ('code_cs', models.CharField(max_length=32, unique=True)),
                ('title_en', models.CharField(blank=True, max_length=255, null=True)),
                ('code_en', models.CharField(blank=True, max_length=32, null=True)),
                ('description_en', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Měření',
                'verbose_name_plural': 'Měření',
                'db_table': 'measurement',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id_point', models.AutoField(primary_key=True, serialize=False)),
                ('point_cs', models.CharField(max_length=255, unique=True)),
                ('lattitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('radius', models.FloatField(blank=True, null=True)),
                ('position', models.FloatField(blank=True, null=True)),
                ('point_en', models.CharField(blank=True, max_length=255, null=True)),
                ('point_number', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Body měření',
                'verbose_name_plural': 'Bod měření',
                'db_table': 'point',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id_sensor', models.AutoField(primary_key=True, serialize=False, verbose_name='id')),
                ('exponent10', models.IntegerField()),
                ('valid_from', models.DateTimeField()),
                ('valid_to', models.DateTimeField(blank=True, null=True)),
                ('datasize', models.IntegerField(blank=True, null=True)),
                ('sensor_number', models.IntegerField(blank=True, null=True, verbose_name='senzor')),
                ('id_magnitude_raw', models.IntegerField(blank=True, null=True)),
                ('serial_number', models.CharField(blank=True, max_length=250, null=True)),
                ('note', models.TextField(blank=True, null=True, verbose_name='Poznámka')),
            ],
            options={
                'verbose_name': 'Senzor',
                'verbose_name_plural': 'Senzory',
                'db_table': 'sensor',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Uzivatel',
            fields=[
                ('iduzivatel', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=60)),
                ('password', models.CharField(max_length=35)),
                ('jmeno', models.CharField(max_length=50)),
                ('prijmeni', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=90)),
            ],
            options={
                'verbose_name': 'Uživatel',
                'verbose_name_plural': 'Uživatelé',
                'db_table': 'uzivatel',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ViewAllData',
            fields=[
                ('time', models.DateTimeField()),
                ('value', models.FloatField()),
                ('id_data', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('type_number', models.IntegerField(blank=True, null=True)),
                ('point_number', models.IntegerField(blank=True, null=True)),
                ('bin_data', models.BinaryField(blank=True, null=True)),
                ('device_number', models.IntegerField(blank=True, null=True)),
                ('exponent10', models.IntegerField()),
                ('valid_from', models.DateTimeField()),
                ('valid_to', models.DateTimeField(blank=True, null=True)),
                ('datasize', models.IntegerField(blank=True, null=True)),
                ('sensor_number', models.IntegerField(blank=True, null=True, verbose_name='senzor')),
                ('point_cs', models.CharField(max_length=255)),
                ('code_cs', models.CharField(max_length=32)),
                ('title_cs', models.CharField(blank=True, max_length=255, null=True)),
                ('device_cs', models.CharField(max_length=255, verbose_name='přístroj')),
                ('magnitude_cs', models.CharField(max_length=255)),
                ('unit_cs', models.CharField(blank=True, max_length=64, null=True)),
                ('id_sensor', models.IntegerField(blank=True, null=True, verbose_name='Sensor')),
            ],
            options={
                'verbose_name': 'Všechna data',
                'verbose_name_plural': 'Všechna data',
                'db_table': 'view_all_data',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ViewOdbcData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sensor_number', models.IntegerField(blank=True, null=True, verbose_name='senzor')),
                ('time', models.DateTimeField(unique=True)),
                ('value', models.FloatField()),
                ('device_number', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Pohled odbc data',
                'verbose_name_plural': 'Pohled odbc data',
                'db_table': 'view_odbc_data',
                'managed': False,
            },
        ),
    ]
