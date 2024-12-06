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
    Você é um mentor de carreiras especializado em tecnologia e desenvolvimento profissional. 
    Por favor, crie um plano de desenvolvimento com até {num_steps} passos para que o candidato preencha lacunas de competências.

    **Instruções específicas:**
    1. Cada passo deve ser categorizado em até 5 categorias principais de competências.
    2. Para cada categoria, liste etapas claras e objetivas necessárias para o progresso.
    3. Certifique-se de que o plano seja relevante para as informações fornecidas.
    4. Não inclua sugestões que não sigam princípios éticos, legais ou sejam inconsistentes com o propósito da aplicação.

    Caso encontre incoerências ou informações insuficientes, avise o usuário de forma educada e peça informações adicionais.

    **Informações fornecidas:**
    Currículo:
    {cv_text}

    Descrição da vaga:
    {job_description}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um mentor especializado em carreiras e desenvolvimento profissional."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erro ao gerar o plano: {e}"

# Função para gerar trilhas de aprendizagem na forma de lista compacta
def generate_learning_tracks_from_plan(training_plan, num_steps):
    prompt = f"""
    Com base no plano de desenvolvimento fornecido, gere um diagrama de trilha de aprendizagem.
    **Instruções específicas:**
    1. Deve gerar no formato mermaid
    2. Devem estar alinhada com o plano de desenvolvimento.
    2. Não inclua comentários e ou informações que fujam dos princípios éticos ou legais.
    3. Caso o plano seja insuficiente, forneça uma mensagem solicitando melhorias ou mais detalhes.

    **Plano de Desenvolvimento fornecido:**
    {training_plan}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um mentor especializado em carreiras e desenvolvimento profissional."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erro ao gerar as trilhas: {e}"

# Função para filtrar linhas válidas para Mermaid
def filter_valid_mermaid_lines(learning_tracks):
    valid_lines = []
    for line in learning_tracks.split("\n"):
        if re.match(r"^[A-Za-z]+\[[^\]]+\] --> \|.*\| [A-Za-z]+\[[^\]]+\]$", line.strip()) or \
           re.match(r"^[A-Za-z]+ --> [A-Za-z]+\[[^\]]+\]$", line.strip()) or \
           re.match(r"^[A-Za-z]+\[[^\]]+\] --> [A-Za-z]+\[[^\]]+\]$", line.strip()):
            valid_lines.append(line.strip())
    return valid_lines

# Função para sanitizar linhas para o Mermaid.js
def sanitize_mermaid_lines(lines):
    sanitized_lines = []
    for line in lines:
        line = re.sub(r"\|.*\|", lambda match: match.group(0).replace(" ", "_").replace(".", ""), line)
        sanitized_lines.append(line)
    return sanitized_lines

# Função para criar o diagrama no estilo hierárquico com Mermaid
def create_mermaid_diagram(processed_list):
    mermaid_code = "graph TD\n"
    for line in processed_list:
        mermaid_code += f"    {line}\n"
    return mermaid_code

# Interface com Streamlit
def main():
    st.title("UeUp - Gerador de Trilhas de Formação. 5/12. v1.1")
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
            st.subheader("Diagrama - Trilha / Itinerario")
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