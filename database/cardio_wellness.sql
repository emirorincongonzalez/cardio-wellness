--
-- PostgreSQL database dump
--

\restrict v1TeYGiRKujHJEuTxHdp0JinjcTrieN1h9N0XOHscO1mTxZyJqaxjYnAW98lja9

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.sesiones_entrenamiento DROP CONSTRAINT IF EXISTS sesiones_entrenamiento_id_cliente_fkey;
ALTER TABLE IF EXISTS ONLY public.rutinas DROP CONSTRAINT IF EXISTS rutinas_creado_por_fkey;
ALTER TABLE IF EXISTS ONLY public.rutina_ejercicios DROP CONSTRAINT IF EXISTS rutina_ejercicios_id_rutina_fkey;
ALTER TABLE IF EXISTS ONLY public.rutina_ejercicios DROP CONSTRAINT IF EXISTS rutina_ejercicios_id_ejercicio_fkey;
ALTER TABLE IF EXISTS ONLY public.progreso_mensual DROP CONSTRAINT IF EXISTS progreso_mensual_id_cliente_fkey;
ALTER TABLE IF EXISTS ONLY public.sesiones_entrenamiento DROP CONSTRAINT IF EXISTS fk_sesion_rutina;
ALTER TABLE IF EXISTS ONLY public.ejercicios DROP CONSTRAINT IF EXISTS ejercicios_creado_por_fkey;
ALTER TABLE IF EXISTS ONLY public.clientes DROP CONSTRAINT IF EXISTS clientes_id_usuario_fkey;
ALTER TABLE IF EXISTS ONLY public.asignaciones_rutina DROP CONSTRAINT IF EXISTS asignaciones_rutina_id_rutina_fkey;
ALTER TABLE IF EXISTS ONLY public.asignaciones_rutina DROP CONSTRAINT IF EXISTS asignaciones_rutina_id_cliente_fkey;
DROP TRIGGER IF EXISTS trigger_sincronizar_hash_contrasena ON public.usuarios;
DROP INDEX IF EXISTS public.idx_usuarios_tipo;
DROP INDEX IF EXISTS public.idx_usuarios_correo;
DROP INDEX IF EXISTS public.idx_sesiones_id_cliente_fecha;
DROP INDEX IF EXISTS public.idx_sesiones_id_cliente_completada;
DROP INDEX IF EXISTS public.idx_sesiones_id_cliente;
DROP INDEX IF EXISTS public.idx_sesiones_fecha;
DROP INDEX IF EXISTS public.idx_sesiones_completada;
DROP INDEX IF EXISTS public.idx_sesiones_cliente;
DROP INDEX IF EXISTS public.idx_rutinas_objetivo;
DROP INDEX IF EXISTS public.idx_rutinas_nombre;
DROP INDEX IF EXISTS public.idx_rutinas_nivel;
DROP INDEX IF EXISTS public.idx_rutinas_creado_por;
DROP INDEX IF EXISTS public.idx_rutina_ejercicios_rutina;
DROP INDEX IF EXISTS public.idx_rutina_ejercicios_orden;
DROP INDEX IF EXISTS public.idx_rutina_ejercicios_ejercicio;
DROP INDEX IF EXISTS public.idx_progreso_mes;
DROP INDEX IF EXISTS public.idx_progreso_id_cliente_mes;
DROP INDEX IF EXISTS public.idx_progreso_id_cliente;
DROP INDEX IF EXISTS public.idx_progreso_cliente;
DROP INDEX IF EXISTS public.idx_ejercicios_tipo;
DROP INDEX IF EXISTS public.idx_ejercicios_nombre;
DROP INDEX IF EXISTS public.idx_ejercicios_intensidad;
DROP INDEX IF EXISTS public.idx_ejercicios_creado_por;
DROP INDEX IF EXISTS public.idx_clientes_ingreso;
DROP INDEX IF EXISTS public.idx_clientes_id_usuario;
DROP INDEX IF EXISTS public.idx_asignaciones_id_cliente;
DROP INDEX IF EXISTS public.idx_asignaciones_fechas;
DROP INDEX IF EXISTS public.idx_asignaciones_estado;
DROP INDEX IF EXISTS public.idx_asignaciones_cliente;
DROP INDEX IF EXISTS public.idx_asignaciones_activa;
ALTER TABLE IF EXISTS ONLY public.usuarios DROP CONSTRAINT IF EXISTS usuarios_pkey;
ALTER TABLE IF EXISTS ONLY public.usuarios DROP CONSTRAINT IF EXISTS usuarios_correo_electronico_key;
ALTER TABLE IF EXISTS ONLY public.progreso_mensual DROP CONSTRAINT IF EXISTS uq_progreso_cliente_mes;
ALTER TABLE IF EXISTS ONLY public.progreso_mensual DROP CONSTRAINT IF EXISTS unq_cliente_mes;
ALTER TABLE IF EXISTS ONLY public.sesiones_entrenamiento DROP CONSTRAINT IF EXISTS sesiones_entrenamiento_pkey;
ALTER TABLE IF EXISTS ONLY public.rutinas DROP CONSTRAINT IF EXISTS rutinas_pkey;
ALTER TABLE IF EXISTS ONLY public.rutina_ejercicios DROP CONSTRAINT IF EXISTS rutina_ejercicios_pkey;
ALTER TABLE IF EXISTS ONLY public.progreso_mensual DROP CONSTRAINT IF EXISTS progreso_mensual_pkey;
ALTER TABLE IF EXISTS ONLY public.ejercicios DROP CONSTRAINT IF EXISTS ejercicios_pkey;
ALTER TABLE IF EXISTS ONLY public.clientes DROP CONSTRAINT IF EXISTS clientes_pkey;
ALTER TABLE IF EXISTS ONLY public.asignaciones_rutina DROP CONSTRAINT IF EXISTS asignaciones_rutina_pkey;
ALTER TABLE IF EXISTS public.usuarios ALTER COLUMN id_usuario DROP DEFAULT;
ALTER TABLE IF EXISTS public.sesiones_entrenamiento ALTER COLUMN id_sesion DROP DEFAULT;
ALTER TABLE IF EXISTS public.rutinas ALTER COLUMN id_rutina DROP DEFAULT;
ALTER TABLE IF EXISTS public.progreso_mensual ALTER COLUMN id_progreso DROP DEFAULT;
ALTER TABLE IF EXISTS public.ejercicios ALTER COLUMN id_ejercicio DROP DEFAULT;
ALTER TABLE IF EXISTS public.asignaciones_rutina ALTER COLUMN id_asignacion DROP DEFAULT;
DROP VIEW IF EXISTS public.vw_rutina_activa_cliente;
DROP VIEW IF EXISTS public.vw_clientes_completo;
DROP SEQUENCE IF EXISTS public.usuarios_id_usuario_seq;
DROP TABLE IF EXISTS public.usuarios;
DROP SEQUENCE IF EXISTS public.sesiones_entrenamiento_id_sesion_seq;
DROP TABLE IF EXISTS public.sesiones_entrenamiento;
DROP SEQUENCE IF EXISTS public.rutinas_id_rutina_seq;
DROP TABLE IF EXISTS public.rutinas;
DROP TABLE IF EXISTS public.rutina_ejercicios;
DROP SEQUENCE IF EXISTS public.progreso_mensual_id_progreso_seq;
DROP TABLE IF EXISTS public.progreso_mensual;
DROP SEQUENCE IF EXISTS public.ejercicios_id_ejercicio_seq;
DROP TABLE IF EXISTS public.ejercicios;
DROP TABLE IF EXISTS public.clientes;
DROP SEQUENCE IF EXISTS public.asignaciones_rutina_id_asignacion_seq;
DROP TABLE IF EXISTS public.asignaciones_rutina;
DROP FUNCTION IF EXISTS public.sincronizar_hash_contrasena();
DROP TYPE IF EXISTS public.tipo_usuario;
DROP TYPE IF EXISTS public.nivel_rutina;
DROP TYPE IF EXISTS public.intensidad;
DROP TYPE IF EXISTS public.estado_asignacion;
--
-- Name: estado_asignacion; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.estado_asignacion AS ENUM (
    'ACTIVA',
    'FINALIZADA',
    'CANCELADA'
);


