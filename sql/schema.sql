-- ============================================================
-- SCRIPT DDL DEFINITIVO: Cardio Wellness Manager (PostgreSQL)
-- BASADO EN: DCD
-- PROPIEDADES: Normalizado (3FN), ACID, buenas prácticas
-- ============================================================

-- ============================================================
-- CREACIÓN DE TIPOS ENUM
-- ============================================================
CREATE TYPE tipo_usuario AS ENUM ('cliente', 'administrador');

CREATE TYPE nivel_rutina AS ENUM ('BASICO', 'INTERMEDIO', 'AVANZADO');

CREATE TYPE intensidad AS ENUM ('BAJA', 'MEDIA', 'ALTA');

CREATE TYPE estado_asignacion AS ENUM ('ACTIVA', 'FINALIZADA', 'CANCELADA');

-- ============================================================
-- TABLA: usuarios (Clase abstracta Usuario)
-- ============================================================
CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    correo_electronico VARCHAR(150) UNIQUE NOT NULL,
    contrasenia_hash VARCHAR(255) NOT NULL,  -- bcrypt
    edad INTEGER NOT NULL CHECK (edad > 0),
    tipo_usuario tipo_usuario NOT NULL DEFAULT 'cliente',
    fecha_registro DATE NOT NULL DEFAULT CURRENT_DATE
)

COMMENT ON TABLE usuarios IS 'Base de la herencia: Usuario (abstracta en Python)';
COMMENT ON COLUMN usuarios.contrasenia_hash IS 'Almacena el hash de la contraseña';

-- Indices criticos
CREATE INDEX idx_usuarios_correo ON usuarios(correo_electronico);
CREATE INDEX idx_usuarios_tipo ON usuarios(tipo_usuario);
CREATE INDEX idx_usuarios_nombre ON usuarios(nombre, apellido);

-- ============================================================
-- TABLA: clientes (Especializacion de Usuario - Herencia 1:1)
-- Representa la clase Cliente del DCD
-- ============================================================
CREATE TABLE clientes (
    id_usuario INTEGER PRIMARY KEY REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    peso DECIMAL(5,2) NOT NULL CHECK (peso > 0),
    altura DECIMAL(5,2) NOT NULL CHECK (altura > 0),
    objetivo VARCHAR(255) NOT NULL,
    fecha_ingreso DATE NOT NULL DEFAULT CURRENT_DATE
);

COMMENT ON TABLE clientes IS 'Especializacion de Usuario: Cliente (hereda de Usuario)';
COMMENT ON COLUMN clientes.objetivo IS 'Ej: Bajar de peso, Mejorar resistencia, Mantener condicion';

-- Indice para consultas de progreso por fecha de ingreso
CREATE INDEX idx_clientes_ingreso ON clientes(fecha_ingreso);

-- ============================================================
-- TABLA: administradores (Especializacion de Usuario)
-- Representa la clase Administrador del DCD
-- ============================================================
CREATE TABLE administradores (
    id_usuario INTEGER PRIMARY KEY REFERENCES usuarios(id_usuario) ON DELETE CASCADE
    -- Sin atributos adicionales (igual que en el DCD)
);

COMMENT ON TABLE administradores IS 'Especializacion de Usuario: Administrador (sin atributos propios)';

-- ============================================================
-- TABLA: ejercicios (Catalogo de ejercicios - Entidad fuerte)
-- Representa la clase EjercicioCardio del DCD
-- ============================================================
CREATE TABLE ejercicios (
    id_ejercicio SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(50) NOT NULL,  -- Ej. "Aeróbico", "HIIT", "Cardio funcional"
    duracion_minutos INTEGER NOT NULL CHECK (duracion_minutos > 0),
    intensidad intensidad NOT NULL,
    calorias_estimadas DECIMAL(6,2) NOT NULL CHECK (calorias_estimadas >= 0),
    creado_por INTEGER NULL REFERENCES usuarios(id_usuario) ON DELETE SET NULL  -- Asociacion con Administrador
);

