USE m2000;

DELIMITER $$
DROP FUNCTION IF EXISTS `m2000`.`cuotas_teorico`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `cuotas_teorico`(fecha DATE, fecha_entrega DATE, cuotas INTEGER) RETURNS int(11)
BEGIN
    SET @mas_catorce = ADDDATE(fecha_entrega, 14);
    SET @res = (fecha - @mas_catorce) / 7;
    RETURN IF(@res > cuotas, cuotas, @res);
END$$
DELIMITER ;

CREATE OR REPLACE VIEW 100_credito_pagos AS
-- Todos los pagos para cada credito.
-- Aquellos creditos que no tienen pago, muestran la fecha de entrega como fecha de pago y el monto en 0
SELECT 
    IF(pago.fecha IS NULL, credito.fecha_entrega, pago.fecha) AS fecha_pago_o_entrega,
    credito.beneficiaria_id,
    credito.id AS credito_id,
    IFNULL(monto, 0) AS monto,
    credito.fecha_finalizacion
FROM 
    credito
    LEFT JOIN pago ON credito.id = pago.credito_id;

CREATE OR REPLACE VIEW 100_credito_total_pagos AS
-- Para cada credito activo, el total de pagos a una determinada fecha
SELECT
    parametro.fecha,
    v100.credito_id,
    SUM(v100.monto) AS total_pagos
FROM 
    parametro,
    100_credito_pagos AS v100
WHERE 
    v100.fecha_pago_o_entrega <= parametro.fecha
    AND (v100.fecha_finalizacion > parametro.fecha OR (v100.fecha_finalizacion IS NULL))
GROUP BY 
    parametro.fecha,
    v100.credito_id;

CREATE OR REPLACE VIEW 101_indicadores AS
SELECT 
    beneficiaria.id AS beneficiaria_id,
    beneficiaria.comentarios,
    barrio.nombre AS barrio,
    CONCAT(beneficiaria.nombre, " ", beneficiaria.apellido) AS beneficiaria,
    credito.nro_credito,
    credito.fecha_entrega,
    ADDDATE(credito.fecha_entrega, 14) AS fecha_inicio,
    ADDDATE(credito.fecha_entrega, cuotas * 7) AS fecha_cancelacion,
    credito.saldo_anterior,
    credito.deuda_total / (1 + credito.tasa_interes) AS capital,
    credito.tasa_interes,
    cartera.nombre AS cartera,
    credito.deuda_total * credito.tasa_interes / (1 + credito.tasa_interes) AS monto_aporte,
    credito.deuda_total,
    credito.cuotas,
    credito.deuda_total / credito.cuotas AS cuota_calculada,
    TP.total_pagos * cuotas / credito.deuda_total AS cuotas_pagadas,
    TP.total_pagos / credito.deuda_total AS cuotas_pagadas_porcent,
    cuotas_teorico(parametro.fecha, credito.fecha_entrega, credito.cuotas) AS cuotas_teorico,       
    cuotas_teorico(parametro.fecha, credito.fecha_entrega, credito.cuotas) / credito.cuotas AS cuotas_teorico_porcent,
    cuotas_teorico(parametro.fecha, credito.fecha_entrega, credito.cuotas) - (TP.total_pagos * cuotas / credito.deuda_total) AS diferencia_cuotas,
    credito.deuda_total - TP.total_pagos AS saldo,
	TP.total_pagos AS monto_pagado,
	credito.deuda_total * cuotas_teorico(parametro.fecha, credito.fecha_entrega, credito.cuotas) / credito.cuotas AS monto_teorico,
    credito.deuda_total * cuotas_teorico(parametro.fecha, credito.fecha_entrega, credito.cuotas) / credito.cuotas - TP.total_pagos AS diferencia_monto
FROM 
    parametro, 
	credito
	INNER JOIN beneficiaria ON credito.beneficiaria_id = beneficiaria.id
	INNER JOIN 100_credito_total_pagos AS TP on credito.id = TP.credito_id
	INNER JOIN barrio ON beneficiaria.barrio_id = barrio.id
	INNER JOIN cartera ON credito.cartera_id = cartera.id
WHERE 
    beneficiaria.activa = TRUE
	AND credito.deuda_total != 0
	AND credito.fecha_entrega <= parametro.fecha
	AND (credito.fecha_finalizacion > parametro.fecha OR credito.fecha_finalizacion IS NULL);

