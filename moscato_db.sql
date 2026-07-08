-- =========================
-- TABLA USUARIOS
-- =========================

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol ENUM('Administrador', 'Caja', 'Mesonero', 'Cocinero') NOT NULL,
    activo TINYINT(1) DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================
-- TABLA MESAS
-- =========================

CREATE TABLE IF NOT EXISTS mesas (
    id_mesa INT PRIMARY KEY AUTO_INCREMENT,
    numero_mesa INT UNIQUE NOT NULL,
    estado ENUM('Libre', 'Ocupada', 'Inactiva') DEFAULT 'Libre',
    activo TINYINT(1) DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================
-- TABLA PRODUCTOS
-- =========================

CREATE TABLE IF NOT EXISTS productos (
    id_producto INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    categoria ENUM('Comida', 'Bebida', 'Postre') NOT NULL,
    disponible TINYINT(1) DEFAULT 1,
    activo TINYINT(1) DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================
-- TABLA PEDIDOS
-- =========================

CREATE TABLE IF NOT EXISTS pedidos (
    id_pedido INT PRIMARY KEY AUTO_INCREMENT,
    id_mesa INT NULL,
    id_usuario INT NOT NULL,
    tipo_pedido ENUM('Mesa', 'Para llevar') DEFAULT 'Mesa',
    fecha_apertura DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_cierre DATETIME NULL,
    subtotal_consumido DECIMAL(10, 2) DEFAULT 0.00,
    estado_pedido ENUM('Abierto', 'En cocina', 'Listo', 'Servido', 'Cancelado') DEFAULT 'Abierto',

    FOREIGN KEY (id_mesa) REFERENCES mesas(id_mesa),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- =========================
-- TABLA DETALLE_PEDIDO
-- =========================

CREATE TABLE IF NOT EXISTS detalle_pedido (
    id_detalle INT PRIMARY KEY AUTO_INCREMENT,
    id_pedido INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    descripcion_preparacion TEXT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    fecha_envio_cocina DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado_item ENUM('Pendiente', 'En cocina', 'En preparación', 'Listo', 'Servido', 'Cancelado') DEFAULT 'Pendiente',

    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);