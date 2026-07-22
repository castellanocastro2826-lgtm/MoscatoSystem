-- =========================
-- TABLA CATEGORIAS (NUEVA)
-- =========================
-- Almacena las clasificaciones del menú de forma dinámica
CREATE TABLE IF NOT EXISTS categorias (
    id_categoria INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT NULL,
    activo TINYINT(1) DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================
-- TABLA EMPLEADOS (NUEVA)
-- =========================
-- Almacena los datos físicos y de contacto del personal
CREATE TABLE IF NOT EXISTS empleados (
    id_empleado INT PRIMARY KEY AUTO_INCREMENT,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    documento_identidad VARCHAR(20) UNIQUE NOT NULL,
    telefono VARCHAR(20) NULL,
    cargo VARCHAR(50) NOT NULL,
    activo TINYINT(1) DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================
-- TABLA USUARIOS (MODIFICADA)
-- =========================
-- Se eliminó "nombre" y se agregó "id_empleado" para normalizar
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    id_empleado INT NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol ENUM('Administrador', 'Caja', 'Mesonero', 'Cocinero') NOT NULL,
    activo TINYINT(1) DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
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
-- TABLA PRODUCTOS (MODIFICADA)
-- =========================
-- Se cambió el ENUM 'categoria' por la llave foránea 'id_categoria'
CREATE TABLE IF NOT EXISTS productos (
    id_producto INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    id_categoria INT NOT NULL,
    disponible TINYINT(1) DEFAULT 1,
    activo TINYINT(1) DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
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