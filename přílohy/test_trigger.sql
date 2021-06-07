-- Vzorové testování senzoru 184
INSERT INTO measurement.data(id_sensor, device_number, sensor_number,  time, time_received, value, value_raw) 
	   VALUES (184, 226, 0, NOW(), NOW(), 0, 1);

SELECT pg_sleep(5*60);	   

INSERT INTO measurement.data(id_sensor, device_number, sensor_number,  time, time_received, value, value_raw) 
	   VALUES (184, 226, 0, NOW(), NOW(), 1, 1);
	   
select id_sensor, time, value, value_raw, value_calculated from measurement.data 
	where id_sensor = 184 order by id_data desc limit 6