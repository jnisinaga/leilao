import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configura o WebDriver do Safari
options = webdriver.SafariOptions()
driver = webdriver.Safari(options=options)

# Função para extrair as motos de uma página
def get_motos_from_page(url, retries=3):
    driver.get(url)
    
    # Espera explícita para garantir que o conteúdo tenha carregado
    wait = WebDriverWait(driver, 30)
    
    for attempt in range(retries):
        try:
            # Tentativa de localizar os elementos
            elementos = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "w-full")]/a/h2')))
            
            # Verifica se a lista de motos está vazia
            if not elementos:
                print("Nenhuma moto encontrada na página. Finalizando a busca.")
                return False  # Retorna False para indicar que não há motos na página
            
            # Extraindo e imprimindo os nomes das motos
            for elemento in elementos:
                print(elemento.text)
            
            return True  # Retorna True se encontrou motos

        except Exception as e:
            print(f"Erro ao buscar motos: {e}")
            # Se falhar, tenta novamente após um pequeno intervalo
            print(f"Tentando novamente... ({attempt + 1}/{retries})")
            time.sleep(2)  # Espera antes de tentar novamente

    return False  # Se todas as tentativas falharem, retorna False

# URL base com a paginação
base_url = "https://www.sodresantoro.com.br/veiculos/lotes?lot_category=motos&order=0&page="

# Iterar pelas páginas, começando da 1
page_number = 1
while True:
    url = base_url + str(page_number)
    print(f"Buscando motos na página {page_number}...")
    
    # Chama a função para buscar motos e verifica se encontrou motos
    if not get_motos_from_page(url):
        break  # Encerra o loop se não houver motos
    
    # Incrementa o número da página para a próxima
    page_number += 1
    time.sleep(2)  # Intervalo entre as requisições para dar tempo ao carregamento

# Fechar o driver após o processo
driver.quit()
