import requests
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json
import pandas as pd
from io import StringIO
from tools import drop_database, populate_database

# Parametri per la connessione al database PostgreSQL
db_genetic_data_params = {
    'host': 'localhost',    # Indirizzo del server del database
    'database': 'genetic_data',      # Nome del database
    'user': 'postgres',     # Nome utente
    'password': 'maurizio',     # Password
    'port' : 5432           # Porta di connessione
}

overall_filters = {
    "op": "and",
    "content": [
        #Filtro riguardante il sito primario della malattia che vogliamo analizzare
        {
            "op": "=",
            "content": {
                "field": "cases.primary_site",
                # "value": "Breast"
                "value": "Liver and intrahepatic bile ducts"
            }
        },

        # {
        #     "op": "in",
        #     "content": {
        #         "field": "cases.samples.sample_type",
        #         "value": ["Primary Solid Tumor", "Metastatic", "Blood Derived Normal", "Solid Tissue Normal",
        #                   "Human Tumor Original Cells", "Primary Blood Derived Cancer - Peripheral Blood",
        #                   "Primary Blood Derived Cancer - Bone Marrow", "Additional - New Primary",
        #                   "Next Generation Cancer Model", "Expanded Next Generation Cancer Model"]
        #     }
        # },


        # Filtro riguardante il tipo di dati che vogliamo analizzare
        {
            "op": "in",
            "content": {
                "field": "data_type",
                "value": ["Gene Expression Quantification"]
            }
        },

        # Filtro riguardante l'accesso dei dati
        {
            "op": "=",
            "content": {
                "field": "access",
                "value": "open"
            }
        },

        # Filtro riguardante il formato del file su cui è riportata l'analisi
        {
            "op": "=",
            "content": {
                "field": "data_format",
                "value": "TSV"
            }
        }
    ]
    }

requests_timeout = 15
requests_tries = 10

def download_data(url, req_timeout, req_tries, parameters=None):
    tries_count = 0

    while tries_count < req_tries:
        try:
            print("downloading", url, end=" ")
            response = requests.get(url, params=parameters, timeout=req_timeout)
            print("got data")
            return response
        except requests.RequestException as request_error:
            print(f"error: {request_error}")
            tries_count += 1
    return None

