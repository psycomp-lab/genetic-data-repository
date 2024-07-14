import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT



def drop_database(db_params, db_name):
    try:
        
        # Crea una connessione al database PostgreSQL
        db_params['database'] = 'postgres'
        
        connection = psycopg2.connect(**db_params)

        # Crea un cursore per eseguire query SQL
        cursor = connection.cursor()
        
        # Inizia la transazione
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Ora sei connesso al database
        print("connected to", db_params['database'])
        
        query = "SELECT datname FROM pg_catalog.pg_database WHERE lower(datname) = lower('" + db_name + "');"
        cursor.execute(query)
        
        result=cursor.fetchone()
        
        if result is not None:
            cursor.execute("DROP database " + db_name + ";")
    
        connection.close()
    
    except Exception as error:
        connection.rollback()
        print(f"Error: {error}")
        
def populate_database(db_params, db_name, sql_file):
    try:
        
        # Crea una connessione al database PostgreSQL
        db_params['database'] = 'postgres'
        
        connection = psycopg2.connect(**db_params)

        # Crea un cursore per eseguire query SQL
        cursor = connection.cursor()
        
        # Inizia la transazione
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Ora sei connesso al database
        print("connected to", db_params['database'])
        
        query = "SELECT datname FROM pg_catalog.pg_database WHERE lower(datname) = lower('" + db_name + "');"
        cursor.execute(query)
        
        result=cursor.fetchone()
        
        if result is None:
            cursor.execute("CREATE database " + db_name + ";")
        
        connection.close()
        
        db_params['database'] = db_name
        
        connection = psycopg2.connect(**db_params)

        # Crea un cursore per eseguire query SQL
        cursor = connection.cursor()
        
        # Inizia la transazione
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Ora sei connesso al database
        print("connected to", db_params['database'])
    
        with open(sql_file, encoding="utf-8") as sqlfile:
            query = "".join(sqlfile.readlines())

        cursor.execute(query)

        connection.close()
    
    except Exception as error:
        connection.rollback()
        print(f"Error: {error}")
    