--
-- Name: intensidad; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.intensidad AS ENUM (
    'BAJA',
    'MEDIA',
    'ALTA'
);


--
-- Name: nivel_rutina; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.nivel_rutina AS ENUM (
    'BASICO',
    'INTERMEDIO',
    'AVANZADO'
);


--
-- Name: tipo_usuario; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.tipo_usuario AS ENUM (
    'cliente',
    'administrador'
);


--
-- Name: sincronizar_hash_contrasena(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.sincronizar_hash_contrasena() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    hash_nuevo TEXT;
BEGIN
    hash_nuevo := to_jsonb(NEW) ->> U&'contrase\00F1a_hash';

    IF hash_nuevo IS NOT NULL THEN
        NEW.contrasenia_hash := hash_nuevo;

    ELSIF NEW.contrasenia_hash IS NOT NULL THEN
        NEW := jsonb_populate_record(
            NEW,
            jsonb_build_object(
                U&'contrase\00F1a_hash',
                NEW.contrasenia_hash
            )
        );
    END IF;

    RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: asignaciones_rutina; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.asignaciones_rutina (
    id_asignacion integer NOT NULL,
    id_cliente integer NOT NULL,
    id_rutina integer NOT NULL,
    fecha_asignacion date DEFAULT CURRENT_DATE NOT NULL,
    fecha_finalizacion date,
    estado public.estado_asignacion DEFAULT 'ACTIVA'::public.estado_asignacion NOT NULL,
    observaciones text,
    CONSTRAINT chk_fechas CHECK (((fecha_finalizacion IS NULL) OR (fecha_finalizacion >= fecha_asignacion)))
);


--
-- Name: TABLE asignaciones_rutina; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.asignaciones_rutina IS 'Historial de asignaciones (Clase AsignacionRutina)';


--
-- Name: CONSTRAINT chk_fechas ON asignaciones_rutina; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON CONSTRAINT chk_fechas ON public.asignaciones_rutina IS 'La fecha de finalización debe ser posterior a la asignación';


--
-- Name: asignaciones_rutina_id_asignacion_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.asignaciones_rutina_id_asignacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: asignaciones_rutina_id_asignacion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.asignaciones_rutina_id_asignacion_seq OWNED BY public.asignaciones_rutina.id_asignacion;


--
-- Name: clientes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.clientes (
    id_usuario integer NOT NULL,
    peso numeric(5,2) NOT NULL,
    altura numeric(5,2) NOT NULL,
    objetivo character varying(255) NOT NULL,
    fecha_ingreso date DEFAULT CURRENT_DATE NOT NULL,
    peso_objetivo numeric(6,2),
    genero character varying(30),
    CONSTRAINT clientes_altura_check CHECK ((altura > (0)::numeric)),
    CONSTRAINT clientes_peso_check CHECK ((peso > (0)::numeric))
);


--
-- Name: TABLE clientes; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.clientes IS 'Especialización de Usuario: Cliente (hereda de Usuario)';


--
-- Name: COLUMN clientes.objetivo; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.clientes.objetivo IS 'Ej: Bajar de peso, Mejorar resistencia, Mantener condición';


--
-- Name: ejercicios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ejercicios (
    id_ejercicio integer NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    tipo character varying(50) NOT NULL,
    duracion_minutos integer NOT NULL,
    intensidad public.intensidad NOT NULL,
    calorias_estimadas numeric(6,2) NOT NULL,
    creado_por integer,
    CONSTRAINT ejercicios_calorias_estimadas_check CHECK ((calorias_estimadas >= (0)::numeric)),
    CONSTRAINT ejercicios_duracion_minutos_check CHECK ((duracion_minutos > 0))
);


--
-- Name: TABLE ejercicios; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.ejercicios IS 'Catálogo de ejercicios (Clase EjercicioCardio)';


--
-- Name: COLUMN ejercicios.creado_por; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.ejercicios.creado_por IS 'Administrador que creó el ejercicio (asociación)';


--
-- Name: ejercicios_id_ejercicio_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ejercicios_id_ejercicio_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ejercicios_id_ejercicio_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ejercicios_id_ejercicio_seq OWNED BY public.ejercicios.id_ejercicio;


--
-- Name: progreso_mensual; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.progreso_mensual (
    id_progreso integer NOT NULL,
    id_cliente integer NOT NULL,
    mes date NOT NULL,
    peso numeric(5,2) NOT NULL,
    sesiones_completadas integer DEFAULT 0 NOT NULL,
    sesiones_planificadas integer DEFAULT 0 NOT NULL,
    porcentaje_cumplimiento numeric(5,2) DEFAULT 0.0 NOT NULL,
    CONSTRAINT progreso_mensual_peso_check CHECK ((peso > (0)::numeric)),
    CONSTRAINT progreso_mensual_porcentaje_cumplimiento_check CHECK (((porcentaje_cumplimiento >= (0)::numeric) AND (porcentaje_cumplimiento <= (100)::numeric))),
    CONSTRAINT progreso_mensual_sesiones_completadas_check CHECK ((sesiones_completadas >= 0)),
    CONSTRAINT progreso_mensual_sesiones_planificadas_check CHECK ((sesiones_planificadas >= 0))
);


--
-- Name: TABLE progreso_mensual; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.progreso_mensual IS 'Resumen mensual de progreso (Clase ProgresoMensual)';


--
-- Name: COLUMN progreso_mensual.mes; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.progreso_mensual.mes IS 'Primer día del mes (ej. 2026-08-01)';


--
-- Name: progreso_mensual_id_progreso_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.progreso_mensual_id_progreso_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: progreso_mensual_id_progreso_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.progreso_mensual_id_progreso_seq OWNED BY public.progreso_mensual.id_progreso;


--
-- Name: rutina_ejercicios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rutina_ejercicios (
    id_rutina integer NOT NULL,
    id_ejercicio integer NOT NULL,
    orden_ejercicio integer NOT NULL,
    CONSTRAINT rutina_ejercicios_orden_ejercicio_check CHECK ((orden_ejercicio > 0))
);


--
-- Name: TABLE rutina_ejercicios; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.rutina_ejercicios IS 'Relación N:M: una rutina contiene varios ejercicios (agregación)';


--
-- Name: rutinas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rutinas (
    id_rutina integer NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    objetivo character varying(255) NOT NULL,
    nivel public.nivel_rutina NOT NULL,
    duracion_semanas integer NOT NULL,
    creado_por integer,
    fecha_creacion date DEFAULT CURRENT_DATE NOT NULL,
    CONSTRAINT rutinas_duracion_semanas_check CHECK ((duracion_semanas > 0))
);


--
-- Name: TABLE rutinas; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.rutinas IS 'Planes de entrenamiento (Clase Rutina)';


--
-- Name: COLUMN rutinas.creado_por; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.rutinas.creado_por IS 'Administrador que gestiona/crea la rutina (asociación)';


--
-- Name: rutinas_id_rutina_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.rutinas_id_rutina_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: rutinas_id_rutina_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.rutinas_id_rutina_seq OWNED BY public.rutinas.id_rutina;


--
-- Name: sesiones_entrenamiento; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sesiones_entrenamiento (
    id_sesion integer NOT NULL,
    id_cliente integer NOT NULL,
    fecha date DEFAULT CURRENT_DATE NOT NULL,
    duracion_real integer NOT NULL,
    intensidad_real public.intensidad NOT NULL,
    calorias_quemadas numeric(10,2) NOT NULL,
    observaciones text,
    completada boolean DEFAULT false NOT NULL,
    id_rutina integer,
    nombre_ejercicio character varying(100) DEFAULT ''::character varying,
    veces_planificadas integer DEFAULT 1 NOT NULL,
    veces_realizadas integer DEFAULT 0 NOT NULL,
    CONSTRAINT sesiones_entrenamiento_calorias_quemadas_check CHECK ((calorias_quemadas >= (0)::numeric)),
    CONSTRAINT sesiones_entrenamiento_duracion_real_check CHECK ((duracion_real > 0)),
    CONSTRAINT sesiones_veces_planificadas_check CHECK ((veces_planificadas > 0)),
    CONSTRAINT sesiones_veces_realizadas_check CHECK ((veces_realizadas >= 0)),
    CONSTRAINT sesiones_veces_realizadas_max_check CHECK ((veces_realizadas <= veces_planificadas))
);


--
-- Name: TABLE sesiones_entrenamiento; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.sesiones_entrenamiento IS 'Registro de entrenamientos (Clase SesionEntrenamiento)';


--
-- Name: sesiones_entrenamiento_id_sesion_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sesiones_entrenamiento_id_sesion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sesiones_entrenamiento_id_sesion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sesiones_entrenamiento_id_sesion_seq OWNED BY public.sesiones_entrenamiento.id_sesion;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usuarios (
    id_usuario integer NOT NULL,
    nombre character varying(100) NOT NULL,
    apellido character varying(100) NOT NULL,
    correo_electronico character varying(150) NOT NULL,
    contrasenia_hash character varying(255) CONSTRAINT "usuarios_contraseña_hash_not_null" NOT NULL,
    edad integer NOT NULL,
    tipo_usuario public.tipo_usuario DEFAULT 'cliente'::public.tipo_usuario NOT NULL,
    fecha_registro date DEFAULT CURRENT_DATE NOT NULL,
    "contraseña_hash" character varying(255),
    CONSTRAINT usuarios_edad_check CHECK ((edad > 0))
);


--
-- Name: TABLE usuarios; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.usuarios IS 'Base de la herencia: Usuario (abstracta en Python)';


--
-- Name: COLUMN usuarios.contrasenia_hash; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.usuarios.contrasenia_hash IS 'Almacena el hash de la contraseña, no el texto plano';


--
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.usuarios_id_usuario_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.usuarios_id_usuario_seq OWNED BY public.usuarios.id_usuario;


--
-- Name: vw_clientes_completo; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.vw_clientes_completo AS
 SELECT u.id_usuario,
    u.nombre,
    u.apellido,
    u.correo_electronico,
    u.edad,
    u.fecha_registro,
    c.peso,
    c.altura,
    c.objetivo,
    c.fecha_ingreso
   FROM (public.usuarios u
     JOIN public.clientes c ON ((u.id_usuario = c.id_usuario)))
  WHERE (u.tipo_usuario = 'cliente'::public.tipo_usuario);


--
-- Name: VIEW vw_clientes_completo; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON VIEW public.vw_clientes_completo IS 'Vista para obtener todos los datos de un cliente en una sola consulta';


--
-- Name: vw_rutina_activa_cliente; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.vw_rutina_activa_cliente AS
 SELECT a.id_cliente,
    a.id_asignacion,
    r.id_rutina,
    r.nombre AS nombre_rutina,
    r.objetivo,
    r.nivel,
    r.duracion_semanas,
    a.fecha_asignacion,
    a.fecha_finalizacion,
    a.observaciones
   FROM (public.asignaciones_rutina a
     JOIN public.rutinas r ON ((a.id_rutina = r.id_rutina)))
  WHERE (a.estado = 'ACTIVA'::public.estado_asignacion);


--
-- Name: VIEW vw_rutina_activa_cliente; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON VIEW public.vw_rutina_activa_cliente IS 'Vista para obtener la rutina activa de un cliente (filtro por id_cliente)';


--
-- Name: asignaciones_rutina id_asignacion; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.asignaciones_rutina ALTER COLUMN id_asignacion SET DEFAULT nextval('public.asignaciones_rutina_id_asignacion_seq'::regclass);


--
-- Name: ejercicios id_ejercicio; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ejercicios ALTER COLUMN id_ejercicio SET DEFAULT nextval('public.ejercicios_id_ejercicio_seq'::regclass);


--
-- Name: progreso_mensual id_progreso; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.progreso_mensual ALTER COLUMN id_progreso SET DEFAULT nextval('public.progreso_mensual_id_progreso_seq'::regclass);


--
-- Name: rutinas id_rutina; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rutinas ALTER COLUMN id_rutina SET DEFAULT nextval('public.rutinas_id_rutina_seq'::regclass);


--
-- Name: sesiones_entrenamiento id_sesion; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sesiones_entrenamiento ALTER COLUMN id_sesion SET DEFAULT nextval('public.sesiones_entrenamiento_id_sesion_seq'::regclass);


--
-- Name: usuarios id_usuario; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id_usuario SET DEFAULT nextval('public.usuarios_id_usuario_seq'::regclass);


--
-- Data for Name: asignaciones_rutina; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.asignaciones_rutina (id_asignacion, id_cliente, id_rutina, fecha_asignacion, fecha_finalizacion, estado, observaciones) FROM stdin;
384	3884	895	2026-09-24	\N	ACTIVA	Asignación desde prueba de integración
303	3370	643	2026-09-23	\N	ACTIVA	ninguna
255	3152	643	2026-09-22	\N	ACTIVA	ninguna
\.


--
-- Data for Name: clientes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.clientes (id_usuario, peso, altura, objetivo, fecha_ingreso, peso_objetivo, genero) FROM stdin;
3369	34.00	1.76	Subir de peso	2026-09-23	60.00	HOMBRE
3370	56.00	1.80	Subir de peso	2026-09-23	70.00	HOMBRE
3884	75.50	1.75	Mejorar resistencia	2026-09-24	\N	\N
3152	78.00	1.80	Mantener peso	2026-09-22	78.00	HOMBRE
\.


--
-- Data for Name: ejercicios; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ejercicios (id_ejercicio, nombre, descripcion, tipo, duracion_minutos, intensidad, calorias_estimadas, creado_por) FROM stdin;
888	Mancuernas	levantar	HIIT	12	MEDIA	120.00	\N
761	saltar	salta	HIIT	12	MEDIA	120.00	\N
27	Sentadillas	Sentadillas sin pes	Fuerza	10	BAJA	40.00	448
22	Press de banca	Press de banca con barra	Fuerza	15	MEDIA	80.00	\N
23	Cinta caminando	Caminata moderada	Cardio	10	BAJA	50.00	\N
24	Press de banca	Press de banca con barra	Fuerza	15	MEDIA	80.00	\N
25	Cinta caminando	Caminata moderada	Cardio	10	BAJA	50.00	448
26	Elíptica	Ejercicio de baja impacto	Cardio	10	BAJA	60.00	448
28	Press de banca	Press de banca con barra	Fuerza	15	MEDIA	80.00	448
29	Peso muerto	Peso muerto rumano	Fuerza	15	MEDIA	90.00	448
30	Dominadas	Dominadas asistidas	Fuerza	15	MEDIA	70.00	448
635	Caminata	Camina	LISS	6	MEDIA	30.00	\N
21	Cinta caminando	Caminata moderada	Cardio	10	BAJA	40.00	\N
\.


--
-- Data for Name: progreso_mensual; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.progreso_mensual (id_progreso, id_cliente, mes, peso, sesiones_completadas, sesiones_planificadas, porcentaje_cumplimiento) FROM stdin;
160	3152	2026-09-01	78.00	4	12	33.33
\.


--
-- Data for Name: rutina_ejercicios; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.rutina_ejercicios (id_rutina, id_ejercicio, orden_ejercicio) FROM stdin;
895	24	1
895	27	2
895	888	3
42	25	1
42	26	2
42	27	3
43	28	1
43	29	2
643	635	1
643	30	2
643	29	3
42	635	4
\.


--
-- Data for Name: rutinas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.rutinas (id_rutina, nombre, descripcion, objetivo, nivel, duracion_semanas, creado_por, fecha_creacion) FROM stdin;
42	Cardio Básico	Rutina de cardio para principiantes	Perder peso	BASICO	4	448	2026-09-13
895	Rutina Test Integración	Rutina creada para pruebas de integración	Mejorar resistencia	INTERMEDIO	4	\N	2026-09-24
43	Fuerza Intermedio	ganar musculo	Ganar masa muscular	INTERMEDIO	6	448	2026-09-13
643	Cardio Mantenimiento	Intervalos de alta intensidad, pero con volumen moderado	Mantener capacidad cardiovascular	AVANZADO	8	448	2026-09-22
\.


--
-- Data for Name: sesiones_entrenamiento; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sesiones_entrenamiento (id_sesion, id_cliente, fecha, duracion_real, intensidad_real, calorias_quemadas, observaciones, completada, id_rutina, nombre_ejercicio, veces_planificadas, veces_realizadas) FROM stdin;
15429	3152	2026-09-22	12	MEDIA	30.00	Ninguna	f	643	Caminata	1	0
15430	3152	2026-09-22	8	MEDIA	20.00	Ninguna	f	643	Caminata	1	0
15431	3152	2026-09-22	20	MEDIA	50.00	ninguna	f	643	Caminata	3	2
15432	3152	2026-09-22	12	MEDIA	23.00	Ninguna	f	643	Caminata	3	2
15433	3152	2026-09-22	13	MEDIA	22.00	Ninguna	f	643	Caminata	2	2
15460	3152	2026-09-23	6	MEDIA	120.00	ninguna	f	643	trotar	3	1
15466	3152	2026-09-23	12	MEDIA	120.00	ninguna	f	643	pesas	4	2
16134	3884	2026-09-24	45	ALTA	450.50	Sesión de prueba de integración	t	\N		1	0
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.usuarios (id_usuario, nombre, apellido, correo_electronico, contrasenia_hash, edad, tipo_usuario, fecha_registro, "contraseña_hash") FROM stdin;
448	Admin	Sistema	admin@cardio.com	$2b$12$.pYQF7KD5Dtwx828I.5dKOnOd4GliD5WYTKCUYmWivH6ShA1V5FkO	30	administrador	2026-09-13	\N
3370	Pedro	Torres	pedro123@gmail.com	$2b$12$OJj.VO4ZJ8W7qOzsXmAHze4I1dCf/.iPr4s98xbCzgivjnuJmkFKO	23	cliente	2026-09-23	$2b$12$OJj.VO4ZJ8W7qOzsXmAHze4I1dCf/.iPr4s98xbCzgivjnuJmkFKO
3369	Jose	Corzo	jose123@gmail.com	$2b$12$Ovr/vcnnBafNrYOo43blqedNv2xKFr52/g9jEsClBcNJrN9fTeEYW	19	cliente	2026-09-23	$2b$12$Ovr/vcnnBafNrYOo43blqedNv2xKFr52/g9jEsClBcNJrN9fTeEYW
3152	Juan	Perea	juan123@gmail.com	$2b$12$vBU22G8lPS2.Kt2ekiOFLuA1XiO4ypyFT6Ephfg6xas7hnkoLMA/6	20	cliente	2026-09-22	\N
3884	Test	Integracion	test.integracion@wellness.com	a109e36947ad56de1dca1cc49f0ef8ac9ad9a7b1aa0df41fb3c4cb73c1ff01ea	25	cliente	2026-09-24	a109e36947ad56de1dca1cc49f0ef8ac9ad9a7b1aa0df41fb3c4cb73c1ff01ea
\.


--
-- Name: asignaciones_rutina_id_asignacion_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.asignaciones_rutina_id_asignacion_seq', 432, true);


--
-- Name: ejercicios_id_ejercicio_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ejercicios_id_ejercicio_seq', 1008, true);


--
-- Name: progreso_mensual_id_progreso_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.progreso_mensual_id_progreso_seq', 287, true);


--
-- Name: rutinas_id_rutina_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.rutinas_id_rutina_seq', 1015, true);


--
-- Name: sesiones_entrenamiento_id_sesion_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sesiones_entrenamiento_id_sesion_seq', 16164, true);


--
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.usuarios_id_usuario_seq', 4162, true);


--
-- Name: asignaciones_rutina asignaciones_rutina_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.asignaciones_rutina
    ADD CONSTRAINT asignaciones_rutina_pkey PRIMARY KEY (id_asignacion);


--
-- Name: clientes clientes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clientes
    ADD CONSTRAINT clientes_pkey PRIMARY KEY (id_usuario);


--
-- Name: ejercicios ejercicios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ejercicios
    ADD CONSTRAINT ejercicios_pkey PRIMARY KEY (id_ejercicio);


--
-- Name: progreso_mensual progreso_mensual_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.progreso_mensual
    ADD CONSTRAINT progreso_mensual_pkey PRIMARY KEY (id_progreso);


--
-- Name: rutina_ejercicios rutina_ejercicios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rutina_ejercicios
    ADD CONSTRAINT rutina_ejercicios_pkey PRIMARY KEY (id_rutina, id_ejercicio);


--
-- Name: rutinas rutinas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rutinas
    ADD CONSTRAINT rutinas_pkey PRIMARY KEY (id_rutina);


--
-- Name: sesiones_entrenamiento sesiones_entrenamiento_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sesiones_entrenamiento
    ADD CONSTRAINT sesiones_entrenamiento_pkey PRIMARY KEY (id_sesion);


--
-- Name: progreso_mensual unq_cliente_mes; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.progreso_mensual
    ADD CONSTRAINT unq_cliente_mes UNIQUE (id_cliente, mes);


--
-- Name: progreso_mensual uq_progreso_cliente_mes; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.progreso_mensual
    ADD CONSTRAINT uq_progreso_cliente_mes UNIQUE (id_cliente, mes);


--
-- Name: usuarios usuarios_correo_electronico_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_correo_electronico_key UNIQUE (correo_electronico);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id_usuario);


