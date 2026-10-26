#---------------------------------------------------------------------
# 1. Library Imports 
#---------------------------------------------------------------------
import os 
import zipfile
import pandas as pd

from ftplib import FTP
from dotenv import load_dotenv

#---------------------------------------------------------------------
# 2. Configuration
#---------------------------------------------------------------------
load_dotenv(override=True)


#---------------------------------------------------------------------
# 3. Conection and Directory Listing Functions
#---------------------------------------------------------------------

FTP_HOST = os.getenv("FTP_HOST")
FTP_DATA_DIR = os.getenv("FTP_DATA_DIR")
FTP_DOCS_DIR = os.getenv("FTP_DOCS_DIR")
LOCAL_DIR = os.getenv("LOCAL_DIR")


os.makedirs(LOCAL_DIR, exist_ok=True)

def download_ftp_file(
    ftp: FTP,
    remote_filename: str,
    local_path: str,
):
    
    total_size = ftp.size(remote_filename) or 0
    bytes_downloaded = 0
    
    print (f"Starting download of {remote_filename} to {local_path} ({total_size / (1024**2):.2f} MB)")
    
    with open(local_path, "wb") as f:
        def callback(chunk):
            nonlocal bytes_downloaded
            f.write(chunk)
            bytes_downloaded += len(chunk)
            if total_size > 0:
                percent = (bytes_downloaded / total_size) * 100
                print (f"\rProgress: {percent:.1f}%", end="", flush=True)
        
        ftp.retrbinary(F"RETR {remote_filename}", callback, blocksize=65536)
    print (f"\nDownload of {remote_filename} completed.")

#---------------------------------------------------------------------
# 4. FTP Connection and Setup
#---------------------------------------------------------------------
print (f"Connecting to FTP server at {FTP_HOST}...")
ftp = FTP(FTP_HOST)
ftp.login() #Anonymous login
ftp.set_pasv(True) #Essential for local/VPN connection

#---------------------------------------------------------------------
# 5. Download ZIP Files from FTP
#---------------------------------------------------------------------
ftp.cwd(FTP_DATA_DIR)
data_files = ftp.nlst()
zip_files = [f for f in data_files if f.endswith(".zip")][0]  # Get the first zip file
local_zip_path = os.path.join(LOCAL_DIR, zip_files) # Local path to save the downloaded zip file

if not os.path.exists(local_zip_path):
    download_ftp_file(ftp, zip_files, local_zip_path)
else:
    print(f"File {local_zip_path} already exists locally.")
    

#---------------------------------------------------------------------
# 6. Download ZIP Files from FTP Docs Directory
#---------------------------------------------------------------------
ftp.cwd(FTP_DOCS_DIR)
docs_files = ftp.nlst()
zip_docs_files = [f for f in docs_files if f.endswith(".zip")][0]  # Get the first zip file
local_zip_doc_path = os.path.join(LOCAL_DIR, zip_docs_files) # Local path to save the downloaded zip file

if not os.path.exists(local_zip_doc_path):
    download_ftp_file(ftp, zip_docs_files, local_zip_doc_path)
else:
    print(f"File {local_zip_doc_path} already exists locally.")

ftp.quit()

#---------------------------------------------------------------------
# 7. Extract ZIP File Contents
#---------------------------------------------------------------------
print("Initializing extraction of zip file contents")
with zipfile.ZipFile(local_zip_path, 'r') as z:
    z.extractall(LOCAL_DIR)
    data_files = [name for name in z.namelist() if name.lower().endswith((".txt", ".csv"))]
    if not data_files:
        raise FileNotFoundError("No data files (.txt or .csv) found in the ZIP archive.")
    data_file_name = data_files[0]  # Get the first data file
    print(f"Extracted data file: {data_file_name}")
    txt_path = os.path.join(LOCAL_DIR, data_file_name)
    
