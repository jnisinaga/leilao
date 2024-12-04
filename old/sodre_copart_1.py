import time
import csv
import smtplib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tabulate import tabulate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configura o WebDriver do Safari
options = webdriver.SafariOptions()
driver = webdriver.Safari(options=options)

# Função para enviar o e-mail
def send_email(subject, body, to_email):
    from_email = "jnisinaga@gmail.com"
    password = "fyvx uqdm ojax ukfb"

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()
    print("E-mail enviado com sucesso!")

# Função para extrair dados do Sodré Santoro
def get_motos_from_sodre(page_number=1):
    base_url = "https://www.sodresantoro.com.br/veiculos/lotes?lot_category=motos&order=0&page="
    all_motos_data = []
    while True:
        url = base_url + str(page_number)
        driver.get(url)
        wait = WebDriverWait(driver, 20)

        try:
            nomes = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "w-full")]/a/h2')))
            lances = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "w-full")]/a/p[2]')))
            anos = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "w-full")]/a/div/div[1]/p/span')))
            locais = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@id, "card-")]/div/div[5]/a/div/div[3]/p/span')))
            links = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@id, "card-")]/div/div[1]/div[1]/div[1]/div[1]/a')))

            if not nomes:
                break

            for nome, lance, ano, local, link in zip(nomes, lances, anos, locais, links):
                all_motos_data.append([nome.text, lance.text, ano.text, local.text, link.get_attribute('href')])
            page_number += 1
            time.sleep(2)
        except Exception as e:
            print(f"Erro: {e}")
            break

    return all_motos_data

# Função para extrair dados do Copart
def get_data_from_copart(url, retries=2):
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

            for nome, lance, ano, local, link in zip(nomes, lances, anos, locais, links):
                data_list.append([nome.text, lance.text, ano.text, local.text, link.get_attribute('href')])
            return data_list
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(5)

    return data_list

# Coletar dados de Sodré Santoro
all_motos_data = get_motos_from_sodre()

# Coletar dados do Copart
copart_url = "https://www.copart.com.br/lotSearchResults/?free=true&query=harley"
copart_data = get_data_from_copart(copart_url)

# Consolidar dados
all_data = all_motos_data + copart_data

# Salvar dados em CSV
csv_filename = "motos_compiladas.csv"
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Nome", "Lance", "Ano", "Local", "Link"])
    writer.writerows(all_data)

# Enviar por e-mail
if all_data:
    table_data = tabulate(all_data, headers=["Nome", "Lance", "Ano", "Local", "Link"], tablefmt="html")
    body = f"<p>Abaixo estão todas as motos Harley Davidson encontradas:</p>{table_data}"
    send_email("Motos Harley Davidson (Copart e Sodré Santoro)", body, "j.nisi@proton.me")

# Fechar o navegador
driver.quit()
