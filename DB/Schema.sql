--
-- PostgreSQL database dump
--

-- Dumped from database version 16.0
-- Dumped by pg_dump version 16.0

-- Started on 2023-10-05 12:51:48

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
-- TOC entry 232 (class 1259 OID 24876)
-- Name: Aliquote; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Aliquote" (
    "Aliquote_Id" text NOT NULL,
    "Aliquote_UUId" text NOT NULL,
    "Analyte_Id" text NOT NULL,
    "Analyte_UUId" text NOT NULL,
    "Type" integer,
    "Concentration" numeric
);


ALTER TABLE public."Aliquote" OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 24818)
-- Name: Aliquote_Type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Aliquote_Type" (
    "Type_Id" integer NOT NULL,
    "Type" text
);


ALTER TABLE public."Aliquote_Type" OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 24817)
-- Name: Aliquote_Type_Type_Id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public."Aliquote_Type" ALTER COLUMN "Type_Id" ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public."Aliquote_Type_Type_Id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 231 (class 1259 OID 24854)
-- Name: Analyte; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Analyte" (
    "Analyte_Id" text NOT NULL,
    "Analyte_UUId" text NOT NULL,
    "Portion_Id" text NOT NULL,
    "Portion_UUId" text NOT NULL,
    "Type" integer,
    "Concentration" numeric
);


ALTER TABLE public."Analyte" OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 24810)
-- Name: Analyte_Type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Analyte_Type" (
    "Type_Id" integer NOT NULL,
    "Type" text
);


ALTER TABLE public."Analyte_Type" OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 24809)
-- Name: Analyte_Type_Type_Id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public."Analyte_Type" ALTER COLUMN "Type_Id" ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public."Analyte_Type_Type_Id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 222 (class 1259 OID 24759)
-- Name: Biospecimen; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Biospecimen" (
    "Id" text NOT NULL,
    "UUId" text NOT NULL,
    "Case" text NOT NULL
);


ALTER TABLE public."Biospecimen" OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 24654)
-- Name: Case; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Case" (
    "Case_UUId" text NOT NULL,
    "Case_Id" text NOT NULL,
    "Created_DateTime" date,
    "Updated_DateTime" date,
    "Project" text NOT NULL,
    "Site" integer,
    "Disease" integer,
    CONSTRAINT "CK_Data" CHECK (("Updated_DateTime" >= "Created_DateTime"))
);


ALTER TABLE public."Case" OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 24630)
-- Name: Demographic; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Demographic" (
    "Case" text NOT NULL,
    "Ethnicity" text,
    "Race" text,
    "Gender" text,
    "Vital_Status" text,
    CONSTRAINT "CK_Gender" CHECK (("Gender" = ANY (ARRAY['Male'::text, 'Female'::text, 'Unknown'::text, 'Not reported'::text]))),
    CONSTRAINT "CK_Vital_Status" CHECK (("Vital_Status" = ANY (ARRAY['Alive'::text, 'Dead'::text])))
);


ALTER TABLE public."Demographic" OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 24591)
-- Name: Disease; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Disease" (
    "Disease_Id" integer NOT NULL,
    "Type" text
);


ALTER TABLE public."Disease" OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 24807)
-- Name: Disease_Disease_Id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public."Disease" ALTER COLUMN "Disease_Id" ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public."Disease_Disease_Id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 233 (class 1259 OID 32774)
-- Name: File; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."File" (
    "File_Id" text NOT NULL,
    "Filename" text,
    "Data_Category" text,
    "File_Size" numeric,
    "Created_DateTime" date,
    "Updated_DateTime" date,
    "Project" text NOT NULL,
    CONSTRAINT "CK_Data" CHECK (("Updated_DateTime" >= "Created_DateTime"))
);


ALTER TABLE public."File" OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 32787)
-- Name: File_Entity; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."File_Entity" (
    "File" text NOT NULL,
    "Biospecimen_Id" text NOT NULL,
    "Biospecimen_UUId" text NOT NULL
);


ALTER TABLE public."File_Entity" OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 32804)
-- Name: Gene; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Gene" (
    "Gene_Id" text NOT NULL,
    "Name" text,
    "Type" integer
);


ALTER TABLE public."Gene" OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 32830)
-- Name: Gene_Expression_File; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Gene_Expression_File" (
    "File" text NOT NULL,
    "Gene" text NOT NULL,
    "TPM" numeric,
    "FPKM" numeric,
    "FPKM_UQ" numeric
);