--
-- Name: idx_asignaciones_activa; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_asignaciones_activa ON public.asignaciones_rutina USING btree (id_cliente) WHERE (estado = 'ACTIVA'::public.estado_asignacion);


--
-- Name: idx_asignaciones_cliente; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_asignaciones_cliente ON public.asignaciones_rutina USING btree (id_cliente);


--
-- Name: idx_asignaciones_estado; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_asignaciones_estado ON public.asignaciones_rutina USING btree (estado);


--
-- Name: idx_asignaciones_fechas; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_asignaciones_fechas ON public.asignaciones_rutina USING btree (fecha_asignacion, fecha_finalizacion);


--
-- Name: idx_asignaciones_id_cliente; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_asignaciones_id_cliente ON public.asignaciones_rutina USING btree (id_cliente, estado);


--
-- Name: idx_clientes_id_usuario; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_clientes_id_usuario ON public.clientes USING btree (id_usuario);


--
-- Name: idx_clientes_ingreso; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_clientes_ingreso ON public.clientes USING btree (fecha_ingreso);


--
-- Name: idx_ejercicios_creado_por; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ejercicios_creado_por ON public.ejercicios USING btree (creado_por);


--
-- Name: idx_ejercicios_intensidad; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ejercicios_intensidad ON public.ejercicios USING btree (intensidad);


