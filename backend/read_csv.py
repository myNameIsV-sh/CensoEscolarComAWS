import pandas as pd
import sqlite3

CSV_FILE_PATH = '.data/microdados_ed_basica_2024.csv'
DB_FILE_PATH = 'microdados_censo_escolar.db'
TABLE_NAME = 'microdados_ed_basica'

COLUNAS_DO_BANCO = [
    'CO_UF',
    'NO_UF',
    'CO_REGIAO',
    'NO_REGIAO',
    'CO_MUNICIPIO',
    'NO_MUNICIPIO',
    'CO_ENTIDADE',
    'NO_ENTIDADE',
    'QT_MAT_BAS',
    'QT_MAT_INF',
    'QT_MAT_FUND',
    'QT_MAT_MED',
    'QT_MAT_PROF',
    'QT_MAT_EJA',
    'QT_MAT_ESP'
]

def load_csv():
    print("Conectando-se ao banco...")
    conn = sqlite3.connect(DB_FILE_PATH)
    print("Realizando a leitura dos dados")
    df = pd.read_csv(CSV_FILE_PATH, sep=';', encoding='latin-1', chunksize=1000, usecols=COLUNAS_DO_BANCO)

    for i, chunk in enumerate(df):
        filtro = (chunk['NO_REGIAO'] == 'Nordeste')
        chunk_filtrado = chunk[filtro]

        if not chunk_filtrado.empty:
            chunk_filtrado.to_sql(TABLE_NAME, conn, if_exists='append', index=False)

    print("Carga finalizada!")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    print('Iniciando a carga dos dados')