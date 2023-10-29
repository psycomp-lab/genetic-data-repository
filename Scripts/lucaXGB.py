import psycopg2
import pandas as pd
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report
from six import StringIO
import pydotplus
from PIL import Image

# Parametri per la connessione al database PostgreSQL
db_params = {
    'host': 'localhost',
    'database': 'GDC',
    'user': 'postgres',
    'password': 'root',
    'port': 5433
}

# Connessione al database
connection = psycopg2.connect(**db_params)
cursor = connection.cursor()

# Query per estrarre i dati di addestramento dal database
query = """
(
    SELECT tpm, fpkm, fpkm_uq, unstranded, stranded_first, stranded_second, sample_type.type as tissue_label
    FROM gene_expression_file
    JOIN analysis_entity ON gene_expression_file.analysis = analysis_entity.analysis
    JOIN aliquote a ON analysis_entity.biospecimen_id = a.aliquote_id
    JOIN Analyte ay ON a.Analyte_Id = ay.analyte_id
    JOIN portion ON ay.portion_id = portion.Portion_Id
    JOIN sample s ON portion.sample_id = s.sample_id
    JOIN sample_type ON s.type = sample_type.type_id
    WHERE s.Type = 1
    LIMIT 5000
)
UNION
(
    SELECT tpm, fpkm, fpkm_uq, unstranded, stranded_first, stranded_second, sample_type.type as tissue_label
    FROM gene_expression_file
    JOIN analysis_entity ON gene_expression_file.analysis = analysis_entity.analysis
    JOIN aliquote a ON analysis_entity.biospecimen_id = a.aliquote_id
    JOIN Analyte ay ON a.Analyte_Id = ay.analyte_id
    JOIN portion ON ay.portion_id = portion.Portion_Id
    JOIN sample s ON portion.sample_id = s.sample_id
    JOIN sample_type ON s.type = sample_type.type_id
    WHERE s.Type = 11
    LIMIT 5000
);
"""

query2 = """
    SELECT tpm, fpkm, fpkm_uq, unstranded, stranded_first, stranded_second, sample_type.type as tissue_label
    FROM gene_expression_file
    JOIN analysis_entity ON gene_expression_file.analysis = analysis_entity.analysis
    JOIN aliquote a ON analysis_entity.biospecimen_id = a.aliquote_id
    JOIN Analyte ay ON a.Analyte_Id = ay.analyte_id
    JOIN portion ON ay.portion_id = portion.Portion_Id
    JOIN sample s ON portion.sample_id = s.sample_id
    JOIN sample_type ON s.type = sample_type.type_id
    WHERE s.Type in (1, 11) and gene = 'ENSG00000000003.15';
"""

# Esecuzione della query e ottenimento dei dati
cursor.execute(query)
data = cursor.fetchall()
column_names = [desc[0] for desc in cursor.description]
df = pd.DataFrame(data, columns=column_names)

# Separazione dei dati in features (X) e target (y)
X = df.drop('tissue_label', axis=1)
y = df['tissue_label']

# Dividi i dati in set di addestramento e test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Crea e addestra il modello di albero decisionale
model = xgb.XGBClassifier(max_depth=10)
model.fit(X_train, y_train)

# Valuta il modello
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

# Visualizza l'accuratezza e il report di classificazione
print(f'Accuratezza: {accuracy}')
print(f'Report di classificazione:\n{report}')


# Visualizza l'albero decisionale come grafico
xgb.plot_tree(model)
plt.show()

# Chiudi la connessione al database
cursor.close()
connection.close()