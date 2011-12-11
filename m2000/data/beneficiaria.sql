TRUNCATE TABLE beneficiaria;
LOAD DATA LOCAL INFILE '/home/fran/projects/m2000/m2000/data/beneficiaria.dat' REPLACE INTO TABLE beneficiaria (id,barrio_id,nombre,apellido,grupo,fecha_alta,activa,fecha_baja,comentarios,dni,fecha_nac,domicilio,estado_civil,telefono);
