INSERT INTO categorias (nombre, descripcion) VALUES
('Moscato Chino - Compartir', 'Combos y para compartir de comida china'),
('Moscato Chino - Personal', 'Platos individuales de comida china y acompañantes'),
('Moscato Broaster', 'Combos de pollo a la broaster tradicional'),
('Promociones', 'Ofertas especiales y combos mixtos');
INSERT INTO productos (nombre, descripcion, precio, id_categoria) VALUES
-- ==========================================
-- Categoría 1: Moscato Chino - Compartir 
-- ==========================================
('Combo 1', 'Arroz 500 g, 3 piezas de pollo broaster y 3 lumpias', 36000.00, 1),
('Combo 2', 'Arroz 1 kg y 4 lumpias', 39000.00, 1),
('Combo 3', '8 piezas de pollo broaster, arroz 1 kg y 4 lumpias', 70000.00, 1),
('Combo 4', 'Pollo agridulce, chop suey, arroz 1 kg y 4 lumpias', 60000.00, 1),
('Combo 5', 'Arroz 1.5 kg, 8 piezas de pollo, chop suey, 5 lumpias y refresco', 130000.00, 1),

-- ==========================================
-- Categoría 2: Moscato Chino - Personal
-- ==========================================
('Promo Personal', 'Arroz 150 g y 1 lumpia', 8000.00, 2),
('Chop Suey Personal', 'Chop suey, arroz 250 g, 1 lumpia y papas fritas', 15000.00, 2),
('Pollo Agridulce', 'Pollo agridulce, arroz 250 g, 1 lumpia y papas', 20000.00, 2),
('Pollo Broaster Personal', '2 piezas de pollo broaster, arroz 250 g, 1 lumpia y papas', 20000.00, 2),
('Cerdo Agridulce', 'Cerdo agridulce, arroz 250 g, 1 lumpia y papas', 26000.00, 2),
('Lomito en Salsa de Ostras', 'Lomito en salsa de ostras, arroz 250 g, 1 lumpia y papas', 26000.00, 2),

-- ==========================================
-- Categoría 3: Moscato Broaster
-- ==========================================
('Combo Soltero', '1 pieza de pollo crocante y arepitas', 10000.00, 3),
('Combo Dúo', '2 piezas de pollo crocante y arepitas', 14000.00, 3),
('Combo Mediano', '4 piezas de pollo crocante y arepitas', 28000.00, 3),
('Combo Broaster', '8 piezas de pollo, arepitas y papas', 59000.00, 3),

-- ==========================================
-- Categoría 4: Promociones
-- ==========================================
('Combo Especial', '8 piezas de pollo, 10 arepitas, papas, ensalada y refresco de 1 litro', 55000.00, 4),
('Súper Moscato', 'Arroz especial, pollo broaster y lumpias', 70000.00, 4);