--
-- Name: idx_ejercicios_nombre; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ejercicios_nombre ON public.ejercicios USING btree (nombre);


--
-- Name: idx_ejercicios_tipo; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ejercicios_tipo ON public.ejercicios USING btree (tipo);


--
-- Name: idx_progreso_cliente; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_progreso_cliente ON public.progreso_mensual USING btree (id_cliente);


--
-- Name: idx_progreso_id_cliente; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_progreso_id_cliente ON public.progreso_mensual USING btree (id_cliente);


--
-- Name: idx_progreso_id_cliente_mes; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_progreso_id_cliente_mes ON public.progreso_mensual USING btree (id_cliente, mes);


--
-- Name: idx_progreso_mes; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_progreso_mes ON public.progreso_mensual USING btree (mes);


--
-- Name: idx_rutina_ejercicios_ejercicio; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_rutina_ejercicios_ejercicio ON public.rutina_ejercicios USING btree (id_ejercicio);


--
-- Name: idx_rutina_ejercicios_orden; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_rutina_ejercicios_orden ON public.rutina_ejercicios USING btree (id_rutina, orden_ejercicio);


--
-- Name: idx_rutina_ejercicios_rutina; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_rutina_ejercicios_rutina ON public.rutina_ejercicios USING btree (id_rutina);


