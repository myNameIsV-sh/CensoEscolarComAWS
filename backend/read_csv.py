# Standard library imports
import io
import json
import logging
import os

# Third-party imports
import boto3
import pandas as pd
from sqlalchemy import create_engine

# Configuração de Logging para CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Definições de constantes
TABLE_NAME = 'censo_escolar_paraiba'
COLUNAS_INTERESSE = [
    'NO_ENTIDADE', 'QT_MAT_BAS', 'CO_UF', 'NO_UF', 
    'NO_MUNICIPIO', 'NO_MESORREGIAO', 'NO_MICRORREGIAO'
]

def get_ssm_parameter(parameter_name):
    """Busca um parâmetro no AWS SSM Parameter Store."""
    ssm = boto3.client('ssm')
    response = s3_client = ssm.get_parameter(
        Name=parameter_name, 
        WithDecryption=True
    )
    return response['Parameter']['Value']

def get_db_engine():
    """Configura engine SQLAlchemy buscando credenciais no Parameter Store."""
    # Nota: Assumimos que os nomes dos parâmetros SSM estão definidos
    user = get_ssm_parameter('/dev/flask-app/DB_USER')
    password = get_ssm_parameter('/dev/flask-app/DB_PASSWORD')
    host = get_ssm_parameter('/dev/flask-app/DB_HOST')
    port = get_ssm_parameter('/dev/flask-app/DB_PORT')
    db_name = get_ssm_parameter('/dev/flask-app/DB_NAME')
    
    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    return create_engine(connection_string)

# Inicialização global (reutilizado entre invocações)
engine = get_db_engine()
s3_client = boto3.client('s3')

def process_csv_from_s3(bucket_name, file_key):
    """Processa CSV do S3, filtra para Paraíba e insere no RDS."""
    logger.info(f"Processando {file_key} do bucket {bucket_name}")
    
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    
    # Leitura em chunks de 10.000 conforme RF-006
    df_iter = pd.read_csv(
        io.BytesIO(response['Body'].read()), 
        sep=';', 
        encoding='latin-1', 
        chunksize=10000,
        usecols=COLUNAS_INTERESSE
    )
    
    total_inserido = 0
    for i, chunk in enumerate(df_iter):
        # RF-007: Filtragem Paraíba (CO_UF=25 e NO_UF='Paraíba')
        chunk_filtrado = chunk[(chunk['CO_UF'] == 25) & (chunk['NO_UF'] == 'Paraíba')]
        
        if not chunk_filtrado.empty:
            # RF-009: Inserção incremental com tratamento de erro
            try:
                chunk_filtrado.to_sql(TABLE_NAME, engine, if_exists='append', index=False)
                total_inserido += len(chunk_filtrado)
                logger.info(f"Bloco {i}: {len(chunk_filtrado)} registros inseridos.")
            except Exception as e:
                logger.error(f"Erro ao inserir bloco {i}: {e}")
                raise # Propaga para o lambda_handler tratar via SQS
    
    logger.info(f"Carga de {file_key} finalizada. Total: {total_inserido} registros.")

def lambda_handler(event, context):
    """Handler para gatilho SQS."""
    batch_item_failures = []
    
    for record in event['Records']:
        try:
            message_body = json.loads(record['body'])
            bucket = message_body['Records'][0]['s3']['bucket']['name']
            key = message_body['Records'][0]['s3']['object']['key']
            
            process_csv_from_s3(bucket, key)
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem {record['messageId']}: {e}")
            batch_item_failures.append({"itemIdentifier": record['messageId']})
            
    return {"batchItemFailures": batch_item_failures}