COMMENT ON TABLE ejercicios IS 'Catalogo de ejercicios (Clase EjercicioCardio)';
COMMENT ON COLUMN ejercicios.creado_por IS 'Administrador que creo el ejercicio (asociacion)';

-- Indices para búsquedas rápidas
CREATE INDEX idx_ejercicios_nombre ON ejercicios(nombre);
CREATE INDEX idx_ejercicios_tipo ON ejercicios(tipo);
CREATE INDEX idx_ejercicios_intensidad ON ejercicios(intensidad);

-- ============================================================
-- TABLA: rutinas (Planes de entrenamiento - Entidad fuerte)
-- Representa la clase Rutina del DCD
-- ============================================================
CREATE TABLE rutinas (
    id_rutina SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    objetivo VARCHAR(255) NOT NULL,
    nivel nivel_rutina NOT NULL,
    duracion_semanas INTEGER NOT NULL CHECK (duracion_semanas > 0),
    creado_por INTEGER NULL REFERENCES usuarios(id_usuario) ON DELETE SET NULL,  -- Asociacion con Administrador
    fecha_creacion DATE NOT NULL DEFAULT CURRENT_DATE
);

COMMENT ON TABLE rutinas IS 'Planes de entrenamiento (Clase Rutina)';
COMMENT ON COLUMN rutinas.creado_por IS 'Administrador que gestiona/crea la rutina (asociacion)';

-- Indices para filtrar rutinas
CREATE INDEX idx_rutinas_objetivo ON rutinas(objetivo);
CREATE INDEX idx_rutinas_nivel ON rutinas(nivel);

-- ============================================================
-- TABLA PUENTE: rutina_ejercicios (Agregación N:M)
-- Representa: Rutina "1" o-- "1..*" EjercicioCardio
-- ============================================================
CREATE TABLE rutina_ejercicios (
    id_rutina INTEGER NOT NULL REFERENCES rutinas(id_rutina) ON DELETE CASCADE,
    id_ejercicio INTEGER NOT NULL REFERENCES ejercicios(id_ejercicio) ON DELETE CASCADE,
    orden_ejercicio INTEGER NOT NULL CHECK (orden_ejercicio > 0),  -- Para mantener el orden en la rutina
    PRIMARY KEY (id_rutina, id_ejercicio)
);

COMMENT ON TABLE rutina_ejercicios IS 'Relacion N:M: una rutina contiene varios ejercicios (agregacion)';

-- Indices para consultas eficientes
CREATE INDEX idx_rutina_ejercicios_rutina ON rutina_ejercicios(id_rutina);
CREATE INDEX idx_rutina_ejercicios_ejercicio ON rutina_ejercicios(id_ejercicio);

-- ============================================================
-- TABLA: asignaciones_rutina (Composicion con Cliente)
-- Representa: Cliente "1" *-- "0..*" AsignacionRutina
-- ============================================================
CREATE TABLE asignaciones_rutina (
    id_asignacion SERIAL PRIMARY KEY,
    id_cliente INTEGER NOT NULL REFERENCES clientes(id_usuario) ON DELETE CASCADE,
    id_rutina INTEGER NOT NULL REFERENCES rutinas(id_rutina) ON DELETE RESTRICT,  -- No borrar rutina si está asignada
    fecha_asignacion DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_finalizacion DATE,
    estado estado_asignacion NOT NULL DEFAULT 'ACTIVA',
    observaciones TEXT,
    CONSTRAINT chk_fechas CHECK (fecha_finalizacion IS NULL OR fecha_finalizacion >= fecha_asignacion)
);

COMMENT ON TABLE asignaciones_rutina IS 'Historial de asignaciones (Clase AsignacionRutina)';
COMMENT ON CONSTRAINT chk_fechas ON asignaciones_rutina IS 'La fecha de finalizacion debe ser posterior a la asignacion';