doc_extract_dir = os.path.join(LOCAL_DIR, "documentacao")
with zipfile.ZipFile(local_zip_doc_path, 'r') as z:
    z.extractall(doc_extract_dir)
    dictionary_files = [name for name in z.namelist() if name.lower().endswith((".xls", ".xlsx"))]
    if dictionary_files:
        dictionary_file_name = dictionary_files[0]  # Get the first dictionary file
        print(f"Extracted dictionary file: {dictionary_file_name}")
    else:
        raise FileNotFoundError("No dictionary files (.xls or .xlsx) found in the ZIP archive.")
    dict_path = os.path.join(doc_extract_dir, dictionary_file_name)

data_file_path = os.path.join(LOCAL_DIR, data_file_name)


#---------------------------------------------------------------------
# 8. Data of interest
#---------------------------------------------------------------------
# V0001 - UF
# V0024 - ESTRATO
# V0020 - ANO DE REFERÊNCIA
# V0026 - TIPO DE SITUAÇÃO CENSITÁRIA
# C006 - SEXO
# C00701 - DIA DO NASCIMENTO
# C00702 - MÊS DO NASCIMENTO
# C00703 - ANO DO NASCIMENTO
# C008 - IDADE DO MORADOR NA DATA DE REFERÊNCIA
# C009 - COR OU RAÇA
# C01001 - CÔNJUGUE OU COMPANHEIRO(A) MORA NESSE DOMICILIO
# C014 - NATUREZA DA UNIÃO
# D00901 - GRAU DE ESCOLARIDADE

#----ESTILO DE VIDA----
# P00102 - SABE SEU PESO?
# P00103 - PESO INFORMADO EM KG (3 INTEIROS E 1 CASA DECIMAL)
# P00104 - PESO FINAL EM KG (3 INTEIROS E 1 CASA DECIMAL)
# P00402 - SABE SUA ALTURA?
# P00403 - ALTURA INFORMADA EM CM (3 INTEIROS)
# P00404 - ALTURA FINAL EM CM (3 INTEIROS)

#----GRAVIDEZ----
# P005 - ESTÁ GRÁVIDA NO MOMENTO?

#----PERCEPÇÃO DO ESTADO DE SAÚDE----
# N001 - EM GERAL, COMO AVALIA SEU ESTADO DE SAÚDE?
# N00101 - CONSIDERANDO SAÚDE COMO UM ESTADO DE BEM-ESTAR FISICO E MENTAL, E NÃO SOMENTE AUSÊNCIA DE DOENÇAS, COMO AVALIA SEU ESTADO DE SAÚDE?
# N004 - QUANDO SOBRE UM LADEIRA, UM LANCE DE ESCADA OU CAMINHA RAPIDO, SENTE DOR OU DESCONFORTO NO PEITO?
# N005 - QUANDO CAMINHA EM LUGAR PLANO EM VELOCIDADE NORMAL, SENTE DOR OU DESCONFORTO NO PEITO?
# N006 - O QUE FAZ CASO SINTA DOR OU DESCONFORTO NO PEITO DURANTE A ATIVIDADE?
# N007 - QUANDO PARA, O QUE ACONTECE COM A DOR OU DESCONFORTO NO PEITO?
# N008 - ONDE GERALMENTE SENTE ESSA DOR OU DESCONFORTO NO PEITO?
# N010 - NAS ULTIMAS DUAS SEMANAS, COM QUE FREQUÊNCIA TTEVE PROBLEMAS DE SONO, COMO DIFICULDADE PARA ADORMECER, ACORDAR FREQUENTEMENTE A NOITE OU DORMIR MAIS DO QUE DE COSTUME?
# N011 - NAS DUAS ULTIMAS SEMANAS, COM QUE FREQUENCIA TEVE PROBLEMAS POR NÃO SE SENTIR DESCANSADO(A) E DISPOSTO(A) DURANTE O DIA, SENTINDO-SE CANSADO(A), SEM TER ENERGIA?
# N012 - NAS DUAS ULTIMAS SEMANAS, COM QUE FREQUÊNCIA TEVE POUCO INTERESSE OU NÃO SENTIU PRAZER EM FAZER AS COISAS?
# N013 - NAS DUAS ULTIMAS SEMANAS, COM QUE FREQUÊNCIA TEVE PROBLEMAS PARA SE CONCENTRAR NAS SUAS ATIVIDADES HABITUAIS?
# N014 - NAS DUAS ULTIMAS SEMANAS, COM QUE FREQUENCIA TEVE PROBLEMAS NA ALIMENTAÇÃO, COMO TER FALTA DE APETITE OU COMER MUITIO MAIS DO QUE DE COSTUME?
# N015 - NAS DUAS ULTIMAS SEMANAS, COM QUE FREQUENCIA TEVE LENTIDAO PARA SE MOVIMENTAR OU FALAR, OU AO CONTRÁRIO, FICOU MUITO AGITADO(A) OU INQUIETO(A)
# N016 - NAS DUAS ULTIMAS SEMANAS, COM QUE FREQUENCIA SENTIU DEPRIMIDO(A), "PARA BAIXO" OU SEM PERSPECTIVA?
# N017 - NAS DUAS ULTIMAS SEMANAS, COM QUE FREQUENCIA SENTIU MAL CONSIGO MESMO, SE ACHANDO UM FRACASSO OU ACHANDO QUE DECEPCIONOU SUA FAMILIA?
# N018 - NAS DUAS ULTIMAS SEMANAS, COM QUE FREQUENCIA PENSOU EM SE FERIR DE ALGUMA MANEIRA OU ACHOU QUE SERIA MELHOR ESTAR MORTO?