CREATE OR REPLACE VIEW 102_indicadores AS
-- Es el reporte 'Indicadores'
-- Para cada beneficiaria activa, el estado de sus creditos.
SELECT 
    beneficiaria_id,
    comentarios,
    barrio,
    beneficiaria,
    nro_credito,
    fecha_entrega,
    fecha_inicio,
    fecha_cancelacion,
    saldo_anterior,
    capital,
    tasa_interes,
    cartera,
    monto_aporte,
    deuda_total,
    cuotas,
    cuota_calculada,
    cuotas_pagadas,
    cuotas_pagadas_porcent,
    cuotas_teorico,       
    cuotas_teorico_porcent,
    diferencia_cuotas,
    saldo,
	monto_pagado,
	monto_teorico,
    diferencia_monto,
    estado_credito.descripcion AS estado
FROM
    101_indicadores 
    JOIN estado_credito 
    ON 101_indicadores.diferencia_cuotas > estado_credito.cuotas_adeudadas_min 
    AND 101_indicadores.diferencia_cuotas <= estado_credito.cuotas_adeudadas_max;

CREATE OR REPLACE VIEW 700_recaudacion_x_cartera AS
-- Es el reporte 'Recaudacion Mensual'
-- Para cada cartera, el total de pagos entre fechas, agrupados por barrio y tasa de interes
SELECT 
    cartera.nombre AS cartera, 
    credito.tasa_interes, 
    SUM(pago.monto) AS recaudacion, 
    barrio.nombre AS barrio
FROM 
    credito
	INNER JOIN pago ON credito.id = pago.credito_id
	INNER JOIN cartera ON credito.cartera_id = cartera.id
	INNER JOIN beneficiaria ON credito.beneficiaria_id = beneficiaria.id
	INNER JOIN barrio ON beneficiaria.barrio_id = barrio.id
WHERE 
	pago.fecha >= (SELECT MIN(fecha) from fecha) 
	AND pago.fecha <= (SELECT MAX(fecha) from fecha) 
GROUP BY 
    cartera.nombre, 
	credito.tasa_interes, 
	barrio.nombre;

CREATE OR REPLACE VIEW 403_creditos_entregados AS
-- Es el reporte 'Cartera - Cheques Entregados'
SELECT 
    CONCAT(beneficiaria.nombre, " ", beneficiaria.apellido) AS beneficiaria,
	barrio.nombre AS barrio, 
	cartera.nombre AS cartera, 
	credito.nro_credito, 
	credito.fecha_entrega, 
	SUM(credito.prestamo) AS monto_prestamo,
	SUM(credito.monto_cheque) AS monto_cheque
FROM 
    credito
	INNER JOIN cartera ON credito.cartera_id = cartera.id
	INNER JOIN beneficiaria ON credito.beneficiaria_id = beneficiaria.id
	INNER JOIN barrio ON beneficiaria.barrio_id = barrio.id
GROUP BY 
    CONCAT(beneficiaria.nombre, " ", beneficiaria.apellido),
	barrio.nombre, 
	cartera.nombre, 
	credito.nro_credito, 
	credito.fecha_entrega;

CREATE OR REPLACE VIEW 700_recaudacion_x_barrio AS
-- Total de pagos por semana y barrio, entre fechas.
SELECT 
    YEARWEEK(pago.fecha,1) AS semana,  -- 1 porque la semana arranca los lunes
	barrio.id AS barrio_id,
    barrio.nombre as barrio_nombre, -- para evitar un nuevo join en otros views
	SUM(monto) AS recaudacion
FROM 
    barrio 
	INNER JOIN beneficiaria ON barrio.id = beneficiaria.barrio_id 
	INNER JOIN credito ON beneficiaria.id = credito.beneficiaria_id
	INNER JOIN pago ON credito.id = pago.credito_id
WHERE 
    pago.fecha BETWEEN (SELECT MIN(fecha) FROM fecha) AND (SELECT MAX(fecha) FROM fecha)
GROUP BY 
    YEARWEEK(pago.fecha,1),
    barrio.id;

CREATE OR REPLACE VIEW recaudacion_real_x_barrio AS
SELECT 
    MAKEDATE(MID(v700.semana, 1, 4), MID(v700.semana, 5, 2) * 7) AS fecha,	 -- MAKEDATE(year, day of year)
	v700.barrio_nombre AS barrio,
	v700.recaudacion