-- Indices criticos para consultas frecuentes
CREATE INDEX idx_asignaciones_cliente ON asignaciones_rutina(id_cliente);
CREATE INDEX idx_asignaciones_estado ON asignaciones_rutina(estado);
CREATE INDEX idx_asignaciones_fechas ON asignaciones_rutina(fecha_asignacion, fecha_finalizacion);

-- Indice parcial para búsquedas de rutina activa (muy rapido)
CREATE INDEX idx_asignaciones_activa ON asignaciones_rutina(id_cliente) WHERE estado = 'ACTIVA';

-- ============================================================
-- TABLA: sesiones_entrenamiento (Composicion con Cliente)
-- Representa: Cliente "1" *-- "0..*" SesionEntrenamiento
-- ============================================================
CREATE TABLE sesiones_entrenamiento (
    id_sesion SERIAL PRIMARY KEY,
    id_cliente INTEGER NOT NULL REFERENCES clientes(id_usuario) ON DELETE CASCADE,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    duracion_real INTEGER NOT NULL CHECK (duracion_real > 0),
    intensidad_real intensidad NOT NULL,
    calorias_quemadas DECIMAL(6,2) NOT NULL CHECK (calorias_quemadas >= 0),
    observaciones TEXT,
    completada BOOLEAN NOT NULL DEFAULT FALSE
);

COMMENT ON TABLE sesiones_entrenamiento IS 'Registro de entrenamientos (Clase SesionEntrenamiento)';

-- Indices para consultar sesiones por cliente y fechas
CREATE INDEX idx_sesiones_cliente ON sesiones_entrenamiento(id_cliente);
CREATE INDEX idx_sesiones_fecha ON sesiones_entrenamiento(fecha);
CREATE INDEX idx_sesiones_completada ON sesiones_entrenamiento(completada);

-- ============================================================
-- TABLA: progreso_mensual (Composicion con Cliente)
-- Representa: Cliente "1" *-- "0..*" ProgresoMensual
-- ============================================================
CREATE TABLE progreso_mensual (
    id_progreso SERIAL PRIMARY KEY,
    id_cliente INTEGER NOT NULL REFERENCES clientes(id_usuario) ON DELETE CASCADE,
    mes DATE NOT NULL,  -- Se recomienda guardar el primer día del mes (ej. 2026-08-01)
    peso DECIMAL(5,2) NOT NULL CHECK (peso > 0),
    sesiones_completadas INTEGER NOT NULL DEFAULT 0 CHECK (sesiones_completadas >= 0),
    sesiones_planificadas INTEGER NOT NULL DEFAULT 0 CHECK (sesiones_planificadas >= 0),
    porcentaje_cumplimiento DECIMAL(5,2) NOT NULL DEFAULT 0.0 CHECK (porcentaje_cumplimiento BETWEEN 0 AND 100),
    CONSTRAINT unq_cliente_mes UNIQUE (id_cliente, mes)  -- Solo un registro por cliente y mes
);

COMMENT ON TABLE progreso_mensual IS 'Resumen mensual de progreso (Clase ProgresoMensual)';
COMMENT ON COLUMN progreso_mensual.mes IS 'Primer día del mes (ej. 2026-08-01)';

-- Indices para consultar progreso
CREATE INDEX idx_progreso_cliente ON progreso_mensual(id_cliente);
CREATE INDEX idx_progreso_mes ON progreso_mensual(mes);

-- ============================================================
-- 12. VISTAS UTILES (para simplificar las consultas en Python)
-- ============================================================
-- Vista: Datos completos del cliente (union de usuario + cliente)
CREATE VIEW vw_clientes_completo AS
SELECT 
    u.id_usuario,
    u.nombre,
    u.apellido,
    u.correo_electronico,
    u.contrasenia_hash,
    u.edad,
    u.fecha_registro,
    c.peso,
    c.altura,
    c.objetivo,
    c.fecha_ingreso
FROM usuarios u
JOIN clientes c ON u.id_usuario = c.id_usuario
WHERE u.tipo_usuario = 'cliente';