--
-- Name: idx_rutinas_creado_por; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_rutinas_creado_por ON public.rutinas USING btree (creado_por);


--
-- Name: idx_rutinas_nivel; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_rutinas_nivel ON public.rutinas USING btree (nivel);


--
-- Name: idx_rutinas_nombre; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_rutinas_nombre ON public.rutinas USING btree (nombre);


--
-- Name: idx_rutinas_objetivo; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_rutinas_objetivo ON public.rutinas USING btree (objetivo);


--
-- Name: idx_sesiones_cliente; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sesiones_cliente ON public.sesiones_entrenamiento USING btree (id_cliente);


--
-- Name: idx_sesiones_completada; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sesiones_completada ON public.sesiones_entrenamiento USING btree (completada);


--
-- Name: idx_sesiones_fecha; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sesiones_fecha ON public.sesiones_entrenamiento USING btree (fecha);


--
-- Name: idx_sesiones_id_cliente; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sesiones_id_cliente ON public.sesiones_entrenamiento USING btree (id_cliente);


--
-- Name: idx_sesiones_id_cliente_completada; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sesiones_id_cliente_completada ON public.sesiones_entrenamiento USING btree (id_cliente, completada);


--
-- Name: idx_sesiones_id_cliente_fecha; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sesiones_id_cliente_fecha ON public.sesiones_entrenamiento USING btree (id_cliente, fecha);


