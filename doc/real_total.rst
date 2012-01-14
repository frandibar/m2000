.. _real_total:

Reporte de Recaudación Real Total
=================================

Es un listado con el total de pagos agrupados por semana, cartera y tasa de interés, efectuados en un intervalo de tiempo especificado: *fecha desde* y *fecha hasta*.

Devuelve las siguientes columnas:

+----------------------+--------------------------------------------------------+
|Columna               |Fórmula                                                 |
+======================+========================================================+
|semana                |'AAAA.SS' siendo AAAA el año y SS la semana             |
+----------------------+--------------------------------------------------------+
|cartera               |                                                        |
+----------------------+--------------------------------------------------------+
|tasa de interés       |                                                        |
+----------------------+--------------------------------------------------------+
|recaudación           |suma de pagos                                           |
+----------------------+--------------------------------------------------------+

Las filas reúnen las siguientes condiciones:
 * fecha de pago comprendida entre *fecha desde* y *fecha hasta*