COMMENT ON VIEW vw_clientes_completo IS 'Vista para obtener todos los datos de un cliente en una sola consulta (incluye hash)';

-- Vista: Rutina activa por cliente (para el panel del cliente)
CREATE VIEW vw_rutina_activa_cliente AS
SELECT 
    a.id_cliente,
    a.id_asignacion,
    r.id_rutina,
    r.nombre AS nombre_rutina,
    r.objetivo,
    r.nivel,
    r.duracion_semanas,
    a.fecha_asignacion,
    a.fecha_finalizacion,
    a.observaciones
FROM asignaciones_rutina a
JOIN rutinas r ON a.id_rutina = r.id_rutina
WHERE a.estado = 'ACTIVA';

COMMENT ON VIEW vw_rutina_activa_cliente IS 'Vista para obtener la rutina activa de un cliente (filtro por id_cliente)';

-- Vista: Resumen de progreso con cumplimiento
CREATE VIEW vw_progreso_cliente AS
SELECT 
    p.id_cliente,
    u.nombre,
    u.apellido,
    p.mes,
    p.peso,
    p.sesiones_completadas,
    p.sesiones_planificadas,
    p.porcentaje_cumplimiento,
    CASE 
        WHEN p.porcentaje_cumplimiento >= 80 THEN 'ALTO'
        WHEN p.porcentaje_cumplimiento >= 50 THEN 'MEDIO'
        ELSE 'BAJO'
    END AS nivel_cumplimiento
FROM progreso_mensual p
JOIN clientes c ON p.id_cliente = c.id_usuario
JOIN usuarios u ON c.id_usuario = u.id_usuario
ORDER BY p.mes DESC;

COMMENT ON VIEW vw_progreso_cliente IS 'Vista para mostrar el progreso con niveles de cumplimiento';

-- ============================================================
-- DATOS DE PRUEBA MÍNIMOS
-- Descomentar para insertar datos de ejemplo
-- ============================================================

-- Insertar un administrador (id_usuario = 1)
INSERT INTO usuarios (nombre, apellido, correo_electronico, contrasenia_hash, edad, tipo_usuario)
VALUES ('Laura', 'Gomez', 'admin@cardiowellness.com', 'hash_dummy_123', 30, 'administrador');

-- Insertar un administrador en la tabla específica
INSERT INTO administradores (id_usuario) VALUES (1);

-- Insertar clientes
INSERT INTO usuarios (nombre, apellido, correo_electronico, contrasenia_hash, edad, tipo_usuario)
VALUES 
    ('Carlos', 'Perez', 'carlos@gmail.com', 'hash_dummy_456', 28, 'cliente'),
    ('Ana', 'Gomez', 'ana@gmail.com', 'hash_dummy_789', 25, 'cliente'),
    ('Galia', 'Gonzalez', 'galia@gmail.com', 'hash_dummy_1234', 22, 'cliente'),
    ('Hector', 'Horcadela', 'hector@gmail.com', 'hash_dummy_1245', 21, 'cliente');

INSERT INTO clientes (id_usuario, peso, altura, objetivo, fecha_ingreso)
VALUES 
    (2, 82.5, 1.75, 'Bajar de peso', '2026-01-15'),
    (3, 65.0, 1.65, 'Mejorar resistencia', '2026-02-01'),
    (4, 63.0, 1.70, 'Mejorar resistencia', '2026-03-15'),
    (5, 60.0, 1.72, 'Mantener condicion', '2026-08-15');

