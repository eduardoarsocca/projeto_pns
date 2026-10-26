# Projeto PNS

Projeto de exploração dos microdados da Pesquisa Nacional de Saúde (PNS) de
2019, realizada pelo IBGE. O objetivo atual é obter os arquivos de dados e
documentação da pesquisa e preparar uma tabela com variáveis selecionadas para
análises posteriores.

O repositório ainda é um protótipo: a extração e a leitura dos dados estão em
um script com efeitos colaterais de execução e em um notebook. Não há, por
enquanto, uma API de análise, cálculo de indicadores, modelos estatísticos ou
exportação automatizada dos resultados.

## Objetivos e escopo

- Obter os microdados e o dicionário de variáveis da PNS 2019.
- Ler o arquivo de largura fixa usando as posições e os tamanhos informados no
  dicionário.
- Selecionar variáveis relacionadas ao desenho amostral, perfil demográfico e
  socioeconômico, antropometria, saúde da mulher, percepção de saúde, angina e
  sintomas investigados pelo questionário PHQ-9.
- Manter identificadores de estrato, unidade primária de amostragem e pesos
  amostrais, necessários para análises que considerem o desenho da pesquisa.

O projeto apenas seleciona e carrega as colunas. A presença dos pesos e das
variáveis de desenho não significa que o notebook já aplique ponderação ou
calcule estimativas populacionais.

## Arquitetura

```text
Projeto PNS
├── src/projeto_pns/
│   ├── __init__.py          Entrada de console provisória (mensagem de teste)
│   ├── ftp_extraction.py    Download e extração dos arquivos via FTP
│   └── pns.ipynb            Leitura do dicionário e seleção dos microdados
└── dados_pns_2019/
    ├── PNS_2019.txt         Microdados em texto de largura fixa
    └── documentacao/        Dicionário Excel e layouts SAS/texto
```

Há dois fluxos de trabalho relacionados, mas independentes:

1. **Obtenção dos arquivos:** `ftp_extraction.py` conecta-se ao FTP, baixa
   arquivos ZIP e extrai os microdados e a documentação para um diretório local.
2. **Preparação dos dados:** `pns.ipynb` lê o arquivo de texto e o dicionário
   Excel já disponíveis localmente e constrói um `pandas.DataFrame` com as
   variáveis solicitadas.

O notebook não chama o módulo FTP. Os dados existentes em `dados_pns_2019/`
podem ser usados diretamente no notebook, sem executar o download.

## Componentes e funções

### `src/projeto_pns/ftp_extraction.py`

Script de obtenção e extração dos arquivos. Ao ser executado, ele:

1. Carrega as variáveis de ambiente com `python-dotenv`.
2. Abre uma conexão FTP com login anônimo e modo passivo.
3. Procura o primeiro arquivo `.zip` listado no diretório de dados e no
   diretório de documentação configurados.
4. Baixa cada ZIP apenas se o respectivo arquivo local ainda não existir.
   `download_ftp_file` transfere o arquivo em blocos de 64 KiB e exibe o
   progresso quando o servidor informa o tamanho.
5. Extrai o ZIP de dados em `LOCAL_DIR` e o ZIP de documentação em
   `LOCAL_DIR/documentacao`. Procura um arquivo `.txt` ou `.csv` no primeiro e
   um arquivo `.xls` ou `.xlsx` no segundo.
6. Carrega uma seleção de colunas de `data_file_path` com `pandas.read_csv`,
   usando espaço como separador, e informa o número de linhas e colunas.

**Atenção:** a conexão, os downloads, a extração e a leitura de dados são
executados no nível do módulo. Portanto, importar `projeto_pns.ftp_extraction`
também inicia esse fluxo. O script escolhe o primeiro ZIP encontrado, não
valida versões nem checksums e pode precisar de ajustes se o FTP listar
arquivos em outra ordem ou se o formato do arquivo mudar.

A única função definida nesse módulo é:

- `download_ftp_file(ftp, remote_filename, local_path)`: baixa um arquivo
  remoto FTP para o caminho local indicado e imprime o progresso. O restante
  do fluxo está escrito no nível do módulo, não em uma função principal.

### `src/projeto_pns/pns.ipynb`

Notebook de preparação local dos microdados. Ele:

1. Define a lista `data_of_interest` com as variáveis de análise.
2. Localiza o `.xls`/`.xlsx` em `dados_pns_2019/documentacao/`.
3. Identifica a aba e a linha de cabeçalho do dicionário, procurando colunas
   referentes à posição, ao tamanho e ao código da variável.
4. Normaliza os códigos e as posições, filtra as variáveis desejadas e
   converte as posições do layout (base 1) em fatias Python (base 0).
5. Lê `PNS_2019.txt` com codificação `latin1`, extrai cada campo por linha e
   cria um `DataFrame`. Campos vazios são substituídos por `NaN`.
6. Informa quais variáveis não foram localizadas no dicionário e exibe as
   dimensões da tabela carregada.

O notebook mantém os valores lidos como texto; não faz conversão geral de
tipos, limpeza analítica, tratamento estatístico, cálculo de IMC ou pontuação
PHQ-9, nem grava a tabela em outro arquivo. Como lê todas as linhas e mantém os
resultados em memória, o processamento pode consumir bastante memória.

A variável `base_dir` usa o caminho relativo `../../dados_pns_2019`, resolvido
a partir do diretório de trabalho do kernel. Execute o notebook com o
diretório de trabalho em `src/projeto_pns` ou ajuste esse caminho para a
localização do clone. A lista `data_of_interest` e as etapas do notebook são
os pontos atuais para alterar as variáveis ou o processo de leitura.

### `src/projeto_pns/__init__.py`

Define `main()`, chamada pelo comando de console `projeto-pns`. Atualmente,
essa função apenas imprime `Hello from projeto-pns!`; ela não inicia o
download nem executa o notebook.

## Variáveis selecionadas no notebook

| Grupo | Variáveis |
|---|---|
| Desenho amostral e referência | `V0001`, `V0024`, `UPA_PNS`, `V0028`, `V00281`, `V0020`, `V0026` |
| Demográficas e socioeconômicas | `C006`, `C00701`, `C00702`, `C00703`, `C008`, `C009`, `C01001`, `C014`, `D00901` |
| Peso, altura e gravidez | `P00102`, `P00103`, `P00104`, `P00402`, `P00403`, `P00404`, `P005` |
| Saúde da mulher / menopausa | `R044`, `R045`, `R046` |
| Saúde percebida e angina (Rose) | `N001`, `N00101`, `N004`, `N005`, `N006`, `N007`, `N008` |
| Sintomas investigados pelo PHQ-9 | `N010` a `N018` |

A existência de um código na lista não garante que ele esteja presente em
todas as versões do dicionário. O notebook compara os códigos solicitados aos
encontrados e informa os que faltarem.

## Dados

O diretório `dados_pns_2019/` contém os arquivos usados no projeto:

- `PNS_2019.txt`: microdados em texto, com aproximadamente 455 MB.
- `PNS_2019_20220525.zip`: arquivo ZIP dos microdados.
- `Dicionario_e_input_20220530.zip`: pacote ZIP da documentação.
- `documentacao/dicionario_PNS_microdados_2019.xls`: dicionário usado pelo
  notebook para mapear códigos, posições e tamanhos dos campos.
- `documentacao/input_PNS_2019.sas` e `documentacao/input_PNS_2019.txt`:
  arquivos de layout/documentação disponibilizados junto aos dados.

## Requisitos e instalação

- Python `>=3.13` (conforme `pyproject.toml`).
- [uv](https://docs.astral.sh/uv/) para sincronizar o ambiente.

Na raiz do repositório:

```bash
uv sync
```

As dependências declaradas incluem `pandas`, `xlrd`, `python-dotenv` e
`ipykernel`. Para executar o notebook, selecione no Jupyter ou no VS Code o
ambiente `.venv` criado pelo `uv`.

## Como executar

### Processar os microdados locais

1. Confirme que `dados_pns_2019/PNS_2019.txt` e o dicionário Excel estão
   presentes.
2. Abra `src/projeto_pns/pns.ipynb` e selecione o ambiente Python do projeto.
3. Configure o diretório de trabalho do kernel como `src/projeto_pns` e
   execute as células em ordem. Se usar outro diretório de trabalho, atualize
   `base_dir` na célula correspondente.

### Baixar e extrair arquivos via FTP

Configure as seguintes variáveis de ambiente (por exemplo, em um `.env` na
raiz do projeto):

| Variável | Finalidade |
|---|---|
| `FTP_HOST` | Host do servidor FTP |
| `FTP_DATA_DIR` | Diretório remoto dos dados |
| `FTP_DOCS_DIR` | Diretório remoto da documentação |
| `LOCAL_DIR` | Diretório local para os arquivos baixados e extraídos |

Depois execute o módulo a partir da raiz do projeto:

```bash
uv run python -m projeto_pns.ftp_extraction
```

Esse comando inicia uma conexão FTP e pode baixar e extrair arquivos. Não o
execute sem configurar os caminhos correspondentes ao servidor esperado. O
script usa login anônimo, não aceita credenciais por parâmetros e não está
conectado ao comando de console `projeto-pns`.

### Comando de console atual

```bash
uv run projeto-pns
```

Esse comando apenas imprime uma mensagem de teste; não executa o pipeline de dados.

## Dependências principais

| Pacote | Uso no projeto |
|---|---|
| `pandas` | Leitura do dicionário e construção/carregamento de tabelas |
| `xlrd` | Leitura do dicionário Excel `.xls` |
| `python-dotenv` | Carregamento da configuração local do FTP |
| `ipykernel` | Kernel Python para execução do notebook |

O projeto não declara atualmente ferramentas de teste, formatação ou análise estática, e não há uma suíte de testes automatizados configurada.
