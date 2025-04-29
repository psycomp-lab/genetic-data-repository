import requests
import psycopg2
import json
import pandas as pd
from io import StringIO
from tools import drop_database, populate_database

# Parametri per la connessione al database PostgreSQL
from_db = {
    'host': 'localhost',    # Indirizzo del server del database
    'database': 'genetic_data',      # Nome del database
    'user': 'postgres',     # Nome utente
    'password': 'maurizio',     # Password
    'port' : 5432           # Porta di connessione
}

to_db = {
    'host': 'localhost',    # Indirizzo del server del database
    'database': 'genetic_data_ml',      # Nome del database
    'user': 'postgres',     # Nome utente
    'password': 'maurizio',     # Password
    'port' : 5432           # Porta di connessione
}

def get_measurement_id(name1, name2, unit, to_cursor):
    get_measurement_id = "SELECT measurement_id FROM measurement_type where name1 = '{}' AND name2 = '{}' AND unit = '{}';"
    add_measurement_id = "INSERT INTO measurement_type (name1, name2, unit) VALUES ('{}', '{}', '{}') ON CONFLICT (name1, name2, unit) DO NOTHING;"

    query = get_measurement_id.format(name1, name2, unit)
    to_cursor.execute(query)

    if to_cursor.fetchone() is None:
        # add the measurement type
        query = add_measurement_id.format(name1, name2, unit)
        to_cursor.execute(query)
    
    # and get its id
    query = get_measurement_id.format(name1, name2, unit)
    to_cursor.execute(query)
    measurement_id = to_cursor.fetchone()[0]
    
    return measurement_id

def copy_to_ML_database(from_db_params, to_db_params):
    try:
        from_connection = psycopg2.connect(**from_db_params)
        to_connection = psycopg2.connect(**to_db_params)

        from_cursor = from_connection.cursor()
        to_cursor = to_connection.cursor()

        from_connection.autocommit = False
        to_connection.autocommit = False
        
        print("Connessione riuscita")

        get_gene_expressions = "SELECT g.gene_id, g.name, gef.tpm, gef.fpkm, gef.fpkm_uq from gene_expression_file as gef, gene as g where gef.gene = g.gene_id  and analysis = '{}'"
        
        get_sample_id = "SELECT sample_id FROM sample_id_type WHERE original_sample_id = '{}'"
        add_sample_id = "INSERT INTO sample_id_type (original_sample_id) VALUES ('{}') ON CONFLICT (original_sample_id) DO NOTHING;"
        
        get_sample_type = "SELECT type FROM sample WHERE sample_id = '{}'"
        
        get_sample_site = 'select s.sample_id, c.site from analysis_entity ae, sample s, biospecimen b, "case" c where ae.biospecimen_id = s.sample_id and ae.biospecimen_id = b.id and b."case" = c.case_id and s.sample_id = \'{}\';'

        add_measurement = "INSERT INTO measurement (sample_id, measurement_id, value) VALUES ({}, {}, '{}')"
        
        get_analysis_from = "SELECT file_id, sample_id FROM analysis"
        
        get_sample_to = "SELECT * FROM sample_id_type WHERE original_sample_id = '{}'"
        
        genes = set()
        
        query = get_analysis_from
        from_cursor.execute(query)
        
        all_analysis = []
        all_samples = []
        for analysis_iter in from_cursor:
            all_analysis.append(analysis_iter[0])
            all_samples.append(analysis_iter[1])
            
        # for each pair (analysis, sample)
        for index in range(len(all_samples)):
            print("sample", index + 1, "of", len(all_samples))
            analysis_iter = all_analysis[index]
            samples_iter = all_samples[index]
            print("analysis:", analysis_iter, "sample:", samples_iter)

            print("checking if sample", samples_iter, "exists")
            # get the sample id in the new database, if exists
            query = get_sample_to.format(samples_iter)
            to_cursor.execute(query)
            
            # if it does not exist, add all the gene expression values for that sample
            if to_cursor.fetchone() is None:
                print("sample does not exist, so add it")

                query = add_sample_id.format(samples_iter)
                to_cursor.execute(query)
                query = get_sample_id.format(samples_iter)
                to_cursor.execute(query)
                sample_id = to_cursor.fetchone()[0]

                print("sample id for", samples_iter, "is", sample_id)

                # get the gene expression values
                print("get all the genes of the analysis", analysis_iter)
                query = get_gene_expressions.format(analysis_iter)
                from_cursor.execute(query)

                # for each of them
                for gene_expression in from_cursor:
                    gene_ensemble = gene_expression[0]
                    gene_id = gene_expression [1]
                    tpm = gene_expression[2]
                    
                    measurement_id = get_measurement_id(gene_ensemble, gene_id, "tpm", to_cursor)
                    
                    # add the measurement itself
                    query = add_measurement.format(int(sample_id), int(measurement_id), tpm)
                    to_cursor.execute(query)
                
                # finally, add the sample type
                
                # get the sample type
                print("getting sample type")
                query = get_sample_type.format(samples_iter)
                from_cursor.execute(query)
                sample_type = from_cursor.fetchone()[0]

                print("adding it to the measurements")
                measurement_id = get_measurement_id("sample_type", "", "int", to_cursor)

                print("adding sample type value for sample id", sample_id, "(measurement id is", measurement_id, ")")
                query = add_measurement.format(int(sample_id), int(measurement_id), sample_type)
                to_cursor.execute(query)

                # get the sample site
                query = get_sample_site.format(samples_iter)
                from_cursor.execute(query)
                sample_site = from_cursor.fetchone()[1]

                measurement_id = get_measurement_id("sample_site", "", "int", to_cursor)

                query = add_measurement.format(int(sample_id), int(measurement_id), sample_site)
                to_cursor.execute(query)
                
            else:
                print("analysis", analysis_iter, "sample", samples_iter, "already present in the db")
            to_connection.commit()
            from_connection.commit()
        
        print(len(genes))
            

    except psycopg2.Error as db_error:
        # Gestione degli errori del database
        from_connection.rollback()
        to_connection.rollback()
        print(f"Errore nel database: {db_error}")

    # Gestione degli errori di richiesta HTTP
    except requests.RequestException as request_error: print(f"Errore nella richiesta HTTP: {request_error}")

    except Exception as error:
        # Gestione generica degli errori
        from_connection.rollback()
        to_connection.rollback()
        print(f"Errore sconosciuto: {error}")

    finally:
        # Ripristina l'autocommit
        from_connection.autocommit = True
        to_connection.autocommit = True

        # Chiudi la connessione
        from_cursor.close()
        to_cursor.close()
        from_connection.close()
        to_connection.close()