-- ============================================================
-- Datos de Prueba: Insertar ejercicios (Calorias sin verificar, solo ejemplo)
-- ============================================================
INSERT INTO ejercicios (nombre, descripcion, tipo, duracion_minutos, intensidad, calorias_estimadas, creado_por)
VALUES 
    ('Caminata Rapida', 'Marcha rapida al aire libre o caminadora', 'LISS', 30, 'BAJA', 150.0, 1),
    ('Trote Continuo', 'Trote a ritmo constante', 'LISS', 25, 'MEDIA', 250.0, 1),
    ('Bicicleta Estatica', 'Pedaleo en bicicleta estatica', 'LISS', 20, 'MEDIA', 190.0, 1),
    ('Saltar la Cuerda', 'Salto continuo con cuerda', 'HIIT', 15, 'ALTA', 280.0, 1),
    ('Circuito Funcional', 'Circuito de 8 estaciones, 45s por estacion', 'HIIT', 25, 'ALTA', 350.0, 1),
    ('HIIT de Bajo Impacto', 'Version sin saltos de HIIT, ideal para principiantes. Incluye sentadillas sin salto, zancadas, planchas y pasos laterales.', 'HIIT', 20, 'MEDIA', 220.0, 1);

-- ============================================================
-- Datos de Prueba: Insertar rutinas
-- ============================================================
INSERT INTO rutinas (nombre, descripcion, objetivo, nivel, duracion_semanas, creado_por)
VALUES
    ('Quema Grasa Basica', 'Rutina suave para empezar con ejercicios de baja intensidad', 'Bajar de peso', 'BASICO', 4, 1),
    ('Quema Grasa Intensa', 'Rutina enfocada en pérdida de peso con ejercicios HIIT y LISS', 'Bajar de peso', 'INTERMEDIO', 4, 1),
    ('Resistencia Cardio', 'Rutina para mejorar capacidad cardiovascular con ejercicios de media intensidad', 'Mejorar resistencia', 'BASICO', 6, 1),
    ('Resistencia Intermedia', 'Rutina para aumentar capacidad cardiovascular con intensidad media-alta', 'Mejorar resistencia', 'INTERMEDIO', 6, 1),
    ('Mantenimiento Basico', 'Rutina ligera para mantener condición física sin esfuerzo excesivo', 'Mantener condicion', 'BASICO', 8, 1),
    ('Mantenimiento Activo', 'Rutina para mantener condición física con ejercicios variados y de bajo impacto', 'Mantener condicion', 'BASICO', 8, 1);

-- ============================================================
-- Datos de prueba: Asignacion de ejercicios a rutinas (Agregacion)
-- ============================================================

-- Quema Grasa Básica (1)
INSERT INTO rutina_ejercicios (id_rutina, id_ejercicio, orden_ejercicio)
VALUES (1, 1, 1), (1, 6, 2), (1, 3, 3);

-- Quema Grasa Intensa (2)
INSERT INTO rutina_ejercicios (id_rutina, id_ejercicio, orden_ejercicio)
VALUES (2, 1, 1), (2, 2, 2), (2, 4, 3), (2, 5, 4);

-- Resistencia Cardio (3)
INSERT INTO rutina_ejercicios (id_rutina, id_ejercicio, orden_ejercicio)
VALUES (3, 2, 1), (3, 3, 2), (3, 6, 3);

-- Resistencia Intermedia (4)
INSERT INTO rutina_ejercicios (id_rutina, id_ejercicio, orden_ejercicio)
VALUES (4, 2, 1), (4, 5, 2), (4, 4, 3), (4, 1, 4);

-- Mantenimiento Básico (5)
INSERT INTO rutina_ejercicios (id_rutina, id_ejercicio, orden_ejercicio)
VALUES (5, 1, 1), (5, 3, 2), (5, 6, 3);

-- Mantenimiento Activo (6)
INSERT INTO rutina_ejercicios (id_rutina, id_ejercicio, orden_ejercicio)
VALUES (6, 3, 1), (6, 6, 2), (6, 1, 3), (6, 2, 4);

-- Asignar rutinas a clientes (composicion)
INSERT INTO asignaciones_rutina (id_cliente, id_rutina, fecha_asignacion, estado)
VALUES 
    (2, 2, '2026-08-01', 'ACTIVA'),   -- Carlos con Quema Grasa Intensa
    (3, 4, '2026-08-15', 'ACTIVA'),   -- Ana con Resistencia Intermedia
    (4, 3, '2026-08-20', 'ACTIVA'),   -- Galia con Resistencia Cardio
    (5, 6, '2026-09-01', 'ACTIVA');   -- Héctor con Mantenimiento Activo

