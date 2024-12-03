import streamlit as st
import openai
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import os
import re

# Carregar variáveis de ambiente
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Função para extrair texto de um arquivo PDF
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Função para processar informações de requisitos e competências
def generate_training_plan(cv_text, job_description, num_steps):
    prompt = f"""
    Gere um plano de desenvolvimento com até {num_steps} passos para que o candidato preencha as lacunas de competências.
    Cada passo deve ser categorizado em até 5 categorias de competências principais. 
    Responda na forma de categorias, e para cada categoria liste as etapas necessárias.
    Baseie-se nas seguintes informações:
    
    Currículo:
    {cv_text}
    
    Descrição da vaga:
    {job_description}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um mentor de carreiras especializado em tecnologia e desenvolvimento profissional."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response["choices"][0]["message"]["content"]

# Função para gerar trilhas de aprendizagem na forma de lista compacta
def generate_learning_tracks_from_plan(training_plan, num_steps):
    prompt = f"""
    Com base no plano de desenvolvimento abaixo, gere trilhas de aprendizagem com até {num_steps} etapas.
    A saída deve ser no formato:
    Categoria -> Nome do Curso ou Certificação.

    Certifique-se de não incluir explicações adicionais ou comentários. Apenas forneça as instruções no formato válido para Mermaid.js.

    Plano de Desenvolvimento:
    {training_plan}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um mentor de carreiras especializado em tecnologia e desenvolvimento profissional."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response["choices"][0]["message"]["content"]

# Função para filtrar linhas válidas para Mermaid
def filter_valid_mermaid_lines(learning_tracks):
    """
    Filtra apenas as linhas que estão no formato válido para Mermaid.js,
    incluindo linhas com pipes (|label|).
    """
    valid_lines = []
    for line in learning_tracks.split("\n"):
        if re.match(r"^[A-Za-z]+\[[^\]]+\] --> \|.*\| [A-Za-z]+\[[^\]]+\]$", line.strip()) or \
           re.match(r"^[A-Za-z]+ --> [A-Za-z]+\[[^\]]+\]$", line.strip()) or \
           re.match(r"^[A-Za-z]+\[[^\]]+\] --> [A-Za-z]+\[[^\]]+\]$", line.strip()):
            valid_lines.append(line.strip())
    return valid_lines

# Função para sanitizar linhas para o Mermaid.js
def sanitize_mermaid_lines(lines):
    """
    Sanitiza as linhas para o formato correto do Mermaid.js,
    removendo ou ajustando pipes e outros caracteres problemáticos.
    """
    sanitized_lines = []
    for line in lines:
        line = re.sub(r"\|.*\|", lambda match: match.group(0).replace(" ", "_").replace(".", ""), line)
        sanitized_lines.append(line)
    return sanitized_lines

# Função para criar o diagrama no estilo hierárquico com Mermaid
def create_mermaid_diagram(processed_list):
    """
    Cria o código Mermaid para um diagrama hierárquico com categorias e cursos.
    """
    mermaid_code = "graph TD\n"
    for line in processed_list:
        mermaid_code += f"    {line}\n"
    return mermaid_code

# Interface com Streamlit
def main():
    st.title("Gerador de Trilhas de Formação")
    st.write("Envie um currículo e uma descrição de vaga para gerar uma trilha de formação personalizada.")

    # Entrada de Currículo
    st.subheader("Currículo")
    cv_input_method = st.radio("Escolha como fornecer o currículo:", ("Upload de PDF", "Colar texto manualmente"))

    cv_text = ""
    if cv_input_method == "Upload de PDF":
        uploaded_cv = st.file_uploader("Envie o currículo em PDF", type="pdf")
        if uploaded_cv:
            cv_text = extract_text_from_pdf(uploaded_cv)
    elif cv_input_method == "Colar texto manualmente":
        cv_text = st.text_area("Cole o texto do currículo aqui", height=200)

    # Entrada de Descrição da Vaga
    st.subheader("Descrição da Vaga")
    job_input_method = st.radio("Escolha como fornecer a vaga:", ("Upload de PDF", "Colar texto manualmente"))

    job_description = ""
    if job_input_method == "Upload de PDF":
        uploaded_job = st.file_uploader("Envie a descrição da vaga em PDF", type="pdf", key="job_pdf")
        if uploaded_job:
            job_description = extract_text_from_pdf(uploaded_job)
    elif job_input_method == "Colar texto manualmente":
        job_description = st.text_area("Cole o texto da descrição da vaga aqui", height=200, key="job_text_manual")

    # Seleção do número de passos
    num_steps = st.slider("Número de etapas na trilha de formação", min_value=1, max_value=20, value=10)

    # Processar somente após clicar no botão
    if st.button("Gerar Trilha de Formação"):
        if cv_text.strip() and job_description.strip():
            # Obter o plano de treinamento detalhado
            with st.spinner("Gerando plano de treinamento..."):
                training_plan = generate_training_plan(cv_text, job_description, num_steps)
            
            st.subheader("Trilha de Formação (Detalhada)")
            st.text(training_plan)

            # Obter a lista compacta para o diagrama com base no plano detalhado
            with st.spinner("Gerando trilhas de aprendizagem..."):
                learning_tracks = generate_learning_tracks_from_plan(training_plan, num_steps)
                
                # Mostrar os dados brutos gerados
                st.subheader("Trilhas Geradas (Raw)")
                st.text(learning_tracks)

                # Filtrar linhas válidas para o diagrama
                processed_list = filter_valid_mermaid_lines(learning_tracks)
                
                # Sanitizar as linhas para o Mermaid.js
                sanitized_list = sanitize_mermaid_lines(processed_list)

                # Mostrar a lista processada e sanitizada
                st.subheader("Trilhas Processadas")
                st.write(sanitized_list)

            # Gerar e exibir o diagrama
            st.subheader("Diagrama no Estilo BPMN (Responsivo)")
            mermaid_code = create_mermaid_diagram(sanitized_list)
            st.components.v1.html(
                f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                    <script>mermaid.initialize({{ startOnLoad: true }});</script>
                </head>
                <body>
                    <div class="mermaid">
                    {mermaid_code}
                    </div>
                </body>
                </html>
                """,
                height=800,
            )
        else:
            st.error("Por favor, forneça tanto o currículo quanto a descrição da vaga.")

if __name__ == "__main__":
    main()