data_of_interest = [
    # ---- DESENHO AMOSTRAL (OBRIGATÓRIO) ----
    "V0001",    # UF
    "V0024",    # Estrato
    "UPA_PNS",  # Unidade Primária de Amostragem (Faltava)
    "V0028",    # Peso do morador selecionado s/ calibração (Faltava)
    "V00281",   # Peso do morador selecionado c/ calibração (Faltava)
    "V0020",    # Ano de referência
    "V0026",    # Tipo de situação censitária (Urbano/Rural)

    # ---- DEMOGRÁFICAS E SOCIOECONÔMICAS ----
    "C006",     # Sexo (1 = Homem, 2 = Mulher)
    "C00701",   # Dia nascimento
    "C00702",   # Mês nascimento
    "C00703",   # Ano nascimento
    "C008",     # Idade na data de referência
    "C009",     # Cor ou raça
    "C01001",   # Cônjuge mora no domicílio
    "C014",     # Natureza da união
    "D00901",   # Escolaridade padronizada

    # ---- ANTROPOMETRIA / ESTILO DE VIDA (MORADOR SELECIONADO) ----
    "P00102",   # Sabe seu peso?
    "P00103",   # Peso informado (kg)
    "P00104",   # Peso final (kg)
    "P00402",   # Sabe sua altura?
    "P00403",   # Altura informada (cm)
    "P00404",   # Altura final (cm)
    "P005",     # Está grávida no momento?

    # ---- SAÚDE DA MULHER (CENÁRIO 1: MENOPAUSA) ----
    "R044",     # Histerectomia (Faltava)
    "R045",     # Ooforectomia (Faltava)
    "R046",     # Idade da última menstruação / menopausa (Faltava)

    # ---- PERCEPÇÃO DE SAÚDE, ANGINA E PHQ-9 (DEPRESSÃO) ----
    "N001",     # Autoavaliação de saúde geral
    "N00101",   # Autoavaliação de bem-estar biopsicossocial
    "N004", "N005", "N006", "N007", "N008", # Angina de peito (Rose)
    "N010", "N011", "N012", "N013", "N014", 
    "N015", "N016", "N017", "N018"          # Rastreio PHQ-9
]

print("loading data of interest...")
df = pd.read_csv(
    data_file_path,
    sep=" ",
    usecols=lambda col: col in data_of_interest,
    low_memory=False
)

print("data of interest loaded.")
print(f"Number of rows loaded: {len(df)}")
print(f"Number of columns loaded: {len(df.columns)}")