-- ============================================================
-- Datos de prueba: Insertar sesiones de entrenamiento
-- ============================================================
INSERT INTO sesiones_entrenamiento (id_cliente, fecha, duracion_real, intensidad_real, calorias_quemadas, observaciones, completada)
VALUES 
    -- Carlos (id_cliente = 2) con Quema Grasa Intensa
    (2, '2026-08-03', 45, 'ALTA', 380.0, 'Buena sesión, completó todo el circuito', TRUE),
    (2, '2026-08-10', 40, 'MEDIA', 310.0, 'Regular, se sintió con poca energía', TRUE),
    (2, '2026-08-17', 50, 'ALTA', 420.0, 'Excelente, mejoró tiempos', TRUE),
    (2, '2026-08-24', 35, 'ALTA', 290.0, 'Corta pero intensa', TRUE),

    -- Ana (id_cliente = 3) con Resistencia Intermedia
    (3, '2026-08-18', 45, 'ALTA', 370.0, 'Muy bien, ritmo constante', TRUE),
    (3, '2026-08-25', 40, 'MEDIA', 290.0, 'Bien, sin complicaciones', TRUE),
    (3, '2026-09-01', 50, 'ALTA', 410.0, 'Excelente, mejoró resistencia', TRUE),

    -- Galia (id_cliente = 4) con Resistencia Cardio
    (4, '2026-08-22', 35, 'MEDIA', 250.0, 'Buena sesión, ritmo adecuado', TRUE),
    (4, '2026-08-29', 40, 'MEDIA', 280.0, 'Bien, se sintió con energía', TRUE),
    (4, '2026-09-05', 30, 'BAJA', 190.0, 'Ligera, solo por mantenerse activa', TRUE),

    -- Héctor (id_cliente = 5) con Mantenimiento Activo
    (5, '2026-09-02', 25, 'BAJA', 160.0, 'Primera sesión, bien', TRUE),
    (5, '2026-09-09', 30, 'MEDIA', 220.0, 'Buena, se sintió cómodo', TRUE),
    (5, '2026-09-16', 20, 'BAJA', 140.0, 'Sesión corta, sin problemas', TRUE);

-- ============================================================
-- Datos de Prueba: Insertar progreso mensual
-- ============================================================

INSERT INTO progreso_mensual (id_cliente, mes, peso, sesiones_completadas, sesiones_planificadas, porcentaje_cumplimiento)
VALUES
-- Carlos (id_cliente = 2) → Bajar de peso
(2, '2026-08-01', 82.5, 4, 4, 100.0),   -- Agosto: completó todas las sesiones planificadas
(2, '2026-09-01', 80.0, 0, 4, 0.0),     -- Septiembre: aún no registra sesiones

-- Ana (id_cliente = 3) → Mejorar resistencia
(3, '2026-08-01', 65.0, 2, 4, 50.0),    -- Agosto: 2 de 4 sesiones
(3, '2026-09-01', 64.5, 1, 4, 25.0),    -- Septiembre: 1 de 4 sesiones

-- Galia (id_cliente = 4) → Mejorar resistencia
(4, '2026-08-01', 63.0, 2, 4, 50.0),    -- Agosto: 2 de 4 sesiones
(4, '2026-09-01', 62.0, 1, 4, 25.0),    -- Septiembre: 1 de 4 sesiones

-- Héctor (id_cliente = 5) → Mantener condición
(5, '2026-08-01', 60.0, 0, 0, 0.0),     -- Agosto: recién ingresó, sin sesiones planificadas
(5, '2026-09-01', 60.0, 3, 4, 75.0);    -- Septiembre: 3 de 4 sesiones

-- ============================================================
-- FIN DEL SCRIPT
-- ============================================================
