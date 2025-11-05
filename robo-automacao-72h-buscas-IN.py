#!/usr/bin/env python
# coding: utf-8

# In[3]:


get_ipython().system('pip install selenium pandas webdriver-manager')


# In[4]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os


# In[18]:


# SUAS BUSCAS
BUSCAS = [
    "Analista Dados",
    "Analista BI",
    "Data Analyst"
]

# ==================== FUNÇÃO SETUP DRIVER ====================
def setup_driver():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => false});")
    driver.maximize_window()
    return driver

# ==================== FUNÇÃO LOGIN ====================
def login(driver):
    driver.get("https://www.linkedin.com/login")
    wait = WebDriverWait(driver, 15)
    
    # SUBSTITUA AQUI SEUS DADOS
    email_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
    email_input.send_keys("bsrol@gmail.com")  # ← COLOQUE SEU EMAIL
    
    senha_input = driver.find_element(By.ID, "password")
    senha_input.send_keys("88888888")  # ← COLOQUE SUA SENHA
    
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()
    
    time.sleep(6)
    print("✅ Login feito com sucesso!")


# In[16]:


# ==================== FUNÇÃO BUSCA (3 DIAS) ====================
def buscar_vagas_72h_completo(driver, termo_busca):
    termo_encoded = termo_busca.replace(' ', '%20')
    termo_lower = termo_busca.lower()
    
    url = f"https://www.linkedin.com/jobs/search/?keywords={termo_encoded}&location=Brasil&f_TPR=r259200&sortBy=DD"
    
    print(f"\n🔍 Acessando (3 dias): {termo_busca}")
    driver.get(url)
    time.sleep(8)
    
    # Cookies
    try:
        driver.find_element(By.XPATH, "//button[contains(text(), 'Aceitar')]").click()
        time.sleep(2)
    except:
        pass

    # Rolar
    print("📜 Rolando para carregar vagas...")
    for i in range(25):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(2)

    # PRINT
    driver.save_screenshot(f"vagas_3dias_{termo_busca.replace(' ', '_')}.png")

    # PEGAR VAGAS COM JS
    print("⚡ Extraindo vagas...")
    js_code = """
    const jobs = [];
    document.querySelectorAll('a').forEach(a => {
        const href = a.href;
        if (href && href.includes('linkedin.com/jobs/view/')) {
            const card = a.closest('[data-job-id]') || a.closest('li') || a.closest('div');
            if (card) {
                const title = (card.querySelector('h3, .job-search-card__title') || {}).innerText || '';
                const company = (card.querySelector('h4 a, .base-search-card__subtitle') || {}).innerText || 'Não informado';
                jobs.push({
                    link: href.split('?')[0],
                    title: title.trim(),
                    company: company.trim()
                });
            }
        }
    });
    return jobs.filter((v, i, a) => a.findIndex(x => x.link === v.link) === i);
    """
    vagas = driver.execute_script(js_code)
    
    # FILTRAR POR TÍTULO
    filtradas = []
    for v in vagas:
        if termo_lower in v['title'].lower():
            filtradas.append(v)
            print(f"   ✅ APROVADA: {v['title'][:65]} | {v['company']}")
        else:
            print(f"   ❌ Ignorada: {v['title'][:65]}")

    print(f"📊 {len(filtradas)} VAGAS RELEVANTES ENCONTRADAS!\n")
    
    # SALVAR
    nome = termo_busca.replace(' ', '_')
    if filtradas:
        df = pd.DataFrame(filtradas)[['title', 'company', 'link']]
        df.columns = ['Título', 'Empresa', 'Link']
        df.to_csv(f"VAGAS_3DIAS_{nome}.csv", index=False, encoding="utf-8")
        
        header = not os.path.exists('TODAS_VAGAS_3DIAS.csv')
        df.to_csv('TODAS_VAGAS_3DIAS.csv', mode='a', header=header, index=False, encoding="utf-8")
    
    return filtradas


# In[17]:


# ==================== EXECUÇÃO PRINCIPAL ====================
print("🚀 INICIANDO BUSCA: VAGAS DOS ÚLTIMOS 3 DIAS (BRASIL)")
driver = setup_driver()
try:
    login(driver)
    
    todas_vagas = []
    for busca in BUSCAS:
        print(f"\n{'='*80}")
        print(f"🔎 BUSCANDO: '{busca}'")
        vagas = buscar_vagas_72h_completo(driver, busca)
        todas_vagas.extend(vagas)
        time.sleep(8)
    
    # RESUMO FINAL
    if todas_vagas:
        df_final = pd.DataFrame(todas_vagas)[['title', 'company', 'link']].drop_duplicates()
        df_final.columns = ['Título', 'Empresa', 'Link']
        df_final.to_csv("RESUMO_3DIAS.csv", index=False, encoding="utf-8")
        print(f"\n🎉 RESUMO DOS 3 DIAS: {len(df_final)} VAGAS ÚNICAS!")
        print(f"📁 Arquivos salvos:")
        print(f"   - RESUMO_3DIAS.csv")
        print(f"   - TODAS_VAGAS_3DIAS.csv (acumula todo dia)")
        print(f"   - VAGAS_3DIAS_*.csv (por busca)")
        display(df_final.head(10))
    else:
        print("😞 Nenhuma vaga encontrada hoje. Tente amanhã!")

finally:
    driver.quit()
    print("✅ Automação finalizada!")

