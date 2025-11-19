# Instalação do ambiente virtual

- Navegar até o diretório do projeto
- Executar o comando: python3 -m venv venv
    - Isso criará um ambiente virtual no diretório.
- Para ativar o venv execute: source venv/bin/activate
    - Isso deve fazer aparecer (venv) no terminal
- Com o venv ativado execute: pip install -r req.txt
    - Isso deve instalar as dependências do projeto no ambiente virtual e manter o seu ambiente global protegido de qualquer dependência que possa danificar sua instalação do python.

# Ambiente virtual instalado

Com as instalações finalizadas execute: streamlit run app.py

- Isso deve criar um servidor local no seu computador, para interagir com a aplicação abra no navegador o link que irá aparecer no seu terminal. (localhost:8000) o número pode ser outro.

- Monitore a aplicação pelo terminal ou pela própria interface.