ALTER TABLE public."Gene_Expression_File" OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 32811)
-- Name: Gene_Type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Gene_Type" (
    "Type_Id" integer NOT NULL,
    "Type" text
);


ALTER TABLE public."Gene_Type" OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 32864)
-- Name: Gene_Type_Type_Id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public."Gene_Type" ALTER COLUMN "Type_Id" ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public."Gene_Type_Type_Id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 230 (class 1259 OID 24837)
-- Name: Portion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Portion" (
    "Portion_Id" text NOT NULL,
    "Portion_UUId" text NOT NULL,
    "Sample_Id" text NOT NULL,
    "Sample_UUId" text NOT NULL
);


ALTER TABLE public."Portion" OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 24584)
-- Name: Primary_Site; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Primary_Site" (
    "Site_Id" integer NOT NULL,
    "Site" text
);


ALTER TABLE public."Primary_Site" OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 24808)
-- Name: Primary_Site_Site_Id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public."Primary_Site" ALTER COLUMN "Site_Id" ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public."Primary_Site_Site_Id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 215 (class 1259 OID 24577)
-- Name: Project; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Project" (
    "Project_Id" text NOT NULL,
    "Name" text
);


ALTER TABLE public."Project" OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 32823)
-- Name: Protein; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Protein" (
    "AGID" text NOT NULL
);


ALTER TABLE public."Protein" OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 32847)
-- Name: Protein_Expression_File; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Protein_Expression_File" (
    "File" text NOT NULL,
    "Protein" text NOT NULL,
    "Expression" numeric
);


ALTER TABLE public."Protein_Expression_File" OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 24785)
-- Name: Sample; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Sample" (
    "Sample_Id" text NOT NULL,
    "Sample_UUId" text NOT NULL,
    "Type" integer,
    "Tumor" integer
);


ALTER TABLE public."Sample" OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 24694)
-- Name: Sample_Type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Sample_Type" (
    "Type_Id" integer NOT NULL,
    "Type" text
);


ALTER TABLE public."Sample_Type" OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 24701)
-- Name: Tumor; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Tumor" (
    "Tumor_Code_Id" integer NOT NULL,
    "Code" text,
    "Descriptor" text
);


ALTER TABLE public."Tumor" OWNER TO postgres;

--
-- TOC entry 4795 (class 2606 OID 24824)
-- Name: Aliquote_Type Aliquote_Type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Aliquote_Type"
    ADD CONSTRAINT "Aliquote_Type_pkey" PRIMARY KEY ("Type_Id");


--
-- TOC entry 4801 (class 2606 OID 24882)
-- Name: Aliquote Aliquote_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Aliquote"
    ADD CONSTRAINT "Aliquote_pkey" PRIMARY KEY ("Aliquote_UUId", "Aliquote_Id");


--
-- TOC entry 4793 (class 2606 OID 24816)
-- Name: Analyte_Type Analyte_Type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Analyte_Type"
    ADD CONSTRAINT "Analyte_Type_pkey" PRIMARY KEY ("Type_Id");


--
-- TOC entry 4799 (class 2606 OID 24860)
-- Name: Analyte Analyte_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Analyte"
    ADD CONSTRAINT "Analyte_pkey" PRIMARY KEY ("Analyte_Id", "Analyte_UUId");


--
-- TOC entry 4789 (class 2606 OID 24765)
-- Name: Biospecimen Biospecimen_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Biospecimen"
    ADD CONSTRAINT "Biospecimen_pkey" PRIMARY KEY ("Id", "UUId");


--
-- TOC entry 4783 (class 2606 OID 24661)
-- Name: Case Case_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Case"
    ADD CONSTRAINT "Case_pkey" PRIMARY KEY ("Case_UUId");


--
-- TOC entry 4781 (class 2606 OID 24597)
-- Name: Disease Disease_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Disease"
    ADD CONSTRAINT "Disease_pkey" PRIMARY KEY ("Disease_Id");


--
-- TOC entry 4805 (class 2606 OID 32793)
-- Name: File_Entity File_Entity_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."File_Entity"
    ADD CONSTRAINT "File_Entity_pkey" PRIMARY KEY ("File", "Biospecimen_Id", "Biospecimen_UUId");


--
-- TOC entry 4803 (class 2606 OID 32781)
-- Name: File File_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."File"
    ADD CONSTRAINT "File_pkey" PRIMARY KEY ("File_Id");