# Funzione per scaricare e processare i dati di espressione da GDC
def download_and_process_expression_data(db_params):
    # Definizioni delle query SQL utilizzate nel codice

    cerca_progetto = "SELECT COUNT(*) FROM project WHERE project_id = %s"
    cerca_caso = "SELECT COUNT(*) FROM public.case WHERE case_id = %s"
    cerca_file = "SELECT COUNT(*) FROM analysis WHERE file_id = %s"
    cerca_tipo_categoria_strategia = "SELECT type_id, category_id, strategy_id FROM data_type, data_category, experimental_strategy WHERE type = %s AND category = %s AND strategy = %s"
    cerca_tipo_gene = "SELECT type_id FROM gene_type WHERE type = %s"

    inserisci_analisi = "INSERT INTO analysis VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    inserisci_entita_analisi = "INSERT INTO analysis_entity VALUES (%s, %s)"
    inserisci_espressione_genica = "INSERT INTO gene_expression_file VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    inserisci_gene = "INSERT INTO gene VALUES (%s, %s, %s) ON CONFLICT (gene_id) DO NOTHING;"
    inserisci_proteina = "INSERT INTO protein VALUES (%s, %s, %s, %s, %s) ON CONFLICT (agid) DO NOTHING;"
    inserisci_espressione_proteica = "INSERT INTO protein_expression_file VALUES (%s, %s, %s)"

    try:
        # Crea una connessione al database PostgreSQL
        connection = psycopg2.connect(**db_params)

        # Crea un cursore per eseguire query SQL
        cursor = connection.cursor()

        # Inizia la transazione
        connection.autocommit = False
        
        # Ora sei connesso al database
        print("Connessione riuscita")

        # URL dell'API GDC per scaricare i file corrispondenti alle analisi
        gdc_api_url = "https://api.gdc.cancer.gov/files"

        #lista_file = cursor.execute("SELECT file_id FROM analysis")
        #results = cursor.fetchall()
        #file_ids = [result[0] for result in results]

        # Scaricamento dei dati


        params = {
            "filters": json.dumps(overall_filters),
            # Puoi aggiungere altri campi che danno più info relative al file
            "fields": "file_name,file_size,created_datetime,updated_datetime,data_type,experimental_strategy,data_category,cases.project.project_id,cases.case_id,cases.submitter_id,associated_entities.entity_submitter_id,cases.samples,cases.samples.sample_id,cases.samples.sample_type,files.cases.samples",
            "format": "JSON",
            "size": "1600",  # Numero massimo di file da scaricare per richiesta
            "pretty": "true"
        }


        response = download_data(gdc_api_url, requests_timeout, requests_tries, params)

        if response is not None:
            hits_data = json.loads(response.content.decode("utf-8"))["data"]["hits"]

            print("received", len(hits_data), "hits")

            skip_genes = True
            skip_genes = False

            # Elaborazione dei dati e inserimento nel database
            for hit_n, file_info in enumerate(hits_data[:]):
                print("hit", hit_n + 1, "of", len(hits_data))
                file_id = file_info["id"]

                # Verifica se il file è già presente nel database
                cursor.execute(cerca_file, (file_id,))
                result = cursor.fetchone()
                if result[0] != 0:
                    continue

                all_cases = file_info["cases"]
                if len(all_cases) > 1:
                    print("found a file with more than one case!!!!!!!")

                for case in all_cases:
                    project_id = case["project"]["project_id"]

                    # Verifica se il progetto è già presente nel database
                    cursor.execute(cerca_progetto, (project_id,))
                    result = cursor.fetchone()
                    if result[0] == 0:
                        project_present = False
                    else:
                        project_present = True

                    if not project_present:
                        project_present = add_project(project_id, cursor)

                    if project_present:

                        # there is always one sample per case, as we are downloading files
                        # a file is always associated to a sample
                        sample_id = case["samples"][0]['sample_id']

                        # get all the samples associated to the case
                        case_data = download_case_data(case["case_id"])

                        if "samples" in case_data:
                            all_samples = case_data["samples"]
                        else:
                            all_samples = []

                        # Verifica se il caso è già presente nel database
                        # cursor.execute(cerca_caso, (case["submitter_id"],))
                        cursor.execute(cerca_caso, (case["case_id"],))
                        result = cursor.fetchone()

                        if result[0] == 0:
                            add_case(case_data, case["case_id"], project_id, cursor)
                            # connection.commit()

                        sample_submitter_id = None
                        if all_samples != []:
                            sample_submitter_id = add_sample(all_samples, case["case_id"], sample_id, file_id, cursor)
                            # connection.commit()

                            # Verifica se il file è già presente nel database
                            cursor.execute(cerca_file, (file_id,))
                            result = cursor.fetchone()

                            if result[0] == 0:
                                cursor.execute(cerca_tipo_categoria_strategia, (file_info["data_type"], file_info["data_category"], file_info["experimental_strategy"],))
                                type_category_strategy_id = cursor.fetchone()
                                type_id = type_category_strategy_id[0]

                                # Inserisci i dettagli del file nel database

                                cursor.execute(inserisci_analisi, (file_id, file_info["file_name"], file_info["file_size"], file_info["created_datetime"], file_info["updated_datetime"], project_id, type_id, type_category_strategy_id[1], type_category_strategy_id[2], sample_submitter_id))

                                cursor.execute(inserisci_entita_analisi, (file_id, sample_submitter_id))
                                for entity in file_info["associated_entities"]:
                                    cursor.execute(inserisci_entita_analisi, (file_id, entity["entity_submitter_id"]))

                                # Scarica i dati dal file e inseriscili nel database
                                if not skip_genes:
                                    expression_data = download_gene_expression_file(file_id, type_id)
                                    if expression_data == []:
                                        print("problem downloading file", file_id)
                                        print("rolling back")
                                        connection.rollback()
                                    else:
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

                                                if stranded_first != 0 and stranded_second != 0:
                                                    cursor.execute(inserisci_espressione_genica, (file_id, gene_id, data_row["tpm_unstranded"], data_row["fpkm_unstranded"], data_row["fpkm_uq_unstranded"], data_row["unstranded"], stranded_first, stranded_second))

                                        elif type_id == 2:
                                            # Inserimento dei dati di espressione proteica nel database
                                            for data_row in expression_data:
                                                agid = data_row["AGID"]
                                                expression = data_row["protein_expression"]

                                                # Inserisci la proteina nel database
                                                #cursor.execute(inserisci_proteina, (agid, data_row["lab_id"], data_row["catalog_number"], data_row["set_id"], data_row["peptide_target"]))

                                                if expression != "NaN":
                                                    cursor.execute(inserisci_espressione_proteica, (file_id, agid, expression))
                                        print("File inserito nel database")

                                connection.commit()

                            # Ignora il conflitto e passa al prossimo file
                            else:
                                print("file is already in the database")
                                connection.rollback()
                        else:
                            print("problem downloading case samples")
                            connection.rollback()
                    else:
                        print("problem adding project")
                        connection.rollback()
        # Commit della transazione        
        # connection.commit()
        print(f"Download, elaborazione e inserimento dei dati completati.")

    except psycopg2.Error as db_error:
        # Gestione degli errori del database
        connection.rollback()
        print(f"Errore nel database: {db_error}")

    except Exception as error:
        # Gestione generica degli errori
        connection.rollback()
        print(f"Errore sconosciuto: {error}")

    finally:
        # Ripristina l'autocommit
        connection.rollback()
        connection.autocommit = True

        # Chiudi la connessione
        cursor.close()
        connection.close()

