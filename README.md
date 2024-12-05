
# Gerador de Trilhas de Formação

Este projeto é uma aplicação web interativa construída com [Streamlit](https://streamlit.io/), que ajuda a gerar trilhas de formação personalizadas a partir de um currículo e uma descrição de vaga. A aplicação utiliza a API da OpenAI para criar planos de treinamento detalhados e os converte em diagramas hierárquicos no estilo BPMN com Mermaid.js.

---

## Funcionalidades

- **Extração de Texto**: Extrai conteúdo textual de arquivos PDF.
- **Plano de Treinamento**: Gera um plano detalhado de desenvolvimento de competências usando a API da OpenAI.
- **Trilhas de Aprendizagem**: Cria uma lista de cursos ou certificações sugeridas com base no plano de desenvolvimento.
- **Diagramas Hierárquicos**: Exibe visualmente as trilhas de formação em formato de diagrama Mermaid.js.

---

## Requisitos

- **Python 3.7 ou superior**
- **Bibliotecas Python**:
  - `streamlit`
  - `openai`
  - `PyPDF2`
  - `python-dotenv`
  - `re`
- **Conta na OpenAI**: Necessária para acessar a API.

---

## Instalação

### 1. Clone o Repositório
```bash
git clone https://github.com/arnottrcaiado/ueup-streamlit.git
cd ueup-streamlit
```

### 2. Configure o Ambiente Virtual
```bash
python -m venv venv
source venv/bin/activate  # Para Windows: venv\Scripts\activate
```

### 3. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 4. Configure a API da OpenAI
Crie um arquivo `.env` no diretório raiz com sua chave de API:
```plaintext
OPENAI_API_KEY=sua_chave_api_aqui
```

---

## Execução

1. Certifique-se de que o ambiente virtual está ativado.
2. Execute o seguinte comando:
   ```bash
   streamlit run main.py
   ```
3. Acesse a aplicação no navegador em `http://localhost:8501`.

---

## Estrutura do Código (`main.py`)

### 1. Importação de Bibliotecas
```python
import streamlit as st
import openai
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import os
import re
```
- **`streamlit`**: Framework para criar a interface web.
- **`openai`**: Biblioteca para interagir com a API da OpenAI.
- **`PyPDF2`**: Para extrair texto de arquivos PDF.
- **`dotenv`**: Carrega variáveis de ambiente do arquivo `.env`.
- **`os` e `re`**: Manipulação de sistema e expressões regulares.

---

### 2. Carregamento da Chave da API
```python
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
```
Carrega a chave da API da OpenAI a partir do arquivo `.env`.

---

### 3. Funções Principais

#### **Extração de Texto de PDFs**
```python
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text
```
- Lê o conteúdo de todas as páginas de um PDF.
- Retorna o texto extraído como uma string.

#### **Geração de Plano de Desenvolvimento**
```python
def generate_training_plan(cv_text, job_description, num_steps):
    prompt = f'''
    Gere um plano de desenvolvimento com até {num_steps} passos para preencher lacunas de competências.
    Cada passo deve ser categorizado em até 5 categorias principais.

    Currículo:
    {cv_text}

    Descrição da vaga:
    {job_description}
    '''
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Você é um mentor de carreiras especializado."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response["choices"][0]["message"]["content"]
```
- Cria um plano de treinamento baseado no currículo e descrição da vaga.
- Retorna uma descrição detalhada categorizada.

#### **Geração de Trilhas de Aprendizagem**
```python
def generate_learning_tracks_from_plan(training_plan, num_steps):
    prompt = f'''
    Gere trilhas de aprendizagem no formato Categoria -> Nome do Curso ou Certificação.

    Plano de Desenvolvimento:
    {training_plan}
    '''
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um mentor especializado."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response["choices"][0]["message"]["content"]
```
- Converte o plano de desenvolvimento em trilhas de aprendizagem no formato hierárquico.

#### **Criação de Diagramas com Mermaid.js**
```python
def create_mermaid_diagram(processed_list):
    mermaid_code = "graph TD
"
    for line in processed_list:
        mermaid_code += f"    {line}
"
    return mermaid_code
```
- Gera código Mermaid.js para exibir as trilhas em um diagrama visual.

---

### 4. Interface com Streamlit
#### Entrada de Dados
```python
cv_input_method = st.radio("Escolha como fornecer o currículo:", ("Upload de PDF", "Colar texto manualmente"))
```
- Permite ao usuário enviar um arquivo PDF ou colar o texto manualmente.

#### Geração de Resultados
```python
if st.button("Gerar Trilha de Formação"):
    training_plan = generate_training_plan(cv_text, job_description, num_steps)
    st.text(training_plan)
```
- Processa o currículo e descrição da vaga, gerando trilhas detalhadas.

#### Exibição de Diagrama
```python
st.components.v1.html(
    f'''
    <div class="mermaid">
    {mermaid_code}
    </div>
    ''',
    height=800,
)
```
- Renderiza o diagrama hierárquico diretamente no navegador.

---

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

---

*Este README fornece um guia completo para configurar e entender a aplicação.* 😊
