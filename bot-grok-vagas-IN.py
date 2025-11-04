#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip install selenium pandas webdriver-manager')


# In[2]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time


# In[55]:


EMAIL = "mailbox@gmail.com"      # ← MUDE AQUI
SENHA = "*******"    # ← MUDE AQUI
BUSCAS = [
    "Analista de dados",
    "Analista de BI"
   
    
 ]
NUM_VAGAS_POR_BUSCA = 7


# In[53]:


from selenium.webdriver.common.keys import Keys
import time

def buscar_vagas_24h_com_filtro_titulo(driver, termo_busca):
    termo_encoded = termo_busca.replace(' ', '%20')
    termo_lower = termo_busca.lower()  # Para comparação
    
    url = f"https://www.linkedin.com/jobs/search/?keywords={termo_encoded}&location=Brasil&f_TPR=r86400&sortBy=DD"
    
    print(f"\nAcessando (24h): {url}")
    driver.get(url)
    time.sleep(8)
    
    # Aceitar cookies
    try:
        driver.find_element(By.XPATH, "//button[contains(text(), 'Aceitar') or contains(text(), 'Accept')]").click()
        time.sleep(2)
    except:
        print("Cookies ignorados.")

    # Rolar até o fim
    print("Rolando para carregar vagas...")
    for i in range(20):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(2.2)

    # PRINT E HTML
    screenshot = f"vagas_24h_{termo_busca.replace(' ', '_')}.png"
    driver.save_screenshot(screenshot)
    print(f"PRINT → {screenshot}")

    html_file = f"html_24h_{termo_busca.replace(' ', '_')}.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"HTML → {html_file}")

    # PEGAR TODOS OS LINKS + TÍTULOS COM JAVASCRIPT
    print("Extraindo títulos e links...")
    js_code = """
    return Array.from(document.querySelectorAll('a'))
        .map(a => ({
            href: a.href,
            title: a.innerText.trim()
        }))
        .filter(item => item.href && item.href.includes('linkedin.com/jobs/view/'))
        .map(item => ({
            link: item.href.split('?')[0],
            title: item.title
        }))
        .filter((v, i, a) => a.findIndex(x => x.link === v.link) === i);
    """
    resultados = driver.execute_script(js_code)
    
    # FILTRAR SÓ VAGAS COM O TERMO NO TÍTULO
    vagas_filtradas = []
    for item in resultados:
        titulo = item['title'].lower()
        if termo_lower in titulo:
            vagas_filtradas.append(item['link'])
            print(f"   APROVADA: {item['title'][:60]}...")
        else:
            print(f"   IGNORADA: {item['title'][:60]}...")

    print(f"\nENCONTRADAS {len(vagas_filtradas)} VAGAS COM '{termo_busca}' NO TÍTULO!")

    # SALVAR
    txt_file = f"LINKS_24H_FILTRADO_{termo_busca.replace(' ', '_')}.txt"
    csv_file = f"LINKS_24H_FILTRADO_{termo_busca.replace(' ', '_')}.csv"
    
    with open(txt_file, "w", encoding="utf-8") as f:
        for link in vagas_filtradas:
            f.write(link + "\n")
    
    pd.DataFrame(vagas_filtradas, columns=["Link da Vaga"]).to_csv(csv_file, index=False, encoding="utf-8")
    
    print(f"LINKS FILTRADOS SALVOS → {txt_file} | {csv_file}\n")
    
    return vagas_filtradas


# In[54]:


driver = setup_driver()

try:
    print("INICIANDO BUSCA: VAGAS 24H COM TÍTULO EXATO (BRASIL)")
    login(driver)
    
    todos_links_filtrados = []
    
    for busca in BUSCAS:
        print(f"{'='*90}")
        print(f"BUSCANDO: '{busca}' (só no título)")
        links = buscar_vagas_24h_com_filtro_titulo(driver, busca)
        todos_links_filtrados.extend(links)
        time.sleep(8)
    
    # SALVAR TUDO
    if todos_links_filtrados:
        unique = list(set(todos_links_filtrados))
        arquivo_final = "VAGAS_24H_FILTRADAS_BRASIL.txt"
        csv_final = "VAGAS_24H_FILTRADAS_BRASIL.csv"
        
        with open(arquivo_final, "w", encoding="utf-8") as f:
            for l in unique:
                f.write(l + "\n")
        
        pd.DataFrame(unique, columns=["Link da Vaga"]).to_csv(csv_final, index=False, encoding="utf-8")
        
        print(f"\nSUCESSO! {len(unique)} VAGAS RELEVANTES SALVAS!")
        print(f"→ {arquivo_final}")
        display(pd.DataFrame(unique, columns=["Link da Vaga"]).head(10))
    else:
        print("Nenhuma vaga com título exato. Tente termos mais amplos.")

finally:
    driver.quit()


# In[ ]:




