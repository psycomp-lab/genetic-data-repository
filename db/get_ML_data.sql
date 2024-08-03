select m.sample_id , mt.name1, mt.name2, mt.unit, m.value from measurement m, measurement_type mt where m.measurement_id = mt.measurement_id;