# Funzione per inserire un nuovo progetto nel database
def add_project(target_project_id, cursor):
    project_url = "https://api.gdc.cancer.gov/projects/" + target_project_id
    inserisci_progetto = "INSERT INTO public.project VALUES (%s, %s) ON CONFLICT (project_id) DO NOTHING;"

    params = {
        #Puoi aggiungere altri campi che danno più info relative al progetto
        "fields": "name",
        "format": "JSON",
        "pretty": "true"
    }

    response = download_data(project_url, requests_timeout, requests_tries, params)
    if response is not None and response.status_code == 200:
        data = json.loads(response.content.decode("utf-8"))["data"]

        cursor.execute(inserisci_progetto, (target_project_id, data["name"]))
        print("Added project", target_project_id, "to database")
        return True
    else:
        return False

def download_case_data(target_case_id):
    cases_url = "https://api.gdc.cancer.gov/cases/" + target_case_id

    params = {
        "filters": json.dumps(overall_filters),
        # Puoi aggiungere altri campi che danno più info relative al caso
        "fields": "files.submitter_id,submitter_id,demographic.ethnicity,demographic.gender,demographic.race,demographic.vital_status,primary_site,disease_type,samples.submitter_id,samples.sample_type,samples.sample_id,samples.sample_type_id,samples.tumor_code,samples.tumor_code_id,samples.tumor_descriptor,samples.portions.submitter_id,samples.portions.analytes.submitter_id,samples.files,samples.portions.analytes.concentration,samples.portions.analytes.aliquots.submitter_id,samples.portions.analytes.aliquots.concentration",
        # samples.portions.slides.submitter_id
        "expand": "true",
        "format": "JSON",
        "pretty": "true"
    }

    response = download_data(cases_url, requests_timeout, requests_tries, params)

    if response is not None and response.status_code == 200:
        data = json.loads(response.content.decode("utf-8"))["data"]
        return data
    else:
        return {}


# Funzione per inserire un nuovo caso nel database
def add_case(target_case_data, target_case_id, project_id, cursor):

    cerca_sito = "SELECT site_id FROM primary_site WHERE site = %s"
    cerca_malattia = "SELECT disease_id FROM disease WHERE type = %s"

    inserisci_caso = "INSERT INTO public.case VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"

    if target_case_data != {}:

        # case_id = data["submitter_id"]

        tipo_malattia = target_case_data["disease_type"]

        cursor.execute(cerca_sito, (target_case_data["primary_site"],))
        site = cursor.fetchone()

        cursor.execute(cerca_malattia, (tipo_malattia,))
        disease = cursor.fetchone()
        if disease == None:
            cursor.execute("INSERT INTO disease(type) VALUES (%s);", (tipo_malattia,))
            cursor.execute(cerca_malattia, (tipo_malattia,))
            disease = cursor.fetchone()

        if "demographic" in target_case_data:
            cursor.execute(inserisci_caso, (target_case_id, target_case_data["demographic"]["ethnicity"], target_case_data["demographic"]["gender"], target_case_data["demographic"]["race"], target_case_data["demographic"]["vital_status"], project_id, site[0], disease[0]))
        else:
            cursor.execute(inserisci_caso, (target_case_id, None, None, None, None, project_id, site[0], disease[0]))

        print("added case", target_case_id, "to database")


def sample_print(sample):
    if "sample_type" in sample:
        print("sample_type:      ", sample["sample_type"])
    else:
        print("sample_type not present!")
    if "sample_type_id" in sample:
        print("sample_type_id:   ", sample["sample_type_id"])
    else:
        print("sample_type_id not present!")
    if "tumor_code_id" in sample:
        print("tumor_code_id:    ", sample["tumor_code_id"])
    else:
        print("tumor_code_id not present!")
    if "tumor_code" in sample:
        print("tumor_code:       ", sample["tumor_code"])
    else:
        print("tumor_code not present!")
    if "tumor_descriptor" in sample:
        print("tumor_descriptor: ", sample["tumor_descriptor"], end="\n\n")
    else:
        print("tumor_descriptor not present!", end="\n\n")
        