# Funzione per inserire un nuovo progetto nel database
def project(id, cursor):
    project_url = "https://api.gdc.cancer.gov/projects/" + id
    inserisci_progetto = "INSERT INTO public.project VALUES (%s, %s) ON CONFLICT (project_id) DO NOTHING;"

    params = {
        #Puoi aggiungere altri campi che danno più info relative al progetto
        "fields": "name",
        "format": "JSON",
        "pretty": "true"
    }

    response = requests.get(project_url, params=params)

    if response.status_code == 200:
        data = json.loads(response.content.decode("utf-8"))["data"]

        cursor.execute(inserisci_progetto, (id, data["name"]))
        print("Progetto inserito nel database")
    else:
        print(f"Errore durante il download del progetto: {response.status_code}")
        return []

# Funzione per inserire un nuovo caso nel database
def cases(id, project_id, cursor):
    cases_url = "https://api.gdc.cancer.gov/cases/" + id

    cerca_sito = "SELECT site_id FROM primary_site WHERE site = %s"
    cerca_malattia = "SELECT disease_id FROM disease WHERE type = %s"

    inserisci_caso = "INSERT INTO public.case VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"

    params = {
        #Puoi aggiungere altri campi che danno più info relative al caso
        "fields": "submitter_id,demographic.ethnicity,demographic.gender,demographic.race,demographic.vital_status,primary_site,disease_type,samples.submitter_id,samples.sample_type,samples.sample_type_id,samples.tumor_code,samples.tumor_code_id,samples.tumor_descriptor,samples.portions.submitter_id,samples.portions.analytes.submitter_id,samples.portions.analytes.concentration,samples.portions.analytes.aliquots.submitter_id,samples.portions.analytes.aliquots.concentration", #samples.portions.slides.submitter_id
        "format": "JSON",
        "pretty": "true"
    }
    response = requests.get(cases_url, params=params)

    if response.status_code == 200:
        data = json.loads(response.content.decode("utf-8"))["data"]
        case_id = data["submitter_id"]
        tipo_malattia = data["disease_type"]

        cursor.execute(cerca_sito, (data["primary_site"],))
        site = cursor.fetchone()

        cursor.execute(cerca_malattia, (tipo_malattia,))
        disease = cursor.fetchone()
        if disease == None: 
            cursor.execute("INSERT INTO disease(type) VALUES (%s);", (tipo_malattia,))
            cursor.execute(cerca_malattia, (tipo_malattia,))
            disease = cursor.fetchone()

        if "demographic" in data: cursor.execute(inserisci_caso, (case_id, data["demographic"]["ethnicity"], data["demographic"]["gender"], data["demographic"]["race"], data["demographic"]["vital_status"], project_id, site[0], disease[0]))
        else: cursor.execute(inserisci_caso, (case_id, None, None, None, None, project_id, site[0], disease[0]))
        samples(data["samples"], case_id, cursor)
        print("Caso inserito nel database")
    else: 
        print(f"Errore durante il download del caso: {response.status_code}")

