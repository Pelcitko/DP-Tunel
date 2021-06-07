CREATE INDEX time_idx ON measurement.data ("time");
CREATE INDEX id_sensor_idx ON measurement.data (id_sensor);
CREATE INDEX time_and_sensor_idx ON measurement.data USING btree("time", id_sensor);
--CREATE INDEX year_trunc_idx ON measurement.data (date_trunc('year'::text, "time"));
--CREATE INDEX day_trunc_idx ON measurement.data (date_trunc('day'::text, "time"));
--CREATE INDEX time_trunc_idx ON measurement.data USING btree(date_trunc('day', "time")::date)v

-- For foreign key:
CREATE INDEX id_point_idx ON measurement.sensor (id_point);
CREATE INDEX id_device_idx ON measurement.sensor (id_device);
CREATE INDEX id_magnitude_idx ON measurement.sensor (id_magnitude);
CREATE INDEX id_measurement_idx ON measurement.sensor (id_measurement);