# Funzione per inserire informazioni sui campioni nel database
def add_sample(samples_list, case_id, target_sample_id, target_file_id, cursor):
    inserisci_biospecie = "INSERT INTO biospecimen VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING;"
    inserisci_tumore = "INSERT INTO tumor VALUES (%s, %s, %s) ON CONFLICT (tumor_code_id) DO NOTHING;"
    inserisci_tipo_campione = "INSERT INTO sample_type VALUES (%s, %s) ON CONFLICT (type_id) DO NOTHING;"
    inserisci_campione = "INSERT INTO sample VALUES (%s, %s, %s)"
    inserisci_porzione = "INSERT INTO portion VALUES (%s, %s) ON CONFLICT (portion_id) DO NOTHING;"
    inserisci_analita = "INSERT INTO analyte VALUES (%s, %s, %s) ON CONFLICT (analyte_id) DO NOTHING;"
    inserisci_aliquota = "INSERT INTO aliquote VALUES (%s, %s, %s) ON CONFLICT (aliquote_id) DO NOTHING;"
    select_sample = "SELECT * FROM sample WHERE sample_id = %s"
    get_sample_type_id = "SELECT type_id FROM sample_type WHERE type = %s"
    inserisci_slide = "INSERT INTO slide VALUES (%s, %s)"

    sample_submitter_id = None

    for sample in samples_list:

        # sample_print(sample)
        # why is the submitter id used as sample id?
        sample_id = sample["sample_id"]

        if sample_id == target_sample_id:
        
            if "tumor_code_id" in sample and sample["tumor_code_id"] != None:
                tumor_code = sample["tumor_code_id"]
                cursor.execute(inserisci_tumore, (tumor_code, sample["tumor_code"], sample["tumor_descriptor"]))
            else:
                tumor_code = None

            if "sample_type_id" in sample and sample["sample_type_id"] != None:
                type_id = sample["sample_type_id"]
                cursor.execute(inserisci_tipo_campione, (type_id, sample["sample_type"]))
            else:
                cursor.execute(get_sample_type_id, (sample["sample_type"],))
                type_id = cursor.fetchone()
                if type_id is not None:
                    type_id = type_id[0]
                else:
                    type_id = None

            sample_submitter_id = sample['submitter_id']
            cursor.execute(inserisci_biospecie, (sample_submitter_id, case_id, 1))

            cursor.execute(select_sample, (sample_submitter_id,))
            result = cursor.fetchone()
            if result is None:
                print("adding sample", sample_submitter_id)
                cursor.execute(inserisci_campione, (sample_submitter_id, type_id, tumor_code))
                print("added sample", sample_submitter_id)
            else:
                print("******** sample", sample_submitter_id, "already present!")

            if "portions" in sample:
                for portion in sample["portions"]:
                    if "submitter_id" in portion:
                        portion_id = portion["submitter_id"]
                    else: portion_id = 1

                    cursor.execute(inserisci_biospecie, (portion_id, case_id, 2))
                    cursor.execute(inserisci_porzione, (portion_id, sample_submitter_id))
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

    return sample_submitter_id



# Funzione per scaricare e processare un file specifico
def download_gene_expression_file(file_id, datatype_id):

    file_url = "https://api.gdc.cancer.gov/data/" + file_id

    response = download_data(file_url, requests_timeout, requests_tries)

    if response is not None and response.status_code == 200:
        # Elabora i dati dal file scaricato
        if datatype_id == 1: data = pd.read_csv(StringIO(response.text), sep="\t", comment="#", skiprows=[2,3,4,5])
        elif datatype_id == 2: data = pd.read_csv(StringIO(response.text), sep="\t", comment="#")
        else:
            print("unknown data type while processing file:", datatype_id)
            return []
        expression_data = data.to_dict(orient="records")
        return expression_data
    else:
        print("error downloading", file_url)
        return []

if __name__ == "__main__":
    answer = input("do you want to delete the database? (y/N) ")
    if answer == "y":
        answer = input("are you sure? (y/N): ")
        if answer == "y":
            drop_database(db_genetic_data_params, "genetic_data")
            populate_database(db_genetic_data_params, "genetic_data", "../db/init_db_genetic_data.sql")
            
    download_and_process_expression_data(db_genetic_data_params)