--
-- Name: idx_usuarios_correo; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_usuarios_correo ON public.usuarios USING btree (correo_electronico);


--
-- Name: idx_usuarios_tipo; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_usuarios_tipo ON public.usuarios USING btree (tipo_usuario);


--
-- Name: usuarios trigger_sincronizar_hash_contrasena; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trigger_sincronizar_hash_contrasena BEFORE INSERT OR UPDATE ON public.usuarios FOR EACH ROW EXECUTE FUNCTION public.sincronizar_hash_contrasena();


--
-- Name: asignaciones_rutina asignaciones_rutina_id_cliente_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.asignaciones_rutina
    ADD CONSTRAINT asignaciones_rutina_id_cliente_fkey FOREIGN KEY (id_cliente) REFERENCES public.clientes(id_usuario) ON DELETE CASCADE;


--
-- Name: asignaciones_rutina asignaciones_rutina_id_rutina_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.asignaciones_rutina
    ADD CONSTRAINT asignaciones_rutina_id_rutina_fkey FOREIGN KEY (id_rutina) REFERENCES public.rutinas(id_rutina) ON DELETE RESTRICT;


--
-- Name: clientes clientes_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clientes
    ADD CONSTRAINT clientes_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;


--
-- Name: ejercicios ejercicios_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ejercicios
    ADD CONSTRAINT ejercicios_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id_usuario) ON DELETE SET NULL;


