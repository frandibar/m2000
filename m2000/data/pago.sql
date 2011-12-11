TRUNCATE TABLE pago;
LOAD DATA LOCAL INFILE '/home/fran/projects/m2000/m2000/data/pago.dat' REPLACE INTO TABLE pago (credito_id, monto, fecha, asistencia_codigo);