FROM 
    700_recaudacion_x_barrio AS v700;

CREATE OR REPLACE VIEW 701_recaudacion_potencial_x_barrio AS
-- Para todos los creditos activos, mostrar por fecha y barrio, el monto total a pagar
SELECT 
    YEARWEEK(fecha.fecha,1) AS semana,
	barrio.id AS barrio_id,
	SUM(credito.deuda_total / credito.cuotas) AS recaudacion_potencial
FROM 
    fecha, 
	barrio 
	INNER JOIN beneficiaria ON barrio.id = beneficiaria.barrio_id 
	INNER JOIN credito ON beneficiaria.id = credito.beneficiaria_id
WHERE 
    ADDDATE(credito.fecha_entrega, 14) <= fecha.fecha
	AND (credito.fecha_finalizacion > fecha.fecha OR credito.fecha_finalizacion IS NULL)
GROUP BY 
    YEARWEEK(fecha.fecha,1),
	barrio.id;

CREATE OR REPLACE VIEW 702_recaudacion_potencial_x_barrio AS
-- Es el reporte 'Recaudacion Potencial Total por barrio'
SELECT 
    MAKEDATE(MID(v700.semana, 1, 4), MID(v700.semana, 5, 2) * 7) AS fecha,	 -- MAKEDATE(year, day of year)
	barrio.nombre AS barrio,
	v700.recaudacion,
	v701.recaudacion_potencial,
	v700.recaudacion / v701.recaudacion_potencial AS porcentaje
FROM 
    700_recaudacion_x_barrio AS v700
	INNER JOIN 701_recaudacion_potencial_x_barrio AS v701 ON v700.barrio_id = v701.barrio_id AND v700.semana = v701.semana
	INNER JOIN barrio ON v700.barrio_id = barrio.id;

CREATE OR REPLACE VIEW 701_recaudacion_potencial AS
SELECT
    YEARWEEK(fecha.fecha,1) AS semana,
	SUM(credito.deuda_total / credito.cuotas) AS recaudacion_potencial
FROM 
     fecha, credito
WHERE 
    ADDDATE(credito.fecha_entrega, 14) <= fecha.fecha
	AND (credito.fecha_finalizacion > fecha.fecha OR credito.fecha_finalizacion IS NULL)
GROUP BY 
    YEARWEEK(fecha.fecha,1);

CREATE OR REPLACE VIEW 700_recaudacion AS
SELECT 
    YEARWEEK(pago.fecha,1) AS semana,
	cartera.id AS cartera_id, 
	credito.tasa_interes, 
	SUM(pago.monto) AS recaudacion
FROM 
    cartera 
	INNER JOIN credito ON cartera.id = credito.cartera_id
	INNER JOIN pago ON credito.id = pago.credito_id
WHERE 
    pago.fecha BETWEEN (SELECT MIN(fecha) FROM fecha) AND (SELECT MAX(fecha) FROM fecha)
GROUP BY 
    YEARWEEK(pago.fecha,1),
	cartera.id,
	credito.tasa_interes;

CREATE OR REPLACE VIEW recaudacion_real_total AS
SELECT 
    MAKEDATE(MID(v700.semana, 1, 4), MID(v700.semana, 5, 2) * 7) AS fecha,	 -- MAKEDATE(year, day of year)
	cartera.nombre AS cartera, 
	v700.tasa_interes, 
	v700.recaudacion
FROM 
    700_recaudacion AS v700 
    INNER JOIN cartera ON v700.cartera_id = cartera.id;

CREATE OR REPLACE VIEW 702_recaudacion_potencial AS
-- Es el reporte 'Recaudacion Potencial'
SELECT 
    MAKEDATE(MID(v700.semana, 1, 4), MID(v700.semana, 5, 2) * 7) AS fecha,	 -- MAKEDATE(year, day of year)
	v700.recaudacion, 
	v701.recaudacion_potencial, 
	v700.recaudacion / v701.recaudacion_potencial AS porcentaje
FROM 
    701_recaudacion_potencial AS v701
	INNER JOIN 700_recaudacion AS v700 ON v701.semana = v700.semana;

CREATE OR REPLACE VIEW pagos_credito AS
-- Para cada credito, el total de pagos
SELECT
    v100.credito_id,
    SUM(v100.monto) AS monto
