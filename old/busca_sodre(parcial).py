from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configura o WebDriver do Safari
options = webdriver.SafariOptions()
driver = webdriver.Safari(options=options)

# Função para extrair as motos de uma página
def get_motos_from_page(url):
    driver.get(url)
    
    # Espera explícita para garantir que o conteúdo tenha carregado
    wait = WebDriverWait(driver, 30)
    try:
        # Alterei o XPath conforme a sua sugestão, que captura os nomes das motos
        elementos = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "w-full")]/a/h2')))
        
        # Extraindo e imprimindo os nomes das motos
        for elemento in elementos:
            print(elemento.text)
    except Exception as e:
        print("Erro ao buscar motos:", e)

# URL base com a paginação
base_url = "https://www.sodresantoro.com.br/veiculos/lotes?lot_category=motos&order=0&page="

# Iterar pelas páginas, começando da 1
for page_number in range(1, 10):  # Ajuste o número final conforme o número total de páginas
    url = base_url + str(page_number)
    print(f"Buscando motos na página {page_number}...")
    get_motos_from_page(url)

# Fechar o driver após o processo
driver.quit()
