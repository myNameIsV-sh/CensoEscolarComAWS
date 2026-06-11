import os, io, logging

import pandas as pd
import boto3

from sqlalchemy import create_engine
from botocore.exceptions import ClientError

# Configuração de Logging para CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configurações obtidas do Parameter Store
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
TABLE_NAME = 'microdados_ed_basica'

def get_db_engine():
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(connection_string)

def process_csv_from_s3(bucket_name, file_key):
    s3_client = boto3.client('s3')
    
    logger.info(f"Iniciando leitura do arquivo {file_key} do bucket {bucket_name}")
    
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        # Lê o conteúdo do S3 como stream
        content = response['Body'].read()
        
        # Cria um DataFrame lendo do stream
        df_iter = pd.read_csv(
            io.BytesIO(content), 
            sep=';', 
            encoding='latin-1', 
            chunksize=1000
        )
        
        engine = get_db_engine()
        
        for i, chunk in enumerate(df_iter):
            # Filtro aplicado no chunk
            chunk_filtrado = chunk[chunk['NO_REGIAO'] == 'Nordeste']

            if not chunk_filtrado.empty:
                chunk_filtrado.to_sql(TABLE_NAME, engine, if_exists='append', index=False)
                logger.info(f"Chunk {i} processado e inserido.")
        
        logger.info("Carga finalizada com sucesso.")
        
    except ClientError as e:
        logger.error(f"Erro ao acessar S3: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro durante o processo de ETL: {e}")
        raise

if __name__ == '__main__':
    logger.info("Script configurado para execução via gatilhos AWS.")