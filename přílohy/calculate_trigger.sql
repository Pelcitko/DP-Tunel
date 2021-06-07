CREATE OR REPLACE FUNCTION measurement.calculate_flow_from_handle(
    base_step int, -- 1 pro sklopku s jednou nádobkou, 2 pro dvouramenou
	new_count double precision,
	new_tim timestamp without time zone,
	pre_count double precision,
	pre_tim timestamp without time zone
)
    RETURNS double precision
    LANGUAGE 'plpgsql'

AS $BODY$
BEGIN
--podmínka při přetečení, "z velkého čísla v dalším kroku nebo po výpadku na nulu."
  IF new_count <= pre_count THEN
    pre_count := new_count - base_step;
  END IF;
  RETURN
 	(new_count - pre_count) / extract(epoch from (new_tim - pre_tim));
END
$BODY$;

CREATE OR REPLACE FUNCTION
    measurement.calculate_flow_from_height(h_surface double precision, h_hole double precision)
    RETURNS double precision
    LANGUAGE 'plpgsql'

AS $BODY$
BEGIN
  IF h_surface <= h_hole THEN
    RETURN 0;
  END IF;
  RETURN sqrt((h_surface - h_hole) / 1000);
END
$BODY$;

CREATE OR REPLACE FUNCTION measurement.calculate_value_trigger()
    RETURNS trigger
    LANGUAGE 'plpgsql'

AS $BODY$
BEGIN

  IF NEW.time is NULL THEN
    NEW.time := NOW();
  END IF;
  IF NEW.value_calculated IS NULL THEN
	CASE NEW.id_sensor

    	WHEN 164 THEN NEW.value_calculated := (
--			neznameK * sqrt(NEW.value/1000)
			null
		);

    	WHEN 172 THEN NEW.value_calculated := 82.2 * (
			 measurement.calculate_flow_from_height(NEW.value, 0)
			 + 2 * measurement.calculate_flow_from_height(NEW.value, 38)
			 + measurement.calculate_flow_from_height(NEW.value, 200)
		);

    	WHEN 178 THEN NEW.value_calculated := 34.5 * (
			sqrt(NEW.value/1000)
			-- measurement.calculate_flow_from_height(NEW.value, 0)
		);
		-- pozor, data jsou duplikovaná, z toho důvodu je krok (offset) 2x větší
		WHEN 168 THEN NEW.value_calculated := 15 * measurement.calculate_flow_from_handle(
			4, NEW.value, NEW.time,
			(select "value" from measurement.data
			 	where id_sensor = 168 order by id_data desc limit 1 offset 3),
			(select "time" from measurement.data
			 	where id_sensor = 168 order by id_data desc limit 1 offset 3)
			);

    	WHEN 184 THEN NEW.value_calculated := 5.66 * measurement.calculate_flow_from_handle(
			2, NEW.value, NEW.time,
			(select "value" from measurement.data
			 	where id_sensor = 184 order by id_data desc limit 1 offset 1),
			(select "time" from measurement.data
			 	where id_sensor = 184 order by id_data desc limit 1 offset 1)
			);

    	WHEN 187 THEN NEW.value_calculated := (
			7.95 * 10^(-5) * (310.4 - NEW.value)^2.3
		);

    	ELSE NEW.value_calculated := NEW.value;
	END case;
  END IF;
  RETURN NEW;
END
$BODY$;

ALTER FUNCTION measurement.calculate_value_trigger()
    OWNER TO postgres;

COMMENT ON FUNCTION measurement.calculate_value_trigger()
    IS 'Vypočítá skutečnou hodnotu měřené veličiny';