FROM 
    100_credito_pagos AS v100
GROUP BY 
    v100.credito_id;

CREATE OR REPLACE VIEW 402_creditos_activos AS
-- Es el reporte 'Creditos activos'
SELECT
    beneficiaria.id AS beneficiaria_id,
    credito.id AS credito_id,
    beneficiaria.comentarios, 
    CONCAT(beneficiaria.nombre, " ", beneficiaria.apellido) as beneficiaria,
    barrio.nombre AS barrio, 
    credito.nro_credito, 
    credito.prestamo, 
    credito.fecha_entrega, 
    credito.deuda_total - pagos_credito.monto AS saldo
FROM 
    barrio 
    INNER JOIN beneficiaria ON barrio.id = beneficiaria.barrio_id
    INNER JOIN credito ON beneficiaria.id = credito.beneficiaria_id
    INNER JOIN pagos_credito ON credito.id = pagos_credito.credito_id
WHERE
    credito.fecha_finalizacion IS NULL;

CREATE OR REPLACE VIEW 901_perdida_x_incobrable AS
-- Es el reporte 'Pérdida por Incobrable'
SELECT 
    beneficiaria.id AS beneficiaria_id,
    credito.id AS credito_id,
    beneficiaria.comentarios, 
    CONCAT(beneficiaria.nombre, " ", beneficiaria.apellido) as beneficiaria,
    beneficiaria.fecha_baja,
    barrio.nombre AS barrio,
    credito.nro_credito,
    credito.fecha_finalizacion,
    credito.comentarios AS comentarios_baja,
    credito.fecha_entrega, 
    credito.prestamo,
    credito.deuda_total,
    credito.deuda_total - pagos_credito.monto AS saldo
FROM 
    barrio 
    INNER JOIN beneficiaria ON barrio.id = beneficiaria.barrio_id
    INNER JOIN credito ON beneficiaria.id = credito.beneficiaria_id
    INNER JOIN pagos_credito ON credito.id = pagos_credito.credito_id
WHERE
    credito.fecha_finalizacion IS NOT NULL
    AND credito.comentarios IS NOT NULL;

CREATE OR REPLACE VIEW creditos_finalizados_sin_saldar AS
-- Es el reporte 'Creditos finalizados sin saldar'
SELECT 
    beneficiaria.id AS beneficiaria_id,
    credito.id AS credito_id,
    beneficiaria.comentarios, 
    CONCAT(beneficiaria.nombre, " ", beneficiaria.apellido) as beneficiaria,
    barrio.nombre AS barrio,
    credito.nro_credito,
    credito.fecha_finalizacion,
    credito.fecha_entrega, 
    credito.prestamo,
    credito.deuda_total,
    credito.deuda_total - pagos_credito.monto AS saldo
FROM 
    barrio 
    INNER JOIN beneficiaria ON barrio.id = beneficiaria.barrio_id
    INNER JOIN credito ON beneficiaria.id = credito.beneficiaria_id
    INNER JOIN pagos_credito ON credito.id = pagos_credito.credito_id
WHERE
    credito.fecha_finalizacion IS NOT NULL
    AND credito.deuda_total - pagos_credito.monto > 1; -- 1 en vez de 0 x razones de redondeo

-- -- REVISAR por ahora no la necesito
-- CREATE OR REPLACE VIEW 210_pagos AS
-- -- Todos los pagos con fecha >= fecha_desde de los creditos activos
-- SELECT 
--        credito.beneficiaria_id, 
--        pago.credito_id,
--        YEARWEEK(pago.fecha,1) AS semana,
--        SUM(pago.monto) AS pago
-- FROM 
--      pago
--      INNER JOIN credito ON pago.credito_id = credito.id
-- WHERE 
--       pago.fecha >= (SELECT MIN(fecha) FROM fecha)
--       AND (credito.fecha_finalizacion > (SELECT MAX(fecha) FROM fecha) OR credito.fecha_finalizacion IS NULL)
-- GROUP BY
--        credito.beneficiaria_id, 
--        pago.credito_id,
--        WEEKOFYEAR(pago.fecha),
--        YEAR(pago.fecha);

