import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tabulate import tabulate

# Configura o WebDriver do Safari
options = webdriver.SafariOptions()
driver = webdriver.Safari(options=options)

# Função para extrair os dados de uma página
def get_data_from_page(url, retries=2):
    driver.get(url)
    wait = WebDriverWait(driver, 20)
    data_list = []

    for attempt in range(retries):
        try:
            nomes = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="serverSideDataTable"]/tbody/tr/td[6]/span')))
            lances = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="serverSideDataTable"]/tbody/tr/td[15]/ul/li/ul/li[1]/span[2]')))
            anos = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="serverSideDataTable"]/tbody/tr/td[4]/span[1]')))
            locais = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="serverSideDataTable"]/tbody/tr/td[11]/a/span')))
            links = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="serverSideDataTable"]/tbody/tr/td[3]/div/a')))

            if not nomes or not lances or not anos or not locais or not links:
                print("Nenhum dado encontrado na página.")
                return False

            for nome, lance, ano, local, link in zip(nomes, lances, anos, locais, links):
                data_list.append([nome.text, lance.text, ano.text, local.text, link.get_attribute('href')])

            return data_list

        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(5)

    return False

# Cabeçalho da tabela
headers = ["Nome", "Lance", "Ano", "Local", "Link"]

# URL base (busca por Harley no Copart)
base_url = "https://www.copart.com.br/lotSearchResults/?free=true&query=harley"

# Executar a busca
all_data = get_data_from_page(base_url)
if all_data:
    print("\nDados encontrados:")
    print(tabulate(all_data, headers=headers, tablefmt="grid"))

    # Salvar os dados em um arquivo CSV
    csv_filename = "motos_copart.csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # Escrever cabeçalho
        writer.writerows(all_data)  # Escrever dados

    print(f"\nDados salvos no arquivo {csv_filename}")

# Fechar o driver após o processo
driver.quit()
