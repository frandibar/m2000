USE m2000;

DELIMITER $$
DROP FUNCTION IF EXISTS `m2000`.`cuotas_teorico`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `cuotas_teorico`(fecha DATE, fecha_entrega DATE, cuotas INTEGER) RETURNS float
BEGIN
    SET @fecha_inicio = ADDDATE(fecha_entrega, 14);
    SET @res = DATEDIFF(fecha, @fecha_inicio) / 7;
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
    AND (v100.fecha_finalizacion > parametro.fecha OR v100.fecha_finalizacion IS NULL)
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
    credito.deuda_total - TP.total_pagos AS saldo,
	TP.total_pagos AS monto_pagado
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
    cuotas_teorico / cuotas AS cuotas_teorico_porcent,
    cuotas_teorico - cuotas_pagadas AS diferencia_cuotas,
    saldo,
	monto_pagado,
	deuda_total * cuotas_teorico / cuotas AS monto_teorico,
    deuda_total * cuotas_teorico / cuotas - monto_pagado AS diferencia_monto,
    estado_credito.descripcion AS estado
FROM
    101_indicadores 
    JOIN estado_credito 
    ON cuotas_teorico - cuotas_pagadas > estado_credito.cuotas_adeudadas_min 
    AND cuotas_teorico - cuotas_pagadas <= estado_credito.cuotas_adeudadas_max;

