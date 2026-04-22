--
-- PostgreSQL database dump
--

\restrict eXNtF5aeN63MktxlNJ51vakJ2CSsurZJVAJKpM5ERoDcZ9hOF2hMPQVcyhdmoFb

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: product_image; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product_image (
    image_id integer NOT NULL,
    product_id integer NOT NULL,
    image_url character varying(500) NOT NULL,
    alt_text character varying(255),
    is_primary boolean DEFAULT false NOT NULL,
    display_order integer DEFAULT 0 NOT NULL,
    uploaded_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.product_image OWNER TO postgres;

--
-- Name: product_image_image_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.product_image_image_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_image_image_id_seq OWNER TO postgres;

--
-- Name: product_image_image_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.product_image_image_id_seq OWNED BY public.product_image.image_id;


--
-- Name: product_image image_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_image ALTER COLUMN image_id SET DEFAULT nextval('public.product_image_image_id_seq'::regclass);


--
-- Data for Name: product_image; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.product_image (image_id, product_id, image_url, alt_text, is_primary, display_order, uploaded_at) FROM stdin;
1	1	/media/products/prod_1_1_laptop.jpg	Dell Inspiron 15 Laptop - Front View	t	1	2026-03-18 02:24:16.959124
2	2	/media/products/prod_2_1_phone.jpg	iPhone 12 Pro Max - Front View	t	1	2026-03-18 02:24:16.959124
3	3	/media/products/prod_3_1_headphone.jpg	Sony WH-1000XM4 Headphones	t	1	2026-03-18 02:24:16.959124
4	4	/media/products/prod_4_1_coat.jpg	Winter Coat - Front View	t	1	2026-03-18 02:24:16.959124
5	5	/media/products/prod_5_1_crimeandpunishmentbook.jpg	Crime and Punishment Book Cover	t	1	2026-03-18 02:24:16.959124
\.


--
-- Name: product_image_image_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.product_image_image_id_seq', 33, true);


--
-- Name: product_image product_image_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_image
    ADD CONSTRAINT product_image_pkey PRIMARY KEY (image_id);


--
-- Name: idx_product_image_product; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_product_image_product ON public.product_image USING btree (product_id);


--
-- Name: product_image product_image_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_image
    ADD CONSTRAINT product_image_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.product(product_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict eXNtF5aeN63MktxlNJ51vakJ2CSsurZJVAJKpM5ERoDcZ9hOF2hMPQVcyhdmoFb

