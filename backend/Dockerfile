# Usando a imagem base oficial do Lambda para Python 3.13
FROM public.ecr.aws/lambda/python:3.13

# Instalar dependências de build (gcc e postgresql-devel são necessários para psycopg2-binary compilar se necessário, embora o pacote binário ajude)
RUN dnf install -y gcc postgresql-devel

# Copiar arquivo de dependências
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

# Copiar o código do Lambda
COPY read_csv.py ./

# Definir o handler para a função Lambda
CMD ["read_csv.lambda_handler"]