-- CREATE OR REPLACE VIEW 803_asistencia AS
-- -- Ex 803 asistencia
-- -- Para aquellos creditos activos, ??
-- SELECT 
--        fecha.fecha,
--        barrio.nombre,
--        beneficiaria.id,
--        ADDDATE(fecha_entrega, 14) AS fecha_inicio, 
--        210_pagos.asistencia_codigo, 
--        ROUND((parametro.fecha - fecha_inicio + 1) / 7) + 1 AS duracion_semanas
-- FROM 
--      parametro, 
--      barrio 
--      INNER JOIN beneficiaria ON barrio.id = beneficiaria.barrio_id
--      INNER JOIN credito ON beneficiaria.id = credito.beneficiaria_id
--      INNER JOIN	210_pagos ON credito.id = 210_pagos.credito_id AND credito.beneficiaria_id = 210_pagos.beneficiaria_id
--      INNER JOIN fecha ON fecha.fecha = 210_pagos.fecha
-- WHERE 
--       fecha.fecha <= parametro.fecha
--       AND ADDDATE(fecha_entrega, 14) <= fecha.fecha
--       AND credito.fecha_finalizacion IS NULL;

-- -- qCreditosActivosPorBeneficiariaActiva
-- SELECT 
--        beneficiaria.id AS id_beneficiaria, 
--        credito.id AS id_credito, 
--        tActividades.id_amortizacion
-- FROM tSistAmortizacion 
--      INNER JOIN tActividades ON tSistAmortizacion.id = tActividades.id_amortizacion
-- 	 INNER JOIN tRubros 
--      INNER JOIN beneficiaria 
--      INNER JOIN credito ON beneficiaria.id = credito.id_beneficiaria) 
--      ON tRubros.id = credito.id_rubro) ON tActividades.id = tRubros.id_actividad
-- WHERE (((beneficiaria.activa)=True) AND ((credito.fecha_finalizacion) Is Null));

-- --qContratoMutuo
-- SELECT 
--        [credito].[id], 
--        [tbeneficiarias].[nombre] & " " & [tbeneficiarias].[apellido] AS beneficiaria, 
--        [beneficiaria].[dni], 
--        [beneficiaria].[fecha_nac],
--        [beneficiaria].[estado_civil],
--        [beneficiaria].[domicilio], 
-- 	   [barrio].[ciudad] AS localidad,
--        [barrio].[provincia],
--        [tActividades].[nombre] AS emprendimiento, 
-- 	   [credito].[cuotas], 
--        num2Text([cuotas]) AS cuotas_en_letras,
--        [credito].[monto_cheque], 
-- 	   num2Text(Fix([credito.monto_cheque])) & " " & cents2Text([monto_cheque]) AS monto_cheque_en_letras, 
--        [monto_cheque]*(1+[tasa_interes])/[cuotas] AS monto_cuota, 
-- 	   num2Text(Fix([monto_cheque]*(1+[tasa_interes])/[cuotas])) & " " & cents2Text(([monto_cheque]*(1+[tasa_interes])/[cuotas])) AS monto_cuota_en_letras,
--        [barrio].[ciudad], 
-- 	   [barrio].[domicilio_pago],
--        Day([credito].[fecha_entrega]+14) AS dia_cuota1, 
-- 	   mes2Text(Month([credito].[fecha_entrega]+14)) AS mes_cuota1,
--        Year([credito].[fecha_entrega]+14) AS anio_cuota1,
--        Day([credito].[fecha_entrega]+([credito].[cuotas]+1)*7) AS dia_venc, 
-- 	   mes2Text(Month([credito].[fecha_entrega]+([credito].[cuotas]+1)*7)) AS mes_venc, 
-- 	   Year([credito].[fecha_entrega]+([credito].[cuotas]+1)*7) AS anio_venc, 
-- 	   Day([credito].[fecha_entrega]) AS dia_entrega,
-- 	   mes2Text(Month([credito].[fecha_entrega])) AS 
-- 	   mes_entrega, Year([credito].[fecha_entrega]) AS anio_entrega
-- FROM 
-- tActividades 
-- INNER JOIN (tRubros 
-- INNER JOIN ((barrio 
-- INNER JOIN beneficiaria ON 
-- 	[barrio].[id]=[beneficiaria].[id_barrio]) 
-- INNER JOIN credito ON 
-- 	[beneficiaria].[id]=[credito].[id_beneficiaria]) ON [tRubros].[id]=[credito].[id_rubro]) ON 
-- 	[tActividades].[id]=[tRubros].[id_actividad];