--
-- TOC entry 4813 (class 2606 OID 32836)
-- Name: Gene_Expression_File Gene_Expression_File_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Gene_Expression_File"
    ADD CONSTRAINT "Gene_Expression_File_pkey" PRIMARY KEY ("File");


--
-- TOC entry 4809 (class 2606 OID 32817)
-- Name: Gene_Type Gene_Type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Gene_Type"
    ADD CONSTRAINT "Gene_Type_pkey" PRIMARY KEY ("Type_Id");


--
-- TOC entry 4807 (class 2606 OID 32810)
-- Name: Gene Gene_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Gene"
    ADD CONSTRAINT "Gene_pkey" PRIMARY KEY ("Gene_Id");


--
-- TOC entry 4797 (class 2606 OID 24843)
-- Name: Portion Portion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Portion"
    ADD CONSTRAINT "Portion_pkey" PRIMARY KEY ("Portion_Id", "Portion_UUId");


--
-- TOC entry 4779 (class 2606 OID 24590)
-- Name: Primary_Site Primary_Site_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Primary_Site"
    ADD CONSTRAINT "Primary_Site_pkey" PRIMARY KEY ("Site_Id");


--
-- TOC entry 4777 (class 2606 OID 24583)
-- Name: Project Project_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Project"
    ADD CONSTRAINT "Project_pkey" PRIMARY KEY ("Project_Id");


--
-- TOC entry 4815 (class 2606 OID 32853)
-- Name: Protein_Expression_File Protein_Expression_File_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Protein_Expression_File"
    ADD CONSTRAINT "Protein_Expression_File_pkey" PRIMARY KEY ("File", "Protein");


--
-- TOC entry 4811 (class 2606 OID 32829)
-- Name: Protein Protein_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Protein"
    ADD CONSTRAINT "Protein_pkey" PRIMARY KEY ("AGID");


--
-- TOC entry 4785 (class 2606 OID 24700)
-- Name: Sample_Type Sample_Type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Sample_Type"
    ADD CONSTRAINT "Sample_Type_pkey" PRIMARY KEY ("Type_Id");


--
-- TOC entry 4791 (class 2606 OID 24791)
-- Name: Sample Sample_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Sample"
    ADD CONSTRAINT "Sample_pkey" PRIMARY KEY ("Sample_Id", "Sample_UUId");


--
-- TOC entry 4787 (class 2606 OID 24707)
-- Name: Tumor Tumor_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Tumor"
    ADD CONSTRAINT "Tumor_pkey" PRIMARY KEY ("Tumor_Code_Id");


--
-- TOC entry 4829 (class 2606 OID 24888)
-- Name: Aliquote Analyte; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Aliquote"
    ADD CONSTRAINT "Analyte" FOREIGN KEY ("Analyte_Id", "Analyte_UUId") REFERENCES public."Analyte"("Analyte_Id", "Analyte_UUId");


--
-- TOC entry 4821 (class 2606 OID 24792)
-- Name: Sample Biospecimen; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Sample"
    ADD CONSTRAINT "Biospecimen" FOREIGN KEY ("Sample_Id", "Sample_UUId") REFERENCES public."Biospecimen"("Id", "UUId");


--
-- TOC entry 4824 (class 2606 OID 24844)
-- Name: Portion Biospecimen; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Portion"
    ADD CONSTRAINT "Biospecimen" FOREIGN KEY ("Portion_Id", "Portion_UUId") REFERENCES public."Biospecimen"("Id", "UUId");


--
-- TOC entry 4826 (class 2606 OID 24861)
-- Name: Analyte Biospecimen; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Analyte"
    ADD CONSTRAINT "Biospecimen" FOREIGN KEY ("Analyte_Id", "Analyte_UUId") REFERENCES public."Biospecimen"("Id", "UUId");


--
-- TOC entry 4830 (class 2606 OID 24883)
-- Name: Aliquote Biospecimen; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Aliquote"
    ADD CONSTRAINT "Biospecimen" FOREIGN KEY ("Aliquote_Id", "Aliquote_UUId") REFERENCES public."Biospecimen"("Id", "UUId");


--
-- TOC entry 4833 (class 2606 OID 32794)
-- Name: File_Entity Biospecimen; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."File_Entity"
    ADD CONSTRAINT "Biospecimen" FOREIGN KEY ("Biospecimen_Id", "Biospecimen_UUId") REFERENCES public."Biospecimen"("Id", "UUId");


--
-- TOC entry 4816 (class 2606 OID 24677)
-- Name: Demographic Case; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Demographic"
    ADD CONSTRAINT "Case" FOREIGN KEY ("Case") REFERENCES public."Case"("Case_UUId") NOT VALID;


