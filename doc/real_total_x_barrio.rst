.. _real_total_x_barrio:

Reporte de Recaudación Real Total por Barrio
============================================

Es un listado con el total de pagos agrupados por semana y barrio, efectuados en un intervalo de tiempo especificado: *fecha desde* y *fecha hasta*.

Devuelve las siguientes columnas:

+----------------------+--------------------------------------------------------+
|Columna               |Fórmula                                                 |
+======================+========================================================+
|semana                |'AAAA.SS' siendo AAAA el año y SS la semana             |
+----------------------+--------------------------------------------------------+
|barrio                |                                                        |
+----------------------+--------------------------------------------------------+
|recaudación           |suma de pagos                                           |
+----------------------+--------------------------------------------------------+

Las filas reúnen las siguientes condiciones:
 * fecha de pago comprendida entre *fecha desde* y *fecha hasta*
