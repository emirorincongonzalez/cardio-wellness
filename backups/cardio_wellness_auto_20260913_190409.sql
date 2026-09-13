--
-- Backup de Cardio-Wellness
-- Fecha: 2026-09-13 19:04:09
-- Base de datos: cardio_wellness
--


--
-- Datos de la tabla usuarios
--

INSERT INTO usuarios (id_usuario, nombre, apellido, correo_electronico, contraseña_hash, edad, tipo_usuario, fecha_registro) VALUES (447, 'jose', 'cordero', 'jose123@gmail.com', '$2b$12$wlYh0W6yZjIgavrQzGZDC.Ucmr518ZsRgoVOw9Yr9ula82/Dan98e', 12, 'cliente', 2026-09-13);
INSERT INTO usuarios (id_usuario, nombre, apellido, correo_electronico, contraseña_hash, edad, tipo_usuario, fecha_registro) VALUES (448, 'Admin', 'Sistema', 'admin@cardio.com', '$2b$12$HP62H/Pf0zmN2JVSW/lXou0q0E0spu01iAZYAZMqMqsJINQbjqqrO', 30, 'cliente', 2026-09-13);

--
-- Datos de la tabla clientes
--

INSERT INTO clientes (id_usuario, peso, altura, objetivo, fecha_ingreso) VALUES (447, 32.00, 123.00, 'bajar de peso', 2026-09-13);

--
-- Datos de la tabla rutinas
--

INSERT INTO rutinas (id_rutina, nombre, descripcion, objetivo, nivel, duracion_semanas, creado_por, fecha_creacion) VALUES (42, 'Cardio Básico', 'Rutina de cardio para principiantes', 'Perder peso', 'BASICO', 4, 448, 2026-09-13);
INSERT INTO rutinas (id_rutina, nombre, descripcion, objetivo, nivel, duracion_semanas, creado_por, fecha_creacion) VALUES (43, 'Fuerza Intermedio', 'Rutina de fuerza para nivel intermedio', 'Ganar masa muscular', 'INTERMEDIO', 6, 448, 2026-09-13);

--
-- Datos de la tabla ejercicios
--

INSERT INTO ejercicios (id_ejercicio, nombre, descripcion, tipo, duracion_minutos, intensidad, calorias_estimadas, creado_por) VALUES (21, 'Cinta caminando', 'Caminata moderada', 'Cardio', 10, 'BAJA', 50.00, NULL);
INSERT INTO ejercicios (id_ejercicio, nombre, descripcion, tipo, duracion_minutos, intensidad, calorias_estimadas, creado_por) VALUES (22, 'Press de banca', 'Press de banca con barra', 'Fuerza', 15, 'MEDIA', 80.00, NULL);
INSERT INTO ejercicios (id_ejercicio, nombre, descripcion, tipo, duracion_minutos, intensidad, calorias_estimadas, creado_por) VALUES (23, 'Cinta caminando', 'Caminata moderada', 'Cardio', 10, 'BAJA', 50.00, NULL);
INSERT INTO ejercicios (id_ejercicio, nombre, descripcion, tipo, duracion_minutos, intensidad, calorias_estimadas, creado_por) VALUES (24, 'Press de banca', 'Press de banca con barra', 'Fuerza', 15, 'MEDIA', 80.00, NULL);
INSERT INTO ejercicios (id_ejercicio, nombre, descripcion, tipo, duracion_minutos, intensidad, calorias_estimadas, creado_por) VALUES (25, 'Cinta caminando', 'Caminata moderada', 'Cardio', 10, 'BAJA', 50.00, 448);
INSERT INTO ejercicios (id_ejercicio, nombre, descripcion, tipo, duracion_minutos, intensidad, calorias_estimadas, creado_por) VALUES (26, 'Elíptica', 'Ejercicio de baja impacto', 'Cardio', 10, 'BAJA', 60.00, 448);
INSERT INTO ejercicios (id_ejercicio, nombre, descripcion, tipo, duracion_minutos, intensidad, calorias_estimadas, creado_por) VALUES (27, 'Sentadillas', 'Sentadillas sin peso', 'Fuerza', 10, 'BAJA', 40.00, 448);
INSERT INTO ejercicios (id_ejercicio, nombre, descripcion, tipo, duracion_minutos, intensidad, calorias_estimadas, creado_por) VALUES (28, 'Press de banca', 'Press de banca con barra', 'Fuerza', 15, 'MEDIA', 80.00, 448);
INSERT INTO ejercicios (id_ejercicio, nombre, descripcion, tipo, duracion_minutos, intensidad, calorias_estimadas, creado_por) VALUES (29, 'Peso muerto', 'Peso muerto rumano', 'Fuerza', 15, 'MEDIA', 90.00, 448);
INSERT INTO ejercicios (id_ejercicio, nombre, descripcion, tipo, duracion_minutos, intensidad, calorias_estimadas, creado_por) VALUES (30, 'Dominadas', 'Dominadas asistidas', 'Fuerza', 15, 'MEDIA', 70.00, 448);
-- Tabla rutinas_ejercicios no existe, saltando...


--
-- Datos de la tabla asignaciones_rutina
--


--
-- Datos de la tabla sesiones_entrenamiento
--


--
-- Datos de la tabla progreso_mensual
--