--
-- TOC entry 4820 (class 2606 OID 32768)
-- Name: Biospecimen Case; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Biospecimen"
    ADD CONSTRAINT "Case" FOREIGN KEY ("Case") REFERENCES public."Case"("Case_UUId") NOT VALID;


--
-- TOC entry 4817 (class 2606 OID 24672)
-- Name: Case Disease; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Case"
    ADD CONSTRAINT "Disease" FOREIGN KEY ("Disease") REFERENCES public."Disease"("Disease_Id");


--
-- TOC entry 4834 (class 2606 OID 32799)
-- Name: File_Entity File; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."File_Entity"
    ADD CONSTRAINT "File" FOREIGN KEY ("File") REFERENCES public."File"("File_Id");


--
-- TOC entry 4836 (class 2606 OID 32837)
-- Name: Gene_Expression_File File; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Gene_Expression_File"
    ADD CONSTRAINT "File" FOREIGN KEY ("File") REFERENCES public."File"("File_Id");


--
-- TOC entry 4838 (class 2606 OID 32854)
-- Name: Protein_Expression_File File; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Protein_Expression_File"
    ADD CONSTRAINT "File" FOREIGN KEY ("File") REFERENCES public."File"("File_Id");


--
-- TOC entry 4837 (class 2606 OID 32842)
-- Name: Gene_Expression_File Gene; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Gene_Expression_File"
    ADD CONSTRAINT "Gene" FOREIGN KEY ("Gene") REFERENCES public."Gene"("Gene_Id");


--
-- TOC entry 4827 (class 2606 OID 24866)
-- Name: Analyte Portion; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Analyte"
    ADD CONSTRAINT "Portion" FOREIGN KEY ("Portion_Id", "Portion_UUId") REFERENCES public."Portion"("Portion_Id", "Portion_UUId");


--
-- TOC entry 4818 (class 2606 OID 24662)
-- Name: Case Project; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Case"
    ADD CONSTRAINT "Project" FOREIGN KEY ("Project") REFERENCES public."Project"("Project_Id");


--
-- TOC entry 4832 (class 2606 OID 32782)
-- Name: File Project; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."File"
    ADD CONSTRAINT "Project" FOREIGN KEY ("Project") REFERENCES public."Project"("Project_Id");


--
-- TOC entry 4839 (class 2606 OID 32859)
-- Name: Protein_Expression_File Protein; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Protein_Expression_File"
    ADD CONSTRAINT "Protein" FOREIGN KEY ("Protein") REFERENCES public."Protein"("AGID");


--
-- TOC entry 4825 (class 2606 OID 24849)
-- Name: Portion Sample; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Portion"
    ADD CONSTRAINT "Sample" FOREIGN KEY ("Sample_Id", "Sample_UUId") REFERENCES public."Sample"("Sample_Id", "Sample_UUId");


--
-- TOC entry 4819 (class 2606 OID 24667)
-- Name: Case Site; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Case"
    ADD CONSTRAINT "Site" FOREIGN KEY ("Site") REFERENCES public."Primary_Site"("Site_Id");


--
-- TOC entry 4822 (class 2606 OID 24802)
-- Name: Sample Tumor; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Sample"
    ADD CONSTRAINT "Tumor" FOREIGN KEY ("Tumor") REFERENCES public."Tumor"("Tumor_Code_Id");


--
-- TOC entry 4823 (class 2606 OID 24797)
-- Name: Sample Type; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Sample"
    ADD CONSTRAINT "Type" FOREIGN KEY ("Type") REFERENCES public."Sample_Type"("Type_Id");


--
-- TOC entry 4828 (class 2606 OID 24871)
-- Name: Analyte Type; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Analyte"
    ADD CONSTRAINT "Type" FOREIGN KEY ("Type") REFERENCES public."Analyte_Type"("Type_Id");


--
-- TOC entry 4831 (class 2606 OID 24893)
-- Name: Aliquote Type; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Aliquote"
    ADD CONSTRAINT "Type" FOREIGN KEY ("Type") REFERENCES public."Aliquote_Type"("Type_Id");


--
-- TOC entry 4835 (class 2606 OID 32818)
-- Name: Gene Type; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Gene"
    ADD CONSTRAINT "Type" FOREIGN KEY ("Type") REFERENCES public."Gene_Type"("Type_Id") NOT VALID;


-- Completed on 2023-10-05 12:51:49

--
-- PostgreSQL database dump complete
--