# Funzione per inserire informazioni sui campioni nel database
def samples(samples, case_id, cursor):
    inserisci_biospecie = "INSERT INTO biospecimen VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING;"
    inserisci_tumore = "INSERT INTO tumor VALUES (%s, %s, %s) ON CONFLICT (tumor_code_id) DO NOTHING;"
    inserisci_tipo_campione = "INSERT INTO sample_type VALUES (%s, %s) ON CONFLICT (type_id) DO NOTHING;"
    inserisci_campione = "INSERT INTO sample VALUES (%s, %s, %s)"
    inserisci_porzione = "INSERT INTO portion VALUES (%s, %s) ON CONFLICT (portion_id) DO NOTHING;"
    inserisci_analita = "INSERT INTO analyte VALUES (%s, %s, %s) ON CONFLICT (analyte_id) DO NOTHING;"
    inserisci_aliquota = "INSERT INTO aliquote VALUES (%s, %s, %s) ON CONFLICT (aliquote_id) DO NOTHING;"
    inserisci_slide = "INSERT INTO slide VALUES (%s, %s)"

    for sample in samples:
        sample_id = sample["submitter_id"]
        
        if "tumor_code_id" in sample and sample["tumor_code_id"] != None: 
            tumor_code = sample["tumor_code_id"]
            cursor.execute(inserisci_tumore, (tumor_code, sample["tumor_code"], sample["tumor_descriptor"]))
        else: tumor_code = None
        if "sample_type_id" in sample and sample["sample_type_id"] != None: 
            type_id = sample["sample_type_id"]
            cursor.execute(inserisci_tipo_campione, (type_id, sample["sample_type"]))
        else: type_id = None   

        cursor.execute(inserisci_biospecie, (sample_id, case_id, 1))
        cursor.execute(inserisci_campione, (sample_id, type_id, tumor_code))
        if "portions" in sample:
            for portion in sample["portions"]:
                if "submitter_id" in portion: 
                    portion_id = portion["submitter_id"]
                else: portion_id = 1

                cursor.execute(inserisci_biospecie, (portion_id, case_id, 2))
                cursor.execute(inserisci_porzione, (portion_id, sample_id))
                if "analytes" in portion:
                    for analyte in portion["analytes"]:
                        if "submitter_id" in analyte: 
                            analyte_id = analyte["submitter_id"]
                            concentration = analyte["concentration"]
                        else: 
                            analyte_id = 1
                            concentration = None

                        cursor.execute(inserisci_biospecie, (analyte_id, case_id, 3))
                        cursor.execute(inserisci_analita, (analyte_id, portion_id, concentration))
                        if "aliquots" in analyte:
                            for aliquote in analyte["aliquots"]:
                                aliquote_id = aliquote["submitter_id"]

                                if "concentration" in aliquote: concentration = aliquote["concentration"]
                                else: concentration = None

                                cursor.execute(inserisci_biospecie, (aliquote_id, case_id, 4))
                                cursor.execute(inserisci_aliquota, (aliquote_id, analyte_id, concentration))
                #if "slides" in portion:
                    #for slide in portion["slides"]:
                        #slide_id = slide["submitter_id"]

                        #cursor.execute(inserisci_biospecie, (slide_id, case_id, 5))
                        #cursor.execute(inserisci_slide, (slide_id, sample_id))

# Funzione per scaricare e processare un file specifico
def download_and_process_file(file_id, data_id):
    file_url = "https://api.gdc.cancer.gov/data/" + file_id
    response = requests.get(file_url)

    if response.status_code == 200:
        # Elabora i dati dal file scaricato
        if data_id == 1: data = pd.read_csv(StringIO(response.text), sep="\t", comment="#", skiprows=[2,3,4,5])
        elif data_id == 2: data = pd.read_csv(StringIO(response.text), sep="\t", comment="#")
        
        # Trasforma i dati in una lista di dizionari
        expression_data = data.to_dict(orient="records")
        return expression_data
    else:
        print(f"Errore durante il download del file: {response.status_code}")
        return []

if __name__ == "__main__":
    answer = input("do you want to delete the database? (y/N) ")
    if answer == "y":
        answer = input("are you sure? (y/N): ")
        if answer == "y":
            drop_database(to_db, "genetic_data_ml")
            populate_database(to_db, "genetic_data_ml", "../db/init_db_genetic_data_ML.sql")
    copy_to_ML_database(from_db, to_db)