--
-- Name: sesiones_entrenamiento fk_sesion_rutina; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sesiones_entrenamiento
    ADD CONSTRAINT fk_sesion_rutina FOREIGN KEY (id_rutina) REFERENCES public.rutinas(id_rutina);


--
-- Name: progreso_mensual progreso_mensual_id_cliente_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.progreso_mensual
    ADD CONSTRAINT progreso_mensual_id_cliente_fkey FOREIGN KEY (id_cliente) REFERENCES public.clientes(id_usuario) ON DELETE CASCADE;


--
-- Name: rutina_ejercicios rutina_ejercicios_id_ejercicio_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rutina_ejercicios
    ADD CONSTRAINT rutina_ejercicios_id_ejercicio_fkey FOREIGN KEY (id_ejercicio) REFERENCES public.ejercicios(id_ejercicio) ON DELETE CASCADE;


--
-- Name: rutina_ejercicios rutina_ejercicios_id_rutina_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rutina_ejercicios
    ADD CONSTRAINT rutina_ejercicios_id_rutina_fkey FOREIGN KEY (id_rutina) REFERENCES public.rutinas(id_rutina) ON DELETE CASCADE;


--
-- Name: rutinas rutinas_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rutinas
    ADD CONSTRAINT rutinas_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id_usuario) ON DELETE SET NULL;


--
-- Name: sesiones_entrenamiento sesiones_entrenamiento_id_cliente_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sesiones_entrenamiento
    ADD CONSTRAINT sesiones_entrenamiento_id_cliente_fkey FOREIGN KEY (id_cliente) REFERENCES public.clientes(id_usuario) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict v1TeYGiRKujHJEuTxHdp0JinjcTrieN1h9N0XOHscO1mTxZyJqaxjYnAW98lja9

