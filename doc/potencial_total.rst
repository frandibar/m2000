.. _potencial_total:

Reporte de Recaudación Potencial Total
======================================

Es un listado con el total potencial de pagos agrupados por semana, efectuados en un intervalo de tiempo especificado: *fecha desde* y *fecha hasta*.

Devuelve las siguientes columnas:

+----------------------+--------------------------------------------------------+
|Columna               |Fórmula                                                 |
+======================+========================================================+
|semana                |'AAAA.SS' siendo AAAA el año y SS la semana             |
+----------------------+--------------------------------------------------------+
|recaudación           |suma de pagos                                           |
+----------------------+--------------------------------------------------------+
|recaudación potencial |suma de (deuda total / cuotas)                          |
+----------------------+--------------------------------------------------------+
|porcentaje            |recaudación / recaudación potencial                     |
+----------------------+--------------------------------------------------------+

Las filas reúnen las siguientes condiciones:
 * fecha de pago comprendida entre *fecha desde* y *fecha hasta*
 * credito activo para la semana en cuestión. 
   Esto implica que:

   * semana en cuestion >= fecha de entrega + 2 semanas
   * semana de fecha de finalización >= semana en cuestion ó fecha de finalización en blanco.
