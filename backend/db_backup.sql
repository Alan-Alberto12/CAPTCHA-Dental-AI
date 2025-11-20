--
-- PostgreSQL database dump
--

\restrict H4DaLfEcPuNlNI6YI5bJQOIPNx6b75n9zxTw6065t7t8pWdeapPpSep9FagKHiG

-- Dumped from database version 15.14
-- Dumped by pg_dump version 15.14

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: captcha_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO captcha_user;

--
-- Name: annotation_images; Type: TABLE; Schema: public; Owner: captcha_user
--

CREATE TABLE public.annotation_images (
    id integer NOT NULL,
    annotation_id integer NOT NULL,
    image_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.annotation_images OWNER TO captcha_user;

--
-- Name: annotation_images_id_seq; Type: SEQUENCE; Schema: public; Owner: captcha_user
--

CREATE SEQUENCE public.annotation_images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.annotation_images_id_seq OWNER TO captcha_user;

--
-- Name: annotation_images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: captcha_user
--

ALTER SEQUENCE public.annotation_images_id_seq OWNED BY public.annotation_images.id;


--
-- Name: annotations; Type: TABLE; Schema: public; Owner: captcha_user
--

CREATE TABLE public.annotations (
    id integer NOT NULL,
    session_id integer,
    question_id integer,
    is_correct boolean,
    time_spent double precision,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.annotations OWNER TO captcha_user;

--
-- Name: annotations_id_seq; Type: SEQUENCE; Schema: public; Owner: captcha_user
--

CREATE SEQUENCE public.annotations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.annotations_id_seq OWNER TO captcha_user;

--
-- Name: annotations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: captcha_user
--

ALTER SEQUENCE public.annotations_id_seq OWNED BY public.annotations.id;


--
-- Name: email_confirmation_tokens; Type: TABLE; Schema: public; Owner: captcha_user
--

CREATE TABLE public.email_confirmation_tokens (
    id integer NOT NULL,
    user_id integer NOT NULL,
    token_hash character varying(64) NOT NULL,
    expires timestamp with time zone NOT NULL
);


ALTER TABLE public.email_confirmation_tokens OWNER TO captcha_user;

--
-- Name: email_confirmation_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: captcha_user
--

CREATE SEQUENCE public.email_confirmation_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.email_confirmation_tokens_id_seq OWNER TO captcha_user;

--
-- Name: email_confirmation_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: captcha_user
--

ALTER SEQUENCE public.email_confirmation_tokens_id_seq OWNED BY public.email_confirmation_tokens.id;


--
-- Name: images; Type: TABLE; Schema: public; Owner: captcha_user
--

CREATE TABLE public.images (
    id integer NOT NULL,
    filename character varying NOT NULL,
    image_url character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.images OWNER TO captcha_user;

--
-- Name: images_id_seq; Type: SEQUENCE; Schema: public; Owner: captcha_user
--

CREATE SEQUENCE public.images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.images_id_seq OWNER TO captcha_user;

--
-- Name: images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: captcha_user
--

ALTER SEQUENCE public.images_id_seq OWNED BY public.images.id;


--
-- Name: password_reset_tokens; Type: TABLE; Schema: public; Owner: captcha_user
--

CREATE TABLE public.password_reset_tokens (
    id integer NOT NULL,
    user_id integer NOT NULL,
    token_hash character varying(64) NOT NULL,
    expires timestamp with time zone NOT NULL
);


ALTER TABLE public.password_reset_tokens OWNER TO captcha_user;

--
-- Name: password_reset_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: captcha_user
--

CREATE SEQUENCE public.password_reset_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.password_reset_tokens_id_seq OWNER TO captcha_user;

--
-- Name: password_reset_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: captcha_user
--

ALTER SEQUENCE public.password_reset_tokens_id_seq OWNED BY public.password_reset_tokens.id;


--
-- Name: questions; Type: TABLE; Schema: public; Owner: captcha_user
--

CREATE TABLE public.questions (
    id integer NOT NULL,
    question_text text NOT NULL,
    question_type character varying NOT NULL,
    active boolean,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.questions OWNER TO captcha_user;

--
-- Name: questions_id_seq; Type: SEQUENCE; Schema: public; Owner: captcha_user
--

CREATE SEQUENCE public.questions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.questions_id_seq OWNER TO captcha_user;

--
-- Name: questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: captcha_user
--

ALTER SEQUENCE public.questions_id_seq OWNED BY public.questions.id;


--
-- Name: session_images; Type: TABLE; Schema: public; Owner: captcha_user
--

CREATE TABLE public.session_images (
    id integer NOT NULL,
    session_id integer NOT NULL,
    image_id integer NOT NULL,
    image_order integer NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.session_images OWNER TO captcha_user;

--
-- Name: session_images_id_seq; Type: SEQUENCE; Schema: public; Owner: captcha_user
--

CREATE SEQUENCE public.session_images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.session_images_id_seq OWNER TO captcha_user;

--
-- Name: session_images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: captcha_user
--

ALTER SEQUENCE public.session_images_id_seq OWNED BY public.session_images.id;


--
-- Name: session_questions; Type: TABLE; Schema: public; Owner: captcha_user
--

CREATE TABLE public.session_questions (
    id integer NOT NULL,
    session_id integer NOT NULL,
    question_id integer NOT NULL,
    question_order integer NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.session_questions OWNER TO captcha_user;

--
-- Name: session_questions_id_seq; Type: SEQUENCE; Schema: public; Owner: captcha_user
--

CREATE SEQUENCE public.session_questions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.session_questions_id_seq OWNER TO captcha_user;

--
-- Name: session_questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: captcha_user
--

ALTER SEQUENCE public.session_questions_id_seq OWNED BY public.session_questions.id;


--
-- Name: sessions; Type: TABLE; Schema: public; Owner: captcha_user
--

CREATE TABLE public.sessions (
    id integer NOT NULL,
    user_id integer,
    is_completed boolean,
    started_at timestamp with time zone DEFAULT now(),
    completed_at timestamp with time zone
);


ALTER TABLE public.sessions OWNER TO captcha_user;

--
-- Name: sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: captcha_user
--

CREATE SEQUENCE public.sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sessions_id_seq OWNER TO captcha_user;

--
-- Name: sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: captcha_user
--

ALTER SEQUENCE public.sessions_id_seq OWNED BY public.sessions.id;


--
-- Name: user_stats; Type: TABLE; Schema: public; Owner: captcha_user
--

CREATE TABLE public.user_stats (
    id integer NOT NULL,
    user_id integer,
    total_points integer,
    total_annotations integer,
    accuracy_rate double precision,
    daily_streak integer,
    last_active timestamp with time zone DEFAULT now()
);


ALTER TABLE public.user_stats OWNER TO captcha_user;

--
-- Name: user_stats_id_seq; Type: SEQUENCE; Schema: public; Owner: captcha_user
--

CREATE SEQUENCE public.user_stats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_stats_id_seq OWNER TO captcha_user;

--
-- Name: user_stats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: captcha_user
--

ALTER SEQUENCE public.user_stats_id_seq OWNED BY public.user_stats.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: captcha_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying NOT NULL,
    username character varying NOT NULL,
    hashed_password character varying NOT NULL,
    first_name character varying,
    last_name character varying,
    is_active boolean,
    is_admin boolean,
    is_verified boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.users OWNER TO captcha_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: captcha_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO captcha_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: captcha_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: annotation_images id; Type: DEFAULT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.annotation_images ALTER COLUMN id SET DEFAULT nextval('public.annotation_images_id_seq'::regclass);


--
-- Name: annotations id; Type: DEFAULT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.annotations ALTER COLUMN id SET DEFAULT nextval('public.annotations_id_seq'::regclass);


--
-- Name: email_confirmation_tokens id; Type: DEFAULT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.email_confirmation_tokens ALTER COLUMN id SET DEFAULT nextval('public.email_confirmation_tokens_id_seq'::regclass);


--
-- Name: images id; Type: DEFAULT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.images ALTER COLUMN id SET DEFAULT nextval('public.images_id_seq'::regclass);


--
-- Name: password_reset_tokens id; Type: DEFAULT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.password_reset_tokens ALTER COLUMN id SET DEFAULT nextval('public.password_reset_tokens_id_seq'::regclass);


--
-- Name: questions id; Type: DEFAULT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.questions ALTER COLUMN id SET DEFAULT nextval('public.questions_id_seq'::regclass);


--
-- Name: session_images id; Type: DEFAULT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.session_images ALTER COLUMN id SET DEFAULT nextval('public.session_images_id_seq'::regclass);


--
-- Name: session_questions id; Type: DEFAULT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.session_questions ALTER COLUMN id SET DEFAULT nextval('public.session_questions_id_seq'::regclass);


--
-- Name: sessions id; Type: DEFAULT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.sessions ALTER COLUMN id SET DEFAULT nextval('public.sessions_id_seq'::regclass);


--
-- Name: user_stats id; Type: DEFAULT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.user_stats ALTER COLUMN id SET DEFAULT nextval('public.user_stats_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: captcha_user
--

COPY public.alembic_version (version_num) FROM stdin;
d0f4b41cee0c
\.


--
-- Data for Name: annotation_images; Type: TABLE DATA; Schema: public; Owner: captcha_user
--

COPY public.annotation_images (id, annotation_id, image_id, created_at) FROM stdin;
\.


--
-- Data for Name: annotations; Type: TABLE DATA; Schema: public; Owner: captcha_user
--

COPY public.annotations (id, session_id, question_id, is_correct, time_spent, created_at) FROM stdin;
\.


--
-- Data for Name: email_confirmation_tokens; Type: TABLE DATA; Schema: public; Owner: captcha_user
--

COPY public.email_confirmation_tokens (id, user_id, token_hash, expires) FROM stdin;
\.


--
-- Data for Name: images; Type: TABLE DATA; Schema: public; Owner: captcha_user
--

COPY public.images (id, filename, image_url, created_at) FROM stdin;
1	cat-paws.jpg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/cat-paws_9315b68d.jpg	2025-11-15 17:53:29.074449+00
2	white-cat.jpg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/white-cat_c812d8a5.jpg	2025-11-15 17:53:29.871514+00
3	DIG01_C5sDR (2).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C5sDR (2)_ac2453e4.jpeg	2025-11-15 18:30:58.822904+00
4	DIG01_C5sDR (6).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C5sDR (6)_7a08bcd0.jpeg	2025-11-15 18:30:59.477563+00
5	DIG01_C5sDR (4).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C5sDR (4)_1158a3f1.jpeg	2025-11-15 18:30:59.607398+00
6	DIG01_C5sDR (3).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C5sDR (3)_25587641.jpeg	2025-11-15 18:30:59.730861+00
7	DIG01_C5sDR (1).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C5sDR (1)_68a6046d.jpeg	2025-11-15 18:30:59.856885+00
8	DIG01_C5sDR (5).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C5sDR (5)_bc2749ec.jpeg	2025-11-15 18:30:59.981419+00
9	DIG01_C5sDR (7).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C5sDR (7)_b80c0c37.jpeg	2025-11-15 18:31:00.121655+00
10	DIG01_C5sDR (9).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C5sDR (9)_527c71e9.jpeg	2025-11-15 18:31:00.245684+00
11	DIG01_C5sDR (15).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C5sDR (15)_9518126c.jpeg	2025-11-15 18:31:00.365991+00
12	DIG01_C5sDR (11).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C5sDR (11)_2fc184e3.jpeg	2025-11-15 18:31:00.501511+00
13	DIG01_C5sDR (13).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C5sDR (13)_d4df4217.jpeg	2025-11-15 18:31:00.627065+00
14	DIG01_C5sDR (8).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C5sDR (8)_59a205bb.jpeg	2025-11-15 18:31:00.75795+00
15	DIG01_C5sDR (14).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C5sDR (14)_527ea1c7.jpeg	2025-11-15 18:31:00.875636+00
16	DIG01_C5sDR (12).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C5sDR (12)_74dd88db.jpeg	2025-11-15 18:31:00.998707+00
17	DIG01_C5sDR (10).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C5sDR (10)_6aa63155.jpeg	2025-11-15 18:31:01.124032+00
18	DIG01_C1sDR (48).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (48)_ccebf306.jpeg	2025-11-15 18:31:01.240184+00
19	DIG01_C1sDR (30).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (30)_0a513d50.jpeg	2025-11-15 18:31:01.35965+00
20	DIG01_C1sDR (51).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (51)_16066ee1.jpeg	2025-11-15 18:31:01.479055+00
21	DIG01_C1sDR (14).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (14)_67e24cd9.jpeg	2025-11-15 18:31:01.595994+00
22	DIG01_C1sDR (29).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (29)_4e3e71df.jpeg	2025-11-15 18:31:01.865363+00
23	DIG01_C1sDR (53).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (53)_d74a3978.jpeg	2025-11-15 18:31:01.97534+00
24	DIG01_C1sDR (16).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (16)_1d911bef.jpeg	2025-11-15 18:31:02.089523+00
25	DIG01_C1sDR (32).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (32)_04dedbb8.jpeg	2025-11-15 18:31:02.236727+00
26	DIG01_C1sDR (9).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (9)_b0a71e98.jpeg	2025-11-15 18:31:02.372036+00
27	DIG01_C1sDR (73).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (73)_856e43ac.jpeg	2025-11-15 18:31:02.488974+00
28	DIG01_C1sDR (36).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (36)_adfbb3d5.jpeg	2025-11-15 18:31:02.610638+00
29	DIG01_C1sDR (57).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (57)_a0cc4fc0.jpeg	2025-11-15 18:31:02.737765+00
30	DIG01_C1sDR (12).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (12)_6914e391.jpeg	2025-11-15 18:31:02.859628+00
31	DIG01_C1sDR (55).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (55)_b906d219.jpeg	2025-11-15 18:31:02.987034+00
32	DIG01_C1sDR (10).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (10)_f6e59c1e.jpeg	2025-11-15 18:31:03.106739+00
33	DIG01_C1sDR (68).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (68)_e6e7a212.jpeg	2025-11-15 18:31:03.237067+00
34	DIG01_C1sDR (71).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (71)_41cc2433.jpeg	2025-11-15 18:31:03.363802+00
35	DIG01_C1sDR (34).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (34)_4984153f.jpeg	2025-11-15 18:31:03.487754+00
36	DIG01_C1sDR (17).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (17)_35b5942a.jpeg	2025-11-15 18:31:03.609139+00
37	DIG01_C1sDR (52).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (52)_4a6ee3cb.jpeg	2025-11-15 18:31:03.737124+00
38	DIG01_C1sDR (8).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (8)_1ba7f134.jpeg	2025-11-15 18:31:03.857508+00
39	DIG01_C1sDR (33).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (33)_45fd2ed0.jpeg	2025-11-15 18:31:03.973535+00
40	DIG01_C1sDR (31).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (31)_376e9a6e.jpeg	2025-11-15 18:31:04.096036+00
41	DIG01_C1sDR (74).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (74)_97353096.jpeg	2025-11-15 18:31:04.218701+00
42	DIG01_C1sDR (49).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (49)_86be9aa5.jpeg	2025-11-15 18:31:04.341905+00
43	DIG01_C1sDR (28).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (28)_f8261277.jpeg	2025-11-15 18:31:04.458721+00
44	DIG01_C1sDR (15).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (15)_4cf49ff1.jpeg	2025-11-15 18:31:04.579761+00
45	DIG01_C1sDR (50).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (50)_96fa1435.jpeg	2025-11-15 18:31:04.739828+00
46	DIG01_C1sDR (69).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (69)_d3e43afb.jpeg	2025-11-15 18:31:04.860381+00
47	DIG01_C1sDR (11).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (11)_fbd2c908.jpeg	2025-11-15 18:31:04.986487+00
48	DIG01_C1sDR (54).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (54)_a6bb3912.jpeg	2025-11-15 18:31:05.108503+00
49	DIG01_C1sDR (35).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (35)_7749cebb.jpeg	2025-11-15 18:31:05.228807+00
50	DIG01_C1sDR (70).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (70)_7994ccbe.jpeg	2025-11-15 18:31:05.349314+00
51	DIG01_C1sDR (37).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (37)_6fdf2cd1.jpeg	2025-11-15 18:31:05.492711+00
52	DIG01_C1sDR (72).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (72)_780a9a3d.jpeg	2025-11-15 18:31:05.612178+00
53	DIG01_C1sDR (13).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (13)_644ab096.jpeg	2025-11-15 18:31:05.730421+00
54	DIG01_C1sDR (56).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (56)_bdd0b161.jpeg	2025-11-15 18:31:05.85662+00
55	DIG01_C1sDR (67).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (67)_c89bff69.jpeg	2025-11-15 18:31:05.984444+00
56	DIG01_C1sDR (22).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (22)_0750846b.jpeg	2025-11-15 18:31:06.105524+00
57	DIG01_C1sDR (43).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (43)_97dfe93f.jpeg	2025-11-15 18:31:06.224019+00
58	DIG01_C1sDR (2).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (2)_c721b688.jpeg	2025-11-15 18:31:06.350813+00
59	DIG01_C1sDR (41).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (41)_4b05fa32.jpeg	2025-11-15 18:31:06.468817+00
60	DIG01_C1sDR (39).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (39)_cb73a040.jpeg	2025-11-15 18:31:06.596364+00
61	DIG01_C1sDR (58).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (58)_2a39b3fa.jpeg	2025-11-15 18:31:06.717071+00
62	DIG01_C1sDR (65).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (65)_c2851c12.jpeg	2025-11-15 18:31:06.837613+00
63	DIG01_C1sDR (20).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (20)_5d2b45ad.jpeg	2025-11-15 18:31:06.959353+00
64	DIG01_C1sDR (19).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (19)_999005b1.jpeg	2025-11-15 18:31:07.084278+00
65	DIG01_C1sDR (61).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (61)_7202f3d7.jpeg	2025-11-15 18:31:07.206879+00
66	DIG01_C1sDR (24).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (24)_a5a5bcad.jpeg	2025-11-15 18:31:07.336931+00
67	DIG01_C1sDR (45).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (45)_e4fcacf4.jpeg	2025-11-15 18:31:07.459711+00
68	DIG01_C1sDR (6).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (6)_7ea6d01e.jpeg	2025-11-15 18:31:07.582085+00
69	DIG01_C1sDR (47).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (47)_73af309e.jpeg	2025-11-15 18:31:07.711663+00
70	DIG01_C1sDR (4).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (4)_dc00e779.jpeg	2025-11-15 18:31:07.833867+00
71	DIG01_C1sDR (63).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (63)_d90a36b9.jpeg	2025-11-15 18:31:07.948964+00
72	DIG01_C1sDR (26).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (26)_b826046e.jpeg	2025-11-15 18:31:08.062284+00
73	DIG01_C1sDR (38).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (38)_b2ce7b60.jpeg	2025-11-15 18:31:08.184585+00
74	DIG01_C1sDR (40).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (40)_25eb0250.jpeg	2025-11-15 18:31:08.306266+00
75	DIG01_C1sDR (3).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (3)_3b12f711.jpeg	2025-11-15 18:31:08.426432+00
76	DIG01_C1sDR (21).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (21)_e9c5f86e.jpeg	2025-11-15 18:31:08.548155+00
77	DIG01_C1sDR (64).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (64)_a3810edd.jpeg	2025-11-15 18:31:08.666036+00
78	DIG01_C1sDR (59).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (59)_7d2b0c77.jpeg	2025-11-15 18:31:08.792944+00
79	DIG01_C1sDR (23).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (23)_b499854e.jpeg	2025-11-15 18:31:08.911466+00
80	DIG01_C1sDR (66).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (66)_e3b17a03.jpeg	2025-11-15 18:31:09.035245+00
81	DIG01_C1sDR (42).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (42)_4e29699d.jpeg	2025-11-15 18:31:09.158185+00
82	DIG01_C1sDR (1).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (1)_cfd4e65c.jpeg	2025-11-15 18:31:09.334691+00
83	DIG01_C1sDR (5).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (5)_97d81aac.jpeg	2025-11-15 18:31:09.451427+00
84	DIG01_C1sDR (46).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (46)_5c242bdf.jpeg	2025-11-15 18:31:09.576386+00
85	DIG01_C1sDR (27).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (27)_48725701.jpeg	2025-11-15 18:31:09.695444+00
86	DIG01_C1sDR (62).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (62)_3dadcc60.jpeg	2025-11-15 18:31:09.814918+00
87	DIG01_C1sDR (25).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (25)_0ad6e331.jpeg	2025-11-15 18:31:09.934144+00
88	DIG01_C1sDR (60).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (60)_f6df3821.jpeg	2025-11-15 18:31:10.051211+00
89	DIG01_C1sDR (18).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (18)_6649b6fc.jpeg	2025-11-15 18:31:10.169321+00
90	DIG01_C1sDR (7).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (7)_2d133089.jpeg	2025-11-15 18:31:10.290565+00
91	DIG01_C1sDR (44).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C1sDR (44)_7e7ccb69.jpeg	2025-11-15 18:31:10.408309+00
92	DIG01_C4sDR (86).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (86)_f81c5d30.jpeg	2025-11-15 18:31:10.538781+00
93	DIG01_C4sDR (120).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (120)_11f5d71b.jpeg	2025-11-15 18:31:10.657146+00
94	DIG01_C4sDR (165).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (165)_c71f54e4.jpeg	2025-11-15 18:31:10.778891+00
95	DIG01_C4sDR (198).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (198)_1cc0f78c.jpeg	2025-11-15 18:31:10.900927+00
96	DIG01_C4sDR (158).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (158)_8a912311.jpeg	2025-11-15 18:31:11.022866+00
97	DIG01_C4sDR (46).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (46)_c6c4d40a.jpeg	2025-11-15 18:31:11.144768+00
98	DIG01_C4sDR (139).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (139)_806b5ec3.jpeg	2025-11-15 18:31:11.264001+00
99	DIG01_C4sDR (181).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (181)_983cadf4.jpeg	2025-11-15 18:31:11.389606+00
100	DIG01_C4sDR (27).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (27)_025f0338.jpeg	2025-11-15 18:31:11.505798+00
101	DIG01_C4sDR (62).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (62)_7fead42e.jpeg	2025-11-15 18:31:11.781116+00
102	DIG01_C4sDR (205).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (205)_8ea012d8.jpeg	2025-11-15 18:31:11.947236+00
103	DIG01_C4sDR (104).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (104)_1f24339b.jpeg	2025-11-15 18:31:12.068376+00
104	DIG01_C4sDR (141).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (141)_15e7093d.jpeg	2025-11-15 18:31:12.322595+00
105	DIG01_C4sDR (18).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (18)_37843368.jpeg	2025-11-15 18:31:12.453022+00
106	DIG01_C4sDR (106).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (106)_d9a31675.jpeg	2025-11-15 18:31:12.577776+00
107	DIG01_C4sDR (143).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (143)_f389e721.jpeg	2025-11-15 18:31:12.693684+00
108	DIG01_C4sDR (207).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (207)_28fdc236.jpeg	2025-11-15 18:31:12.8086+00
109	DIG01_C4sDR (183).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (183)_828889b5.jpeg	2025-11-15 18:31:12.934555+00
110	DIG01_C4sDR (25).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (25)_2a427730.jpeg	2025-11-15 18:31:13.051974+00
111	DIG01_C4sDR (60).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (60)_ebbdd9e5.jpeg	2025-11-15 18:31:13.174739+00
112	DIG01_C4sDR (44).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (44)_08328aa4.jpeg	2025-11-15 18:31:13.293239+00
113	DIG01_C4sDR (84).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (84)_07e79fc7.jpeg	2025-11-15 18:31:13.410533+00
114	DIG01_C4sDR (79).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (79)_fdd7080c.jpeg	2025-11-15 18:31:13.540307+00
115	DIG01_C4sDR (122).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (122)_158ddf09.jpeg	2025-11-15 18:31:13.65993+00
116	DIG01_C4sDR (167).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (167)_24b91160.jpeg	2025-11-15 18:31:13.785288+00
117	DIG01_C4sDR (40).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (40)_d1419999.jpeg	2025-11-15 18:31:13.916506+00
118	DIG01_C4sDR (126).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (126)_e24e24c6.jpeg	2025-11-15 18:31:14.037577+00
119	DIG01_C4sDR (163).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (163)_75b4cbe0.jpeg	2025-11-15 18:31:14.151425+00
120	DIG01_C4sDR (38).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (38)_dd0fc4db.jpeg	2025-11-15 18:31:14.282094+00
121	DIG01_C4sDR (80).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (80)_fef4b0c6.jpeg	2025-11-15 18:31:14.394381+00
122	DIG01_C4sDR (203).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (203)_5819af44.jpeg	2025-11-15 18:31:14.517587+00
123	DIG01_C4sDR (102).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (102)_26222d69.jpeg	2025-11-15 18:31:14.636268+00
124	DIG01_C4sDR (147).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (147)_e90f4dd9.jpeg	2025-11-15 18:31:14.753899+00
125	DIG01_C4sDR (59).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (59)_78aad654.jpeg	2025-11-15 18:31:14.897682+00
126	DIG01_C4sDR (9).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (9)_9bb2a936.jpeg	2025-11-15 18:31:15.016576+00
127	DIG01_C4sDR (21).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (21)_c03bffbf.jpeg	2025-11-15 18:31:15.156489+00
128	DIG01_C4sDR (64).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (64)_1b724c1a.jpeg	2025-11-15 18:31:15.283258+00
129	DIG01_C4sDR (99).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (99)_4c21d732.jpeg	2025-11-15 18:31:15.40446+00
130	DIG01_C4sDR (187).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (187)_2f7cea85.jpeg	2025-11-15 18:31:15.529929+00
131	DIG01_C4sDR (23).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (23)_c5012dc3.jpeg	2025-11-15 18:31:15.645153+00
132	DIG01_C4sDR (66).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (66)_036a2ea8.jpeg	2025-11-15 18:31:15.764195+00
133	DIG01_C4sDR (185).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (185)_cafb562d.jpeg	2025-11-15 18:31:15.883029+00
134	DIG01_C4sDR (178).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (178)_12338c4a.jpeg	2025-11-15 18:31:15.99662+00
135	DIG01_C4sDR (100).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (100)_d97750c0.jpeg	2025-11-15 18:31:16.119197+00
136	DIG01_C4sDR (145).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (145)_f7d17316.jpeg	2025-11-15 18:31:16.236608+00
137	DIG01_C4sDR (201).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (201)_cb0408ac.jpeg	2025-11-15 18:31:16.349643+00
138	DIG01_C4sDR (124).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (124)_0e3115f0.jpeg	2025-11-15 18:31:16.470123+00
139	DIG01_C4sDR (161).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (161)_908e0aa4.jpeg	2025-11-15 18:31:16.585321+00
140	DIG01_C4sDR (82).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (82)_daecace5.jpeg	2025-11-15 18:31:16.701003+00
141	DIG01_C4sDR (42).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (42)_3202dec7.jpeg	2025-11-15 18:31:16.852004+00
142	DIG01_C4sDR (119).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (119)_9a60a050.jpeg	2025-11-15 18:31:16.967653+00
143	DIG01_C4sDR (61).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (61)_e9c3bac1.jpeg	2025-11-15 18:31:17.116036+00
144	DIG01_C4sDR (24).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (24)_65a29272.jpeg	2025-11-15 18:31:17.237693+00
145	DIG01_C4sDR (182).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (182)_01af104f.jpeg	2025-11-15 18:31:17.341254+00
146	DIG01_C4sDR (142).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (142)_622447b0.jpeg	2025-11-15 18:31:17.449368+00
147	DIG01_C4sDR (107).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (107)_a5dff25b.jpeg	2025-11-15 18:31:17.567081+00
148	DIG01_C4sDR (206).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (206)_258eff50.jpeg	2025-11-15 18:31:17.683861+00
149	DIG01_C4sDR (19).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (19)_da223218.jpeg	2025-11-15 18:31:17.791503+00
150	DIG01_C4sDR (166).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (166)_552c555f.jpeg	2025-11-15 18:31:17.902015+00
151	DIG01_C4sDR (123).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (123)_778a87f5.jpeg	2025-11-15 18:31:18.014928+00
152	DIG01_C4sDR (85).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (85)_8bc00824.jpeg	2025-11-15 18:31:18.126223+00
153	DIG01_C4sDR (78).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (78)_b61dcb47.jpeg	2025-11-15 18:31:18.237734+00
154	DIG01_C4sDR (45).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (45)_80e6d048.jpeg	2025-11-15 18:31:18.343303+00
155	DIG01_C4sDR (47).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (47)_377914e6.jpeg	2025-11-15 18:31:18.456365+00
156	DIG01_C4sDR (159).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (159)_2e877687.jpeg	2025-11-15 18:31:18.564196+00
157	DIG01_C4sDR (164).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (164)_1af9c9b1.jpeg	2025-11-15 18:31:18.676408+00
158	DIG01_C4sDR (121).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (121)_f48769a5.jpeg	2025-11-15 18:31:18.786567+00
159	DIG01_C4sDR (199).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (199)_072713c6.jpeg	2025-11-15 18:31:18.896635+00
160	DIG01_C4sDR (87).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (87)_ce70e6b6.jpeg	2025-11-15 18:31:19.034234+00
161	DIG01_C4sDR (204).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (204)_c581f856.jpeg	2025-11-15 18:31:19.145343+00
162	DIG01_C4sDR (140).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (140)_1dc37269.jpeg	2025-11-15 18:31:19.255428+00
163	DIG01_C4sDR (105).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (105)_f91dffcf.jpeg	2025-11-15 18:31:19.361014+00
164	DIG01_C4sDR (63).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (63)_e624eb72.jpeg	2025-11-15 18:31:19.472174+00
165	DIG01_C4sDR (26).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (26)_23ac7042.jpeg	2025-11-15 18:31:19.579087+00
166	DIG01_C4sDR (138).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (138)_1b85d329.jpeg	2025-11-15 18:31:19.68812+00
167	DIG01_C4sDR (180).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (180)_4c4f40d9.jpeg	2025-11-15 18:31:19.796886+00
168	DIG01_C4sDR (144).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (144)_634b0600.jpeg	2025-11-15 18:31:19.912499+00
169	DIG01_C4sDR (101).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (101)_808f89ce.jpeg	2025-11-15 18:31:20.020989+00
170	DIG01_C4sDR (200).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (200)_0676a2e7.jpeg	2025-11-15 18:31:20.130174+00
171	DIG01_C4sDR (184).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (184)_a67a1b92.jpeg	2025-11-15 18:31:20.24036+00
172	DIG01_C4sDR (179).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (179)_19158586.jpeg	2025-11-15 18:31:20.347386+00
173	DIG01_C4sDR (67).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (67)_3d95b830.jpeg	2025-11-15 18:31:20.458753+00
174	DIG01_C4sDR (22).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (22)_aa3fd39d.jpeg	2025-11-15 18:31:20.567513+00
175	DIG01_C4sDR (118).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (118)_8795e013.jpeg	2025-11-15 18:31:20.676374+00
176	DIG01_C4sDR (43).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (43)_f2f56626.jpeg	2025-11-15 18:31:20.782082+00
177	DIG01_C4sDR (83).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (83)_a9a89e03.jpeg	2025-11-15 18:31:20.893711+00
178	DIG01_C4sDR (160).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (160)_84b4ad2d.jpeg	2025-11-15 18:31:21.037028+00
179	DIG01_C4sDR (125).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (125)_cd7f6dfe.jpeg	2025-11-15 18:31:21.14489+00
180	DIG01_C4sDR (39).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (39)_7356b806.jpeg	2025-11-15 18:31:21.254218+00
181	DIG01_C4sDR (81).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (81)_64261606.jpeg	2025-11-15 18:31:21.363568+00
182	DIG01_C4sDR (162).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (162)_6e53de3e.jpeg	2025-11-15 18:31:21.476177+00
183	DIG01_C4sDR (127).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (127)_60f6388d.jpeg	2025-11-15 18:31:21.586672+00
184	DIG01_C4sDR (41).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (41)_f40adfa8.jpeg	2025-11-15 18:31:21.737062+00
185	DIG01_C4sDR (186).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (186)_e6966949.jpeg	2025-11-15 18:31:21.874967+00
186	DIG01_C4sDR (65).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (65)_febebfa8.jpeg	2025-11-15 18:31:21.995011+00
187	DIG01_C4sDR (20).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (20)_3b55f366.jpeg	2025-11-15 18:31:22.113857+00
188	DIG01_C4sDR (98).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (98)_300a972d.jpeg	2025-11-15 18:31:22.229368+00
189	DIG01_C4sDR (58).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (58)_1ac06f84.jpeg	2025-11-15 18:31:22.342017+00
190	DIG01_C4sDR (8).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (8)_b3a9e151.jpeg	2025-11-15 18:31:22.463265+00
191	DIG01_C4sDR (202).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (202)_bb65ad4d.jpeg	2025-11-15 18:31:22.580732+00
192	DIG01_C4sDR (146).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (146)_c4962c4e.jpeg	2025-11-15 18:31:22.697479+00
193	DIG01_C4sDR (103).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (103)_ed0016c6.jpeg	2025-11-15 18:31:22.810857+00
194	DIG01_C4sDR (4).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (4)_e6fed8ea.jpeg	2025-11-15 18:31:22.926731+00
195	DIG01_C4sDR (11).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (11)_a437eab6.jpeg	2025-11-15 18:31:23.041373+00
196	DIG01_C4sDR (54).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (54)_9c9d7eda.jpeg	2025-11-15 18:31:23.16115+00
197	DIG01_C4sDR (132).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (132)_34771371.jpeg	2025-11-15 18:31:23.28427+00
198	DIG01_C4sDR (177).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (177)_80a7e949.jpeg	2025-11-15 18:31:23.400674+00
199	DIG01_C4sDR (69).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (69)_1d5e3559.jpeg	2025-11-15 18:31:23.520617+00
200	DIG01_C4sDR (94).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (94)_a9a57151.jpeg	2025-11-15 18:31:23.638619+00
201	DIG01_C4sDR (116).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (116)_2c04388c.jpeg	2025-11-15 18:31:23.75518+00
202	DIG01_C4sDR (153).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (153)_1b734f24.jpeg	2025-11-15 18:31:23.867859+00
203	DIG01_C4sDR (35).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (35)_541f3655.jpeg	2025-11-15 18:31:23.976701+00
204	DIG01_C4sDR (70).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (70)_b8e794c6.jpeg	2025-11-15 18:31:24.54015+00
205	DIG01_C4sDR (193).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (193)_5ad31816.jpeg	2025-11-15 18:31:24.647811+00
206	DIG01_C4sDR (37).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (37)_5d54eac8.jpeg	2025-11-15 18:31:24.75819+00
207	DIG01_C4sDR (72).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (72)_c743342f.jpeg	2025-11-15 18:31:24.870046+00
208	DIG01_C4sDR (191).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (191)_16469609.jpeg	2025-11-15 18:31:24.978422+00
209	DIG01_C4sDR (129).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (129)_671433bd.jpeg	2025-11-15 18:31:25.084065+00
210	DIG01_C4sDR (114).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (114)_5428b352.jpeg	2025-11-15 18:31:25.188017+00
211	DIG01_C4sDR (151).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (151)_f113fbe0.jpeg	2025-11-15 18:31:25.296192+00
212	DIG01_C4sDR (188).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (188)_8ca5ce65.jpeg	2025-11-15 18:31:25.40385+00
213	DIG01_C4sDR (130).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (130)_aec3b07d.jpeg	2025-11-15 18:31:25.511373+00
214	DIG01_C4sDR (175).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (175)_8e3dbc4c.jpeg	2025-11-15 18:31:25.616046+00
215	DIG01_C4sDR (96).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (96)_4986f6dc.jpeg	2025-11-15 18:31:25.728437+00
216	DIG01_C4sDR (13).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (13)_e4c3563c.jpeg	2025-11-15 18:31:25.843459+00
217	DIG01_C4sDR (56).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (56)_89186126.jpeg	2025-11-15 18:31:25.957646+00
218	DIG01_C4sDR (6).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (6)_6d224950.jpeg	2025-11-15 18:31:26.067798+00
219	DIG01_C4sDR (148).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (148)_d67d3b22.jpeg	2025-11-15 18:31:26.248105+00
220	DIG01_C4sDR (92).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (92)_f8666d74.jpeg	2025-11-15 18:31:26.415867+00
221	DIG01_C4sDR (134).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (134)_e4aebac7.jpeg	2025-11-15 18:31:26.532386+00
222	DIG01_C4sDR (171).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (171)_4dce7e53.jpeg	2025-11-15 18:31:26.638268+00
223	DIG01_C4sDR (208).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (208)_73d2eb20.jpeg	2025-11-15 18:31:26.751351+00
224	DIG01_C4sDR (109).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (109)_339f866b.jpeg	2025-11-15 18:31:26.862055+00
225	DIG01_C4sDR (17).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (17)_0a32b444.jpeg	2025-11-15 18:31:26.9696+00
226	DIG01_C4sDR (52).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (52)_40874717.jpeg	2025-11-15 18:31:27.080195+00
227	DIG01_C4sDR (2).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (2)_bd9ce8d1.jpeg	2025-11-15 18:31:27.188418+00
228	DIG01_C4sDR (168).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (168)_616ec27b.jpeg	2025-11-15 18:31:27.299158+00
229	DIG01_C4sDR (195).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (195)_42e5156d.jpeg	2025-11-15 18:31:27.411866+00
230	DIG01_C4sDR (33).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (33)_d3035058.jpeg	2025-11-15 18:31:27.51997+00
231	DIG01_C4sDR (76).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (76)_5f3761f8.jpeg	2025-11-15 18:31:27.63058+00
232	DIG01_C4sDR (211).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (211)_d1a42314.jpeg	2025-11-15 18:31:27.742214+00
233	DIG01_C4sDR (110).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (110)_17166902.jpeg	2025-11-15 18:31:27.853697+00
234	DIG01_C4sDR (155).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (155)_6e8f6f54.jpeg	2025-11-15 18:31:27.961675+00
235	DIG01_C4sDR (49).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (49)_2ea9bed1.jpeg	2025-11-15 18:31:28.070206+00
236	DIG01_C4sDR (112).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (112)_2c517f3d.jpeg	2025-11-15 18:31:28.177605+00
237	DIG01_C4sDR (157).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (157)_169584dc.jpeg	2025-11-15 18:31:28.289913+00
238	DIG01_C4sDR (213).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (213)_fd93057e.jpeg	2025-11-15 18:31:28.40106+00
239	DIG01_C4sDR (197).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (197)_cf3f890f.jpeg	2025-11-15 18:31:28.507308+00
240	DIG01_C4sDR (89).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (89)_ce420c10.jpeg	2025-11-15 18:31:28.625778+00
241	DIG01_C4sDR (31).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (31)_db8fe2cb.jpeg	2025-11-15 18:31:28.745214+00
242	DIG01_C4sDR (74).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (74)_2a06692e.jpeg	2025-11-15 18:31:28.860034+00
243	DIG01_C4sDR (15).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (15)_07364937.jpeg	2025-11-15 18:31:28.968064+00
244	DIG01_C4sDR (50).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (50)_77492232.jpeg	2025-11-15 18:31:29.074017+00
245	DIG01_C4sDR (90).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (90)_e54a90e5.jpeg	2025-11-15 18:31:29.187235+00
246	DIG01_C4sDR (28).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (28)_0eedb486.jpeg	2025-11-15 18:31:29.293126+00
247	DIG01_C4sDR (136).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (136)_4359800b.jpeg	2025-11-15 18:31:29.403488+00
248	DIG01_C4sDR (173).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (173)_7b01d750.jpeg	2025-11-15 18:31:29.510599+00
249	DIG01_C4sDR (150).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (150)_ac35f7fe.jpeg	2025-11-15 18:31:29.615626+00
250	DIG01_C4sDR (115).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (115)_d1f18275.jpeg	2025-11-15 18:31:29.723172+00
251	DIG01_C4sDR (214).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (214)_71b2e44d.jpeg	2025-11-15 18:31:29.831215+00
252	DIG01_C4sDR (190).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (190)_e9d4bb07.jpeg	2025-11-15 18:31:29.939187+00
253	DIG01_C4sDR (128).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (128)_644f6184.jpeg	2025-11-15 18:31:30.04888+00
254	DIG01_C4sDR (73).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (73)_5840bfe5.jpeg	2025-11-15 18:31:30.151632+00
255	DIG01_C4sDR (36).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (36)_62c228f2.jpeg	2025-11-15 18:31:30.254506+00
256	DIG01_C4sDR (149).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (149)_40fb19c6.jpeg	2025-11-15 18:31:30.359371+00
257	DIG01_C4sDR (57).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (57)_b4d0295b.jpeg	2025-11-15 18:31:30.467357+00
258	DIG01_C4sDR (12).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (12)_b8b3597c.jpeg	2025-11-15 18:31:30.572299+00
259	DIG01_C4sDR (7).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (7)_d5821f53.jpeg	2025-11-15 18:31:30.682378+00
260	DIG01_C4sDR (97).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (97)_0f0e0249.jpeg	2025-11-15 18:31:30.79388+00
261	DIG01_C4sDR (189).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (189)_4ccb3a27.jpeg	2025-11-15 18:31:30.908323+00
262	DIG01_C4sDR (174).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (174)_54df80f1.jpeg	2025-11-15 18:31:31.020642+00
263	DIG01_C4sDR (131).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (131)_7d09714e.jpeg	2025-11-15 18:31:31.130797+00
264	DIG01_C4sDR (68).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (68)_52fb44f4.jpeg	2025-11-15 18:31:31.236663+00
265	DIG01_C4sDR (95).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (95)_5bf8598b.jpeg	2025-11-15 18:31:31.341274+00
266	DIG01_C4sDR (176).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (176)_be2f1d9e.jpeg	2025-11-15 18:31:31.452432+00
267	DIG01_C4sDR (133).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (133)_97ee619f.jpeg	2025-11-15 18:31:31.559113+00
268	DIG01_C4sDR (5).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (5)_5cd3751c.jpeg	2025-11-15 18:31:31.782786+00
269	DIG01_C4sDR (55).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (55)_5b960f3f.jpeg	2025-11-15 18:31:31.922802+00
270	DIG01_C4sDR (10).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (10)_2bf61d4f.jpeg	2025-11-15 18:31:32.032297+00
271	DIG01_C4sDR (192).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (192)_de6629a3.jpeg	2025-11-15 18:31:32.145934+00
272	DIG01_C4sDR (71).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (71)_c480180d.jpeg	2025-11-15 18:31:32.266539+00
273	DIG01_C4sDR (34).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (34)_f3f5697c.jpeg	2025-11-15 18:31:32.393199+00
274	DIG01_C4sDR (152).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (152)_6900e47f.jpeg	2025-11-15 18:31:32.512217+00
275	DIG01_C4sDR (117).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (117)_7856d4c8.jpeg	2025-11-15 18:31:32.632086+00
276	DIG01_C4sDR (88).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (88)_10bea87e.jpeg	2025-11-15 18:31:32.756165+00
277	DIG01_C4sDR (75).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (75)_25a1a869.jpeg	2025-11-15 18:31:32.87228+00
278	DIG01_C4sDR (30).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (30)_a6ac81d8.jpeg	2025-11-15 18:31:32.982305+00
279	DIG01_C4sDR (196).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (196)_deaa7111.jpeg	2025-11-15 18:31:33.103976+00
280	DIG01_C4sDR (156).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (156)_4a98b5ea.jpeg	2025-11-15 18:31:33.216708+00
281	DIG01_C4sDR (113).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (113)_e3afe605.jpeg	2025-11-15 18:31:33.332768+00
282	DIG01_C4sDR (212).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (212)_47f9820d.jpeg	2025-11-15 18:31:33.452654+00
283	DIG01_C4sDR (48).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (48)_53068085.jpeg	2025-11-15 18:31:33.597698+00
284	DIG01_C4sDR (172).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (172)_4a4a540d.jpeg	2025-11-15 18:31:33.713255+00
285	DIG01_C4sDR (137).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (137)_b4d1ce8b.jpeg	2025-11-15 18:31:33.829077+00
286	DIG01_C4sDR (91).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (91)_4032325c.jpeg	2025-11-15 18:31:33.987298+00
287	DIG01_C4sDR (29).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (29)_c9f27f8f.jpeg	2025-11-15 18:31:34.106742+00
288	DIG01_C4sDR (1).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (1)_abb306cf.jpeg	2025-11-15 18:31:34.217363+00
289	DIG01_C4sDR (51).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (51)_52222b66.jpeg	2025-11-15 18:31:34.339864+00
290	DIG01_C4sDR (14).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (14)_6391b000.jpeg	2025-11-15 18:31:34.461864+00
291	DIG01_C4sDR (53).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (53)_589a0f52.jpeg	2025-11-15 18:31:34.577858+00
292	DIG01_C4sDR (16).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (16)_7140d7f3.jpeg	2025-11-15 18:31:34.697602+00
293	DIG01_C4sDR (3).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (3)_71f0e6b8.jpeg	2025-11-15 18:31:34.816545+00
294	DIG01_C4sDR (209).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (209)_3f863eb7.jpeg	2025-11-15 18:31:34.935251+00
295	DIG01_C4sDR (108).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (108)_8debd77c.jpeg	2025-11-15 18:31:35.091655+00
296	DIG01_C4sDR (170).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (170)_55f1b06b.jpeg	2025-11-15 18:31:35.209862+00
297	DIG01_C4sDR (135).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (135)_39f67d3e.jpeg	2025-11-15 18:31:35.329249+00
298	DIG01_C4sDR (93).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (93)_f2b5c288.jpeg	2025-11-15 18:31:35.44879+00
299	DIG01_C4sDR (210).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (210)_b2a5d1fe.jpeg	2025-11-15 18:31:35.566227+00
300	DIG01_C4sDR (154).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (154)_620de8f4.jpeg	2025-11-15 18:31:35.687469+00
301	DIG01_C4sDR (111).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (111)_4395420b.jpeg	2025-11-15 18:31:35.807842+00
302	DIG01_C4sDR (77).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (77)_f9ad46e0.jpeg	2025-11-15 18:31:35.928989+00
303	DIG01_C4sDR (32).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (32)_7723d4e2.jpeg	2025-11-15 18:31:36.043092+00
304	DIG01_C4sDR (169).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (169)_151d5df7.jpeg	2025-11-15 18:31:36.313779+00
305	DIG01_C4sDR (194).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C4sDR (194)_a815f08f.jpeg	2025-11-15 18:31:36.438689+00
306	DIG01_C3sDR (3).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (3)_6687b4aa.jpeg	2025-11-15 18:31:36.565041+00
307	DIG01_C3sDR (124).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (124)_e4e12e80.jpeg	2025-11-15 18:31:36.688747+00
308	DIG01_C3sDR (86).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (86)_a4495ca3.jpeg	2025-11-15 18:31:36.810376+00
309	DIG01_C3sDR (46).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (46)_877c4972.jpeg	2025-11-15 18:31:36.935286+00
310	DIG01_C3sDR (119).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (119)_8dd16b90.jpeg	2025-11-15 18:31:37.061812+00
311	DIG01_C3sDR (62).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (62)_e75e2f7b.jpeg	2025-11-15 18:31:37.182843+00
312	DIG01_C3sDR (27).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (27)_88f9cafe.jpeg	2025-11-15 18:31:37.308258+00
313	DIG01_C3sDR (145).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (145)_7b7cd047.jpeg	2025-11-15 18:31:37.42357+00
314	DIG01_C3sDR (100).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (100)_fad1fc65.jpeg	2025-11-15 18:31:37.543474+00
315	DIG01_C3sDR (102).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (102)_e9fe5855.jpeg	2025-11-15 18:31:37.663571+00
316	DIG01_C3sDR (18).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (18)_bb7ee748.jpeg	2025-11-15 18:31:37.780808+00
317	DIG01_C3sDR (60).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (60)_28b72ee4.jpeg	2025-11-15 18:31:37.92732+00
318	DIG01_C3sDR (25).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (25)_ec71d321.jpeg	2025-11-15 18:31:38.048642+00
319	DIG01_C3sDR (44).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (44)_6ea2d463.jpeg	2025-11-15 18:31:38.171384+00
320	DIG01_C3sDR (126).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (126)_5561a2ef.jpeg	2025-11-15 18:31:38.29374+00
321	DIG01_C3sDR (1).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (1)_95204095.jpeg	2025-11-15 18:31:38.413307+00
322	DIG01_C3sDR (84).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (84)_39d7b533.jpeg	2025-11-15 18:31:38.533877+00
323	DIG01_C3sDR (79).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (79)_6aac6c0b.jpeg	2025-11-15 18:31:38.65686+00
324	DIG01_C3sDR (40).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (40)_0f84b705.jpeg	2025-11-15 18:31:38.773992+00
325	DIG01_C3sDR (38).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (38)_68ab3d6c.jpeg	2025-11-15 18:31:38.90129+00
326	DIG01_C3sDR (80).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (80)_90782e9f.jpeg	2025-11-15 18:31:39.024231+00
327	DIG01_C3sDR (5).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (5)_6b1f24de.jpeg	2025-11-15 18:31:39.149347+00
328	DIG01_C3sDR (122).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (122)_e3f59ceb.jpeg	2025-11-15 18:31:39.283799+00
329	DIG01_C3sDR (59).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (59)_4da20c86.jpeg	2025-11-15 18:31:39.401523+00
330	DIG01_C3sDR (143).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (143)_99e50f40.jpeg	2025-11-15 18:31:39.511976+00
331	DIG01_C3sDR (106).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (106)_b7fce1af.jpeg	2025-11-15 18:31:39.635932+00
332	DIG01_C3sDR (64).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (64)_3fd3a143.jpeg	2025-11-15 18:31:39.747574+00
333	DIG01_C3sDR (21).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (21)_ce2e23e5.jpeg	2025-11-15 18:31:39.860721+00
334	DIG01_C3sDR (99).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (99)_2d3fef87.jpeg	2025-11-15 18:31:39.974841+00
335	DIG01_C3sDR (139).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (139)_f346f634.jpeg	2025-11-15 18:31:40.086608+00
336	DIG01_C3sDR (66).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (66)_5a393d38.jpeg	2025-11-15 18:31:40.201386+00
337	DIG01_C3sDR (23).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (23)_bf8d76b4.jpeg	2025-11-15 18:31:40.312168+00
338	DIG01_C3sDR (141).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (141)_e83239bb.jpeg	2025-11-15 18:31:40.426963+00
339	DIG01_C3sDR (104).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (104)_0bb947ac.jpeg	2025-11-15 18:31:40.543929+00
340	DIG01_C3sDR (82).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (82)_cb260433.jpeg	2025-11-15 18:31:40.662122+00
341	DIG01_C3sDR (120).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (120)_19da9589.jpeg	2025-11-15 18:31:40.783104+00
342	DIG01_C3sDR (7).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (7)_970513f7.jpeg	2025-11-15 18:31:40.89362+00
343	DIG01_C3sDR (42).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (42)_21e8cbeb.jpeg	2025-11-15 18:31:41.007802+00
344	DIG01_C3sDR (24).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (24)_d360e854.jpeg	2025-11-15 18:31:41.130748+00
345	DIG01_C3sDR (61).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (61)_63488bc5.jpeg	2025-11-15 18:31:41.248843+00
346	DIG01_C3sDR (19).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (19)_9a74c9ea.jpeg	2025-11-15 18:31:41.372355+00
347	DIG01_C3sDR (103).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (103)_db3d57bf.jpeg	2025-11-15 18:31:41.490225+00
348	DIG01_C3sDR (146).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (146)_d4cc5a9c.jpeg	2025-11-15 18:31:41.610295+00
349	DIG01_C3sDR (85).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (85)_b3c053a1.jpeg	2025-11-15 18:31:41.816175+00
350	DIG01_C3sDR (78).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (78)_9411f61c.jpeg	2025-11-15 18:31:41.936384+00
351	DIG01_C3sDR (127).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (127)_1f4cfaa2.jpeg	2025-11-15 18:31:42.07101+00
352	DIG01_C3sDR (45).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (45)_22e78d44.jpeg	2025-11-15 18:31:42.198798+00
353	DIG01_C3sDR (118).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (118)_afb62851.jpeg	2025-11-15 18:31:42.32487+00
354	DIG01_C3sDR (47).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (47)_ad8e33e0.jpeg	2025-11-15 18:31:42.470481+00
355	DIG01_C3sDR (87).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (87)_cf5900dc.jpeg	2025-11-15 18:31:42.586182+00
356	DIG01_C3sDR (2).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (2)_f63cb524.jpeg	2025-11-15 18:31:42.703004+00
357	DIG01_C3sDR (125).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (125)_52f80ca5.jpeg	2025-11-15 18:31:42.82751+00
358	DIG01_C3sDR (101).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (101)_bba6624a.jpeg	2025-11-15 18:31:42.990296+00
359	DIG01_C3sDR (144).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (144)_be250ad4.jpeg	2025-11-15 18:31:43.116116+00
360	DIG01_C3sDR (26).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (26)_f7862846.jpeg	2025-11-15 18:31:43.237239+00
361	DIG01_C3sDR (63).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (63)_8e0b188d.jpeg	2025-11-15 18:31:43.358567+00
362	DIG01_C3sDR (105).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (105)_12f3c76e.jpeg	2025-11-15 18:31:43.478467+00
363	DIG01_C3sDR (140).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (140)_073a1a67.jpeg	2025-11-15 18:31:43.601324+00
364	DIG01_C3sDR (22).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (22)_31e80e0f.jpeg	2025-11-15 18:31:43.720421+00
365	DIG01_C3sDR (67).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (67)_0a06bde7.jpeg	2025-11-15 18:31:43.838242+00
366	DIG01_C3sDR (138).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (138)_68112db9.jpeg	2025-11-15 18:31:43.957941+00
367	DIG01_C3sDR (43).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (43)_7dbc88e3.jpeg	2025-11-15 18:31:44.076377+00
368	DIG01_C3sDR (121).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (121)_7bca4b92.jpeg	2025-11-15 18:31:44.199939+00
369	DIG01_C3sDR (6).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (6)_819da6df.jpeg	2025-11-15 18:31:44.317872+00
370	DIG01_C3sDR (83).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (83)_c7de9ee8.jpeg	2025-11-15 18:31:44.434954+00
371	DIG01_C3sDR (4).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (4)_3a3b4936.jpeg	2025-11-15 18:31:44.576974+00
372	DIG01_C3sDR (123).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (123)_ed10d59e.jpeg	2025-11-15 18:31:44.725553+00
373	DIG01_C3sDR (39).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (39)_b768f2fe.jpeg	2025-11-15 18:31:44.848521+00
374	DIG01_C3sDR (81).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (81)_c8bf2f55.jpeg	2025-11-15 18:31:44.967986+00
375	DIG01_C3sDR (41).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (41)_36983d64.jpeg	2025-11-15 18:31:45.089821+00
376	DIG01_C3sDR (20).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (20)_e4003fcd.jpeg	2025-11-15 18:31:45.206416+00
377	DIG01_C3sDR (65).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (65)_216f1d4b.jpeg	2025-11-15 18:31:45.318916+00
378	DIG01_C3sDR (98).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (98)_b48e09de.jpeg	2025-11-15 18:31:45.440619+00
379	DIG01_C3sDR (107).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (107)_9de129e4.jpeg	2025-11-15 18:31:45.558445+00
380	DIG01_C3sDR (142).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (142)_5b1d7def.jpeg	2025-11-15 18:31:45.681324+00
381	DIG01_C3sDR (58).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (58)_f91f7493.jpeg	2025-11-15 18:31:45.80767+00
382	DIG01_C3sDR (54).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (54)_04e5790c.jpeg	2025-11-15 18:31:45.930447+00
383	DIG01_C3sDR (11).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (11)_b1c18fc1.jpeg	2025-11-15 18:31:46.049801+00
384	DIG01_C3sDR (69).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (69)_e391727b.jpeg	2025-11-15 18:31:46.169368+00
385	DIG01_C3sDR (94).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (94)_51507281.jpeg	2025-11-15 18:31:46.294275+00
386	DIG01_C3sDR (136).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (136)_c7955d7c.jpeg	2025-11-15 18:31:46.42064+00
387	DIG01_C3sDR (112).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (112)_4e0af683.jpeg	2025-11-15 18:31:46.532913+00
388	DIG01_C3sDR (8).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (8)_6f88597a.jpeg	2025-11-15 18:31:46.646676+00
389	DIG01_C3sDR (70).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (70)_340988f0.jpeg	2025-11-15 18:31:46.764012+00
390	DIG01_C3sDR (35).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (35)_9fe7c529.jpeg	2025-11-15 18:31:46.877155+00
391	DIG01_C3sDR (72).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (72)_b2596c4b.jpeg	2025-11-15 18:31:46.987963+00
392	DIG01_C3sDR (37).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (37)_8af3d4f2.jpeg	2025-11-15 18:31:47.109818+00
393	DIG01_C3sDR (110).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (110)_0e50ac11.jpeg	2025-11-15 18:31:47.220776+00
394	DIG01_C3sDR (96).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (96)_e3a32bdf.jpeg	2025-11-15 18:31:47.342482+00
395	DIG01_C3sDR (134).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (134)_c48a048a.jpeg	2025-11-15 18:31:47.465743+00
396	DIG01_C3sDR (109).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (109)_ea842238.jpeg	2025-11-15 18:31:47.580757+00
397	DIG01_C3sDR (56).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (56)_67811f66.jpeg	2025-11-15 18:31:47.702682+00
398	DIG01_C3sDR (13).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (13)_2f216a3e.jpeg	2025-11-15 18:31:47.827982+00
399	DIG01_C3sDR (130).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (130)_9c1b8225.jpeg	2025-11-15 18:31:47.946435+00
400	DIG01_C3sDR (92).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (92)_51735d9a.jpeg	2025-11-15 18:31:48.072405+00
401	DIG01_C3sDR (52).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (52)_1e513e73.jpeg	2025-11-15 18:31:48.192004+00
402	DIG01_C3sDR (17).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (17)_52ac27bd.jpeg	2025-11-15 18:31:48.315406+00
403	DIG01_C3sDR (76).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (76)_8f362304.jpeg	2025-11-15 18:31:48.45832+00
404	DIG01_C3sDR (33).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (33)_76a48c40.jpeg	2025-11-15 18:31:49.067504+00
405	DIG01_C3sDR (129).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (129)_978d0575.jpeg	2025-11-15 18:31:49.185967+00
406	DIG01_C3sDR (114).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (114)_e49ce1ea.jpeg	2025-11-15 18:31:49.26254+00
407	DIG01_C3sDR (116).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (116)_253e0e9d.jpeg	2025-11-15 18:31:49.384307+00
408	DIG01_C3sDR (49).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (49)_f3d5e1b6.jpeg	2025-11-15 18:31:49.498999+00
409	DIG01_C3sDR (89).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (89)_0ef39ca1.jpeg	2025-11-15 18:31:49.622931+00
410	DIG01_C3sDR (74).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (74)_753e2ae1.jpeg	2025-11-15 18:31:49.740785+00
411	DIG01_C3sDR (31).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (31)_f200f65e.jpeg	2025-11-15 18:31:49.867499+00
412	DIG01_C3sDR (50).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (50)_5da963f5.jpeg	2025-11-15 18:31:49.988793+00
413	DIG01_C3sDR (15).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (15)_de694de2.jpeg	2025-11-15 18:31:50.110958+00
414	DIG01_C3sDR (132).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (132)_9384e0ae.jpeg	2025-11-15 18:31:50.234687+00
415	DIG01_C3sDR (90).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (90)_80cb7d74.jpeg	2025-11-15 18:31:50.351574+00
416	DIG01_C3sDR (28).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (28)_1fcc9de2.jpeg	2025-11-15 18:31:50.472283+00
417	DIG01_C3sDR (111).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (111)_18ee31a5.jpeg	2025-11-15 18:31:50.591769+00
418	DIG01_C3sDR (36).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (36)_2c9460a1.jpeg	2025-11-15 18:31:50.722402+00
419	DIG01_C3sDR (73).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (73)_9a0e05f2.jpeg	2025-11-15 18:31:50.840793+00
420	DIG01_C3sDR (12).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (12)_40fed267.jpeg	2025-11-15 18:31:50.965956+00
421	DIG01_C3sDR (57).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (57)_b067564f.jpeg	2025-11-15 18:31:51.093389+00
422	DIG01_C3sDR (108).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (108)_4ba8d3f3.jpeg	2025-11-15 18:31:51.216235+00
423	DIG01_C3sDR (135).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (135)_2ce67c2a.jpeg	2025-11-15 18:31:51.328782+00
424	DIG01_C3sDR (97).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (97)_f3b516ce.jpeg	2025-11-15 18:31:51.453944+00
425	DIG01_C3sDR (137).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (137)_1f7e63e8.jpeg	2025-11-15 18:31:51.57507+00
426	DIG01_C3sDR (68).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (68)_7b8c1505.jpeg	2025-11-15 18:31:51.796233+00
427	DIG01_C3sDR (95).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (95)_3196b21b.jpeg	2025-11-15 18:31:51.941107+00
428	DIG01_C3sDR (10).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (10)_eb272d61.jpeg	2025-11-15 18:31:52.076429+00
429	DIG01_C3sDR (55).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (55)_adb9b9a8.jpeg	2025-11-15 18:31:52.193364+00
430	DIG01_C3sDR (34).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (34)_b832a7c5.jpeg	2025-11-15 18:31:52.319724+00
431	DIG01_C3sDR (71).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (71)_0b9423f9.jpeg	2025-11-15 18:31:52.440792+00
432	DIG01_C3sDR (9).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (9)_881edca9.jpeg	2025-11-15 18:31:52.549485+00
433	DIG01_C3sDR (113).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (113)_81704500.jpeg	2025-11-15 18:31:52.672249+00
434	DIG01_C3sDR (88).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (88)_2b8bd981.jpeg	2025-11-15 18:31:52.785938+00
435	DIG01_C3sDR (30).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (30)_ce4a3eca.jpeg	2025-11-15 18:31:52.906353+00
436	DIG01_C3sDR (75).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (75)_0e0ccdd8.jpeg	2025-11-15 18:31:53.025255+00
437	DIG01_C3sDR (48).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (48)_93c9dc67.jpeg	2025-11-15 18:31:53.14519+00
438	DIG01_C3sDR (117).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (117)_dde00a59.jpeg	2025-11-15 18:31:53.267027+00
439	DIG01_C3sDR (91).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (91)_6785323e.jpeg	2025-11-15 18:31:53.384061+00
440	DIG01_C3sDR (29).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (29)_79489e10.jpeg	2025-11-15 18:31:53.504617+00
441	DIG01_C3sDR (133).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (133)_73300d46.jpeg	2025-11-15 18:31:53.6261+00
442	DIG01_C3sDR (14).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (14)_eddd0a78.jpeg	2025-11-15 18:31:53.744337+00
443	DIG01_C3sDR (51).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (51)_02168590.jpeg	2025-11-15 18:31:53.866214+00
444	DIG01_C3sDR (16).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (16)_429eb9e4.jpeg	2025-11-15 18:31:53.986387+00
445	DIG01_C3sDR (53).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (53)_61f47f37.jpeg	2025-11-15 18:31:54.103536+00
446	DIG01_C3sDR (93).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (93)_5a8c86b3.jpeg	2025-11-15 18:31:54.226436+00
447	DIG01_C3sDR (131).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (131)_e4f4c0c8.jpeg	2025-11-15 18:31:54.342016+00
448	DIG01_C3sDR (115).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (115)_4ed602c0.jpeg	2025-11-15 18:31:54.466093+00
449	DIG01_C3sDR (128).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (128)_ee97064a.jpeg	2025-11-15 18:31:54.581383+00
450	DIG01_C3sDR (32).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (32)_dc8ced04.jpeg	2025-11-15 18:31:54.698634+00
451	DIG01_C3sDR (77).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C3sDR (77)_28ed26e3.jpeg	2025-11-15 18:31:54.815984+00
452	DIG01_C2sDR (21).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (21)_ab19437d.jpeg	2025-11-15 18:31:54.932413+00
453	DIG01_C2sDR (40).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (40)_5ba9f892.jpeg	2025-11-15 18:31:55.051237+00
454	DIG01_C2sDR (38).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (38)_793d1e3e.jpeg	2025-11-15 18:31:55.172819+00
455	DIG01_C2sDR (42).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (42)_e6731762.jpeg	2025-11-15 18:31:55.295152+00
456	DIG01_C2sDR (23).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (23)_688f1aaa.jpeg	2025-11-15 18:31:55.40927+00
457	DIG01_C2sDR (27).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (27)_852e8c03.jpeg	2025-11-15 18:31:55.531764+00
458	DIG01_C2sDR (46).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (46)_fdd75ac4.jpeg	2025-11-15 18:31:55.650105+00
459	DIG01_C2sDR (44).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (44)_7072726c.jpeg	2025-11-15 18:31:55.777759+00
460	DIG01_C2sDR (8).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (8)_7ab4503a.jpeg	2025-11-15 18:31:55.895065+00
461	DIG01_C2sDR (18).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (18)_030a2657.jpeg	2025-11-15 18:31:56.011419+00
462	DIG01_C2sDR (25).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (25)_a993b47e.jpeg	2025-11-15 18:31:56.133224+00
463	DIG01_C2sDR (43).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (43)_af997df6.jpeg	2025-11-15 18:31:56.257564+00
464	DIG01_C2sDR (22).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (22)_47e69db6.jpeg	2025-11-15 18:31:56.374784+00
465	DIG01_C2sDR (20).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (20)_8be29a98.jpeg	2025-11-15 18:31:56.4946+00
466	DIG01_C2sDR (39).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (39)_de09ab5d.jpeg	2025-11-15 18:31:56.61271+00
467	DIG01_C2sDR (41).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (41)_b0cad6ab.jpeg	2025-11-15 18:31:56.731922+00
468	DIG01_C2sDR (9).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (9)_eb3e5b11.jpeg	2025-11-15 18:31:56.851796+00
469	DIG01_C2sDR (45).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (45)_ed77adeb.jpeg	2025-11-15 18:31:56.979832+00
470	DIG01_C2sDR (24).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (24)_2084962b.jpeg	2025-11-15 18:31:57.101212+00
471	DIG01_C2sDR (19).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (19)_9eb8bc2c.jpeg	2025-11-15 18:31:57.219103+00
472	DIG01_C2sDR (26).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (26)_d99234aa.jpeg	2025-11-15 18:31:57.339998+00
473	DIG01_C2sDR (47).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (47)_6818e467.jpeg	2025-11-15 18:31:57.457138+00
474	DIG01_C2sDR (7).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (7)_05f6e009.jpeg	2025-11-15 18:31:57.60669+00
475	DIG01_C2sDR (33).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (33)_e0d15ad4.jpeg	2025-11-15 18:31:57.734413+00
476	DIG01_C2sDR (17).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (17)_2f6ca9bc.jpeg	2025-11-15 18:31:57.853481+00
477	DIG01_C2sDR (15).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (15)_17072d3f.jpeg	2025-11-15 18:31:57.968532+00
478	DIG01_C2sDR (50).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (50)_a27d7570.jpeg	2025-11-15 18:31:58.085214+00
479	DIG01_C2sDR (28).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (28)_a57ba162.jpeg	2025-11-15 18:31:58.201536+00
480	DIG01_C2sDR (49).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (49)_ef875524.jpeg	2025-11-15 18:31:58.321279+00
481	DIG01_C2sDR (5).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (5)_df3318ed.jpeg	2025-11-15 18:31:58.43616+00
482	DIG01_C2sDR (31).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (31)_9754ad06.jpeg	2025-11-15 18:31:58.554599+00
483	DIG01_C2sDR (35).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (35)_1b4fb776.jpeg	2025-11-15 18:31:58.679248+00
484	DIG01_C2sDR (1).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (1)_007e4c60.jpeg	2025-11-15 18:31:58.791438+00
485	DIG01_C2sDR (11).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (11)_d00f537f.jpeg	2025-11-15 18:31:58.906165+00
486	DIG01_C2sDR (13).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (13)_6805b921.jpeg	2025-11-15 18:31:59.022636+00
487	DIG01_C2sDR (37).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (37)_6b0707a5.jpeg	2025-11-15 18:31:59.135985+00
488	DIG01_C2sDR (3).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (3)_a66d375d.jpeg	2025-11-15 18:31:59.24994+00
489	DIG01_C2sDR (29).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (29)_64b8e72f.jpeg	2025-11-15 18:31:59.365619+00
490	DIG01_C2sDR (51).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (51)_9a855385.jpeg	2025-11-15 18:31:59.489226+00
491	DIG01_C2sDR (14).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (14)_02a61710.jpeg	2025-11-15 18:31:59.603653+00
492	DIG01_C2sDR (30).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (30)_263b5d4b.jpeg	2025-11-15 18:31:59.750253+00
493	DIG01_C2sDR (4).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (4)_55ceaf66.jpeg	2025-11-15 18:31:59.871219+00
494	DIG01_C2sDR (48).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (48)_bb5ccf20.jpeg	2025-11-15 18:31:59.992201+00
495	DIG01_C2sDR (32).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (32)_5be1b1c3.jpeg	2025-11-15 18:32:00.115894+00
496	DIG01_C2sDR (6).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (6)_8e9f24b0.jpeg	2025-11-15 18:32:00.235844+00
497	DIG01_C2sDR (16).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (16)_df6f4c7a.jpeg	2025-11-15 18:32:00.35435+00
498	DIG01_C2sDR (12).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (12)_4846de84.jpeg	2025-11-15 18:32:00.478462+00
499	DIG01_C2sDR (2).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (2)_b27895d1.jpeg	2025-11-15 18:32:00.601298+00
500	DIG01_C2sDR (36).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (36)_ee6605f8.jpeg	2025-11-15 18:32:00.721016+00
501	DIG01_C2sDR (34).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (34)_421a0802.jpeg	2025-11-15 18:32:00.839945+00
502	DIG01_C2sDR (10).jpeg	https://captcha-dental-images.s3.us-east-2.amazonaws.com/dental-xrays/DIG01_C2sDR (10)_14767428.jpeg	2025-11-15 18:32:00.953555+00
\.


--
-- Data for Name: password_reset_tokens; Type: TABLE DATA; Schema: public; Owner: captcha_user
--

COPY public.password_reset_tokens (id, user_id, token_hash, expires) FROM stdin;
\.


--
-- Data for Name: questions; Type: TABLE DATA; Schema: public; Owner: captcha_user
--

COPY public.questions (id, question_text, question_type, active, created_at) FROM stdin;
1	Which images look most realistic?	Synthetic	t	2025-11-15 18:44:31.972527+00
2	Which images have visible dental restorations?	Synthetic	t	2025-11-15 18:44:31.972527+00
3	Which images show restorations in the mandibular (lower) arch?	Synthetic	t	2025-11-15 18:44:31.972527+00
4	Which images show restorations in the maxillary (upper) arch?	Synthetic	t	2025-11-15 18:44:31.972527+00
5	Which images have the clearest image quality?	Synthetic	t	2025-11-15 18:44:31.972527+00
6	Which images show complete dentition?	Synthetic	t	2025-11-15 18:44:31.972527+00
7	Which images show missing teeth?	Synthetic	t	2025-11-15 18:44:31.972527+00
8	Which images show primarily posterior teeth?	Synthetic	t	2025-11-15 18:44:31.972527+00
9	Which images have the most blurry or unclear quality?	Synthetic	t	2025-11-15 18:44:31.972527+00
10	Which images show signs of dental decay (caries)?	Synthetic	t	2025-11-15 18:44:31.972527+00
11	Which images show good bone levels?	Synthetic	t	2025-11-15 18:44:31.972527+00
12	Which images show bone loss?	Synthetic	t	2025-11-15 18:44:31.972527+00
13	Which images have high contrast?	Synthetic	t	2025-11-15 18:44:31.972527+00
14	Which images have low contrast?	Synthetic	t	2025-11-15 18:44:31.972527+00
15	Which images show overlapping teeth?	Synthetic	t	2025-11-15 18:44:31.972527+00
\.


--
-- Data for Name: session_images; Type: TABLE DATA; Schema: public; Owner: captcha_user
--

COPY public.session_images (id, session_id, image_id, image_order, created_at) FROM stdin;
1	1	405	1	2025-11-15 18:34:01.393507+00
2	1	324	2	2025-11-15 18:34:01.393507+00
3	1	302	3	2025-11-15 18:34:01.393507+00
4	1	429	4	2025-11-15 18:34:01.393507+00
\.


--
-- Data for Name: session_questions; Type: TABLE DATA; Schema: public; Owner: captcha_user
--

COPY public.session_questions (id, session_id, question_id, question_order, created_at) FROM stdin;
\.


--
-- Data for Name: sessions; Type: TABLE DATA; Schema: public; Owner: captcha_user
--

COPY public.sessions (id, user_id, is_completed, started_at, completed_at) FROM stdin;
1	2	f	2025-11-15 18:34:01.393507+00	\N
\.


--
-- Data for Name: user_stats; Type: TABLE DATA; Schema: public; Owner: captcha_user
--

COPY public.user_stats (id, user_id, total_points, total_annotations, accuracy_rate, daily_streak, last_active) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: captcha_user
--

COPY public.users (id, email, username, hashed_password, first_name, last_name, is_active, is_admin, is_verified, created_at, updated_at) FROM stdin;
1	AlansEmail@gmail.com	AlansUsername	$2b$12$Ur//jZSjURxcvfC6ijoUSeTfc5bKIuLkmIzd/qEVggcAnuLoHI5X2	Alan	Alberto	t	t	t	2025-11-09 21:34:46.284184+00	\N
2	AlansNewEmail@gmail.com	AlansNewUsername	$2b$12$dH8hWYWt6ETX8i3XnY1ROOtzpiDvwbqCzpb7DvddZYPiPpKIApnS6	Alan	Alberto	t	t	t	2025-11-11 04:03:30.118889+00	2025-11-11 04:06:25.249492+00
3	admin@captcha.local	admin	$2b$12$sm6MouEwC4NUvVlr.wqnzenodHQjNOUwaWqmxO9eEQwHs3cPeXJJ2	Admin	User	t	t	t	2025-11-13 17:36:33.791511+00	\N
4	test@captcha.local	testuser	$2b$12$lAtL7NBNkgnDIPy8uAGm.OoXMDinYcxpXmWlNVa0vzK23AqdW/kfK	Test	User	t	f	t	2025-11-13 17:36:34.300164+00	\N
5	mail@gmail.com	User	$2b$12$siWddc..FEYBIsgm/WUNyOc9RuD7wOAhvZl1Bv/V.Qb5OleQWrD8S	First	Last	t	f	t	2025-11-13 20:32:31.297812+00	2025-11-13 20:33:16.916469+00
\.


--
-- Name: annotation_images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: captcha_user
--

SELECT pg_catalog.setval('public.annotation_images_id_seq', 1, false);


--
-- Name: annotations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: captcha_user
--

SELECT pg_catalog.setval('public.annotations_id_seq', 1, false);


--
-- Name: email_confirmation_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: captcha_user
--

SELECT pg_catalog.setval('public.email_confirmation_tokens_id_seq', 1, false);


--
-- Name: images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: captcha_user
--

SELECT pg_catalog.setval('public.images_id_seq', 502, true);


--
-- Name: password_reset_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: captcha_user
--

SELECT pg_catalog.setval('public.password_reset_tokens_id_seq', 1, false);


--
-- Name: questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: captcha_user
--

SELECT pg_catalog.setval('public.questions_id_seq', 15, true);


--
-- Name: session_images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: captcha_user
--

SELECT pg_catalog.setval('public.session_images_id_seq', 4, true);


--
-- Name: session_questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: captcha_user
--

SELECT pg_catalog.setval('public.session_questions_id_seq', 1, true);


--
-- Name: sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: captcha_user
--

SELECT pg_catalog.setval('public.sessions_id_seq', 1, true);


--
-- Name: user_stats_id_seq; Type: SEQUENCE SET; Schema: public; Owner: captcha_user
--

SELECT pg_catalog.setval('public.user_stats_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: captcha_user
--

SELECT pg_catalog.setval('public.users_id_seq', 5, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: annotation_images annotation_images_pkey; Type: CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.annotation_images
    ADD CONSTRAINT annotation_images_pkey PRIMARY KEY (id);


--
-- Name: annotations annotations_pkey; Type: CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.annotations
    ADD CONSTRAINT annotations_pkey PRIMARY KEY (id);


--
-- Name: email_confirmation_tokens email_confirmation_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.email_confirmation_tokens
    ADD CONSTRAINT email_confirmation_tokens_pkey PRIMARY KEY (id);


--
-- Name: images images_filename_key; Type: CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_filename_key UNIQUE (filename);


--
-- Name: images images_pkey; Type: CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (id);


--
-- Name: password_reset_tokens password_reset_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_pkey PRIMARY KEY (id);


--
-- Name: questions questions_pkey; Type: CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_pkey PRIMARY KEY (id);


--
-- Name: session_images session_images_pkey; Type: CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.session_images
    ADD CONSTRAINT session_images_pkey PRIMARY KEY (id);


--
-- Name: session_questions session_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.session_questions
    ADD CONSTRAINT session_questions_pkey PRIMARY KEY (id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);


--
-- Name: user_stats user_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.user_stats
    ADD CONSTRAINT user_stats_pkey PRIMARY KEY (id);


--
-- Name: user_stats user_stats_user_id_key; Type: CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.user_stats
    ADD CONSTRAINT user_stats_user_id_key UNIQUE (user_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_annotation_images_id; Type: INDEX; Schema: public; Owner: captcha_user
--

CREATE INDEX ix_annotation_images_id ON public.annotation_images USING btree (id);


--
-- Name: ix_annotations_id; Type: INDEX; Schema: public; Owner: captcha_user
--

CREATE INDEX ix_annotations_id ON public.annotations USING btree (id);


--
-- Name: ix_email_confirmation_tokens_id; Type: INDEX; Schema: public; Owner: captcha_user
--

CREATE INDEX ix_email_confirmation_tokens_id ON public.email_confirmation_tokens USING btree (id);


--
-- Name: ix_email_confirmation_tokens_token_hash; Type: INDEX; Schema: public; Owner: captcha_user
--

CREATE UNIQUE INDEX ix_email_confirmation_tokens_token_hash ON public.email_confirmation_tokens USING btree (token_hash);


--
-- Name: ix_images_id; Type: INDEX; Schema: public; Owner: captcha_user
--

CREATE INDEX ix_images_id ON public.images USING btree (id);


--
-- Name: ix_password_reset_tokens_id; Type: INDEX; Schema: public; Owner: captcha_user
--

CREATE INDEX ix_password_reset_tokens_id ON public.password_reset_tokens USING btree (id);


--
-- Name: ix_password_reset_tokens_token_hash; Type: INDEX; Schema: public; Owner: captcha_user
--

CREATE UNIQUE INDEX ix_password_reset_tokens_token_hash ON public.password_reset_tokens USING btree (token_hash);


--
-- Name: ix_questions_id; Type: INDEX; Schema: public; Owner: captcha_user
--

CREATE INDEX ix_questions_id ON public.questions USING btree (id);


--
-- Name: ix_session_images_id; Type: INDEX; Schema: public; Owner: captcha_user
--

CREATE INDEX ix_session_images_id ON public.session_images USING btree (id);


--
-- Name: ix_session_questions_id; Type: INDEX; Schema: public; Owner: captcha_user
--

CREATE INDEX ix_session_questions_id ON public.session_questions USING btree (id);


--
-- Name: ix_sessions_id; Type: INDEX; Schema: public; Owner: captcha_user
--

CREATE INDEX ix_sessions_id ON public.sessions USING btree (id);


--
-- Name: ix_user_stats_id; Type: INDEX; Schema: public; Owner: captcha_user
--

CREATE INDEX ix_user_stats_id ON public.user_stats USING btree (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: captcha_user
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: captcha_user
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: captcha_user
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: annotation_images annotation_images_annotation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.annotation_images
    ADD CONSTRAINT annotation_images_annotation_id_fkey FOREIGN KEY (annotation_id) REFERENCES public.annotations(id) ON DELETE CASCADE;


--
-- Name: annotation_images annotation_images_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.annotation_images
    ADD CONSTRAINT annotation_images_image_id_fkey FOREIGN KEY (image_id) REFERENCES public.images(id) ON DELETE CASCADE;


--
-- Name: annotations annotations_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.annotations
    ADD CONSTRAINT annotations_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(id) ON DELETE CASCADE;


--
-- Name: annotations annotations_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.annotations
    ADD CONSTRAINT annotations_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(id) ON DELETE CASCADE;


--
-- Name: email_confirmation_tokens email_confirmation_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.email_confirmation_tokens
    ADD CONSTRAINT email_confirmation_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: password_reset_tokens password_reset_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: session_images session_images_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.session_images
    ADD CONSTRAINT session_images_image_id_fkey FOREIGN KEY (image_id) REFERENCES public.images(id) ON DELETE CASCADE;


--
-- Name: session_images session_images_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.session_images
    ADD CONSTRAINT session_images_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(id) ON DELETE CASCADE;


--
-- Name: session_questions session_questions_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.session_questions
    ADD CONSTRAINT session_questions_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(id) ON DELETE CASCADE;


--
-- Name: session_questions session_questions_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.session_questions
    ADD CONSTRAINT session_questions_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(id) ON DELETE CASCADE;


--
-- Name: sessions sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_stats user_stats_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: captcha_user
--

ALTER TABLE ONLY public.user_stats
    ADD CONSTRAINT user_stats_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict H4DaLfEcPuNlNI6YI5bJQOIPNx6b75n9zxTw6065t7t8pWdeapPpSep9FagKHiG

