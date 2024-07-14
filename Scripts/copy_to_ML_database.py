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

def copy_to_ML_database(from_db_params, to_db_params):
    try:
        from_connection = psycopg2.connect(**from_db_params)
        to_connection = psycopg2.connect(**to_db_params)

        from_cursor = from_connection.cursor()
        to_cursor = to_connection.cursor()

        from_connection.autocommit = False
        to_connection.autocommit = False
        
        print("Connessione riuscita")

        get_gene_expressions = "SELECT * from gene_expression_file where analysis = '{}'"
        
        get_sample_id = "SELECT sample_id FROM sample_type WHERE analysis_id = '{}'"
        add_sample_id = "INSERT INTO sample_type (analysis_id) VALUES ('{}') ON CONFLICT (analysis_id) DO NOTHING;"
        
        get_measurement_id = "SELECT measurement_id FROM measurement_type where name = '{}' AND unit = '{}';"
        add_measurement_id = "INSERT INTO measurement_type (name, unit) VALUES ('{}', '{}') ON CONFLICT (name, unit) DO NOTHING;"

        add_measurement = "INSERT INTO measurement (sample_id, measurement_id, value) VALUES ({}, {}, '{}')"
        
        get_analysis_from = "SELECT * FROM analysis_entity"
        
        get_analysis_to = "SELECT * FROM sample_type WHERE analysis_id = '{}'"
        
        genes = set()
        
        query = get_analysis_from
        from_cursor.execute(query)
        
        all_analysis = []
        for analysis_iter in from_cursor:
            all_analysis.append(analysis_iter[0])
        
        for analysis_iter in all_analysis:
            
            query = get_analysis_to.format(analysis_iter)
            to_cursor.execute(query)
            
            if to_cursor.fetchone() is None:
                
                query = get_gene_expressions.format(analysis_iter)
                from_cursor.execute(query)
        
                for gene_expression in from_cursor:
                    analysis = gene_expression[0]
                    gene = gene_expression[1]
                    tpm = gene_expression[2]
                    
                    genes.add(gene)

                    query = get_sample_id.format(analysis)
                    to_cursor.execute(query)
                    sample_id = to_cursor.fetchone()
                    
                    if sample_id is None:
                        query = add_sample_id.format(analysis)
                        to_cursor.execute(query)
                        query = get_sample_id.format(analysis)
                        to_cursor.execute(query)
                        sample_id = to_cursor.fetchone()
                        
                    sample_id = sample_id[0]
                    
                    query = add_measurement_id.format(gene, "tpm")
                    to_cursor.execute(query)
                    
                    query = get_measurement_id.format(gene, "tpm")
                    to_cursor.execute(query)
                    measurement_id = to_cursor.fetchone()[0]
                    
                    query = add_measurement.format(int(sample_id), int(measurement_id), tpm)
                    to_cursor.execute(query)
            else:
                print("analysis", analysis_iter, "already present in the db")
            to_connection.commit()
            from_connection.commit()
        
        print(len(genes))
            
        
        '''# Elaborazione dei dati e inserimento nel database
        for file_info in json.loads(response.content.decode("utf-8"))["data"]["hits"]:
            file_id = file_info["id"]
            if len(file_info["cases"]) > 1:
                print("found a file with more than one case!")
            for case in file_info["cases"]:
                project_id = case["project"]["project_id"]

                # Verifica se il progetto è già presente nel database
                cursor.execute(cerca_progetto, (project_id,))
                result = cursor.fetchone()
                if result[0] == 0: 
                    # Se il progetto non è presente, esegui la funzione project() per inserirlo
                    project(project_id, cursor)
                    connection.commit()

                # Verifica se il caso è già presente nel database
                cursor.execute(cerca_caso, (case["submitter_id"],))
                result = cursor.fetchone()
                if result[0] == 0: 
                    # Se il caso non è presente, esegui la funzione cases() per inserirlo
                    cases(case["case_id"], project_id, cursor)
                    connection.commit()

                # Verifica se il file è già presente nel database
                cursor.execute(cerca_file, (file_id,))
                result = cursor.fetchone()
                if result[0] == 0:
                    cursor.execute(cerca_tipo_categoria_strategia, (file_info["data_type"], file_info["data_category"], file_info["experimental_strategy"],))
                    type_category_strategy_id = cursor.fetchone()
                    type_id = type_category_strategy_id[0]

                    # Inserisci i dettagli del file nel database
                    cursor.execute(inserisci_analisi, (file_id, file_info["file_name"], file_info["file_size"], file_info["created_datetime"], file_info["updated_datetime"], project_id, type_id, type_category_strategy_id[1], type_category_strategy_id[2]))
                    
                    # Scarica i dati dal file e inseriscili nel database
                    expression_data = download_and_process_file(file_id, type_id)

                    for entity in file_info["associated_entities"]: cursor.execute(inserisci_entita_analisi, (file_id, entity["entity_submitter_id"]))
                    connection.commit()
                    
                    if type_id == 1:
                        for data_row in expression_data:
                            # Inserimento dei dati di espressione genica nel database
                            gene_id = data_row["gene_id"]
                            stranded_first = data_row["stranded_first"]
                            stranded_second = data_row["stranded_second"]

                            # Verifica se il tipo di gene è già presente nel database
                            cursor.execute(cerca_tipo_gene, (data_row["gene_type"],))
                            gene_type_id = cursor.fetchone()[0]
                            # Inserisci il gene nel database
                            cursor.execute(inserisci_gene, (gene_id, data_row["gene_name"], gene_type_id))
                            
                            if stranded_first != 0 and stranded_second != 0: cursor.execute(inserisci_espressione_genica, (file_id, gene_id, data_row["tpm_unstranded"], data_row["fpkm_unstranded"], data_row["fpkm_uq_unstranded"], data_row["unstranded"], stranded_first, stranded_second))
                        connection.commit()
                    elif type_id == 2:
                        # Inserimento dei dati di espressione proteica nel database
                        for data_row in expression_data:
                            agid = data_row["AGID"]
                            expression = data_row["protein_expression"]

                            # Inserisci la proteina nel database
                            #cursor.execute(inserisci_proteina, (agid, data_row["lab_id"], data_row["catalog_number"], data_row["set_id"], data_row["peptide_target"]))
                            
                            if expression != "NaN": cursor.execute(inserisci_espressione_proteica, (file_id, agid, expression))
                        connection.commit()
                    print("File inserito nel database")
                # Ignora il conflitto e passa al prossimo file
                else: print("Il file è gia presente nel database")

        # Commit della transazione        
        connection.commit()
        print(f"Download, elaborazione e inserimento dei dati completati.")'''

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