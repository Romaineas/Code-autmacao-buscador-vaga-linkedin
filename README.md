# Requisitos uso dos códigos

* Pessoal esses arquivos serão atualizados sempre que possivel pora debugar os codigos de erros e fugir das atualizações da HTML do linkedin

- Instale as dependências: pip install selenium pandas webdriver-manager
- Baixe o ChromeDriver automaticamente via webdriver-manager (não precisa baixar manualmente).
- Substitua SEU_EMAIL e SUA_SENHA pelas suas credenciais do LinkedIn (use com cuidado!).
- Rode o script em um ambiente local, não em servidores.

Script Python Ajustado
Aqui vai o código completo. Ele roda no Chrome, faz login, busca as vagas e salva em vagas_linkedin.csv. Ajustei para buscar as duas áreas que você mencionou, limitando a 10 resultados por busca para evitar detecção.
