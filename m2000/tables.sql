DROP DATABASE IF EXISTS m2000;
CREATE DATABASE m2000;

CREATE TABLE  `m2000`.`amortizacion` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(25) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE  `m2000`.`actividad` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  `amortizacion_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`),
  KEY `ix_actividad_amortizacion_id` (`amortizacion_id`),
  CONSTRAINT `actividad_amortizacion_id_fk` FOREIGN KEY (`amortizacion_id`) REFERENCES `amortizacion` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE  `m2000`.`asistencia` (
  `codigo` varchar(5) NOT NULL,
  `descripcion` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE  `m2000`.`provincia` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE  `m2000`.`ciudad` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  `provincia_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_ciudad_provincia_id` (`provincia_id`),
  CONSTRAINT `ciudad_provincia_id_fk` FOREIGN KEY (`provincia_id`) REFERENCES `provincia` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE  `m2000`.`domicilio_pago` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  `ciudad_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_domicilio_pago_ciudad_id` (`ciudad_id`),
  CONSTRAINT `domicilio_pago_ciudad_id_fk` FOREIGN KEY (`ciudad_id`) REFERENCES `ciudad` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE  `m2000`.`barrio` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  `domicilio_pago_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`),
  KEY `ix_barrio_domicilio_pago_id` (`domicilio_pago_id`),
  CONSTRAINT `barrio_domicilio_pago_id_fk` FOREIGN KEY (`domicilio_pago_id`) REFERENCES `domicilio_pago` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE  `m2000`.`beneficiaria` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `barrio_id` int(11) NOT NULL,
  `nombre` varchar(200) NOT NULL,
  `apellido` varchar(200) NOT NULL,
  `grupo` varchar(200) NOT NULL,
  `fecha_alta` date DEFAULT NULL,
  `activa` tinyint(1) DEFAULT 1,
  `fecha_baja` date DEFAULT NULL,
  `comentarios` varchar(1000) DEFAULT NULL,
  `dni` varchar(10) DEFAULT NULL,
  `fecha_nac` date DEFAULT NULL,
  `domicilio` varchar(50) DEFAULT NULL,
  `estado_civil` int(11) DEFAULT NULL,
  `telefono` varchar(50) DEFAULT NULL,
  `email` varchar(256) DEFAULT NULL,
  `foto` varchar(100) DEFAULT 'sin-foto.jpg',
  PRIMARY KEY (`id`),
  KEY `ix_beneficiaria_barrio_id` (`barrio_id`),
  CONSTRAINT `beneficiaria_barrio_id_fk` FOREIGN KEY (`barrio_id`) REFERENCES `barrio` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE  `m2000`.`cartera` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  `tasa_interes_anual` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE  `m2000`.`estado_credito` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(200) NOT NULL,
  `cuotas_adeudadas_min` int(11) NOT NULL,
  `cuotas_adeudadas_max` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `descripcion` (`descripcion`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE  `m2000`.`fecha` (
  `fecha` date NOT NULL,
  PRIMARY KEY (`fecha`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE  `m2000`.`parametro` (
  `fecha` date NOT NULL,
  PRIMARY KEY (`fecha`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE  `m2000`.`rubro` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  `actividad_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_rubro_actividad_id` (`actividad_id`),
  CONSTRAINT `rubro_actividad_id_fk` FOREIGN KEY (`actividad_id`) REFERENCES `actividad` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE  `m2000`.`credito` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `beneficiaria_id` int(11) NOT NULL,
  `rubro_id` int(11) NOT NULL,
  `fecha_entrega` date NOT NULL,
  `fecha_cobro` date NOT NULL,
  `prestamo` float DEFAULT NULL,
  `saldo_anterior` float DEFAULT NULL,
  `monto_cheque` float DEFAULT NULL,
  `tasa_interes` float DEFAULT NULL,
  `deuda_total` float DEFAULT NULL,
  `cartera_id` int(11) NOT NULL,
  `cuotas` int(11) NOT NULL,
  `nro_credito` int(11) NOT NULL,
  `fecha_finalizacion` date DEFAULT NULL,
  `comentarios` varchar(1000) DEFAULT NULL,
  `gastos_arq` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_credito_beneficiaria_id` (`beneficiaria_id`),
  KEY `ix_credito_cartera_id` (`cartera_id`),
  KEY `ix_credito_rubro_id` (`rubro_id`),
  CONSTRAINT `credito_beneficiaria_id_fk` FOREIGN KEY (`beneficiaria_id`) REFERENCES `beneficiaria` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `credito_cartera_id_fk` FOREIGN KEY (`cartera_id`) REFERENCES `cartera` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `credito_rubro_id_fk` FOREIGN KEY (`rubro_id`) REFERENCES `rubro` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE  `m2000`.`pago` (
  `credito_id` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `monto` float DEFAULT NULL,
  `asistencia_codigo` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`credito_id`,`fecha`),
  KEY `ix_pago_asistencia_codigo` (`asistencia_codigo`),
  KEY `ix_pago_credito_id` (`credito_id`),
  CONSTRAINT `pago_asistencia_codigo_fk` FOREIGN KEY (`asistencia_codigo`) REFERENCES `asistencia` (`codigo`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `pago_credito_id_fk` FOREIGN KEY (`credito_id`) REFERENCES `credito` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
