import time
import smtplib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tabulate import tabulate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

chromedriver_autoinstaller.install()  # Instala o ChromeDriver automaticamente

# Configurações para Chrome Headless
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Inicializa o WebDriver com Chrome Headless
driver = webdriver.Chrome(options=options)

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
                moto = [nome.text, lance.text, ano.text, local.text, link.get_attribute('href')]
                all_motos_data.append(moto)
                print(tabulate([moto], headers=["Nome", "Lance", "Ano", "Local", "Link"], tablefmt="grid"))

            page_number += 1
            time.sleep(2)
        except Exception as e:
            print(f"Erro: {e}")
            break

    return all_motos_data

# Função para extrair dados da Copart
def get_motos_from_copart():
    base_url = "https://www.copart.com.br/lotSearchResults/?free=true&query=harley"
    driver.get(base_url)
    wait = WebDriverWait(driver, 20)
    all_motos_data = []

    try:
        nomes = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="serverSideDataTable"]/tbody/tr/td[6]/span')))
        lances = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="serverSideDataTable"]/tbody/tr/td[15]/ul/li/ul/li[1]/span[2]')))
        anos = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="serverSideDataTable"]/tbody/tr/td[4]/span[1]')))
        locais = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="serverSideDataTable"]/tbody/tr/td[11]/a/span')))
        links = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="serverSideDataTable"]/tbody/tr/td[3]/div/a')))

        for nome, lance, ano, local, link in zip(nomes, lances, anos, locais, links):
            all_motos_data.append([nome.text, lance.text, ano.text, local.text, link.get_attribute('href')])
    except Exception as e:
        print(f"Erro ao buscar dados da Copart: {e}")

    return all_motos_data

# Coletar dados de Sodré Santoro e Copart
sodre_motos = get_motos_from_sodre()
copart_motos = get_motos_from_copart()

# Filtrar apenas Harley no Sodré
harley_sodre_motos = [moto for moto in sodre_motos if 'harley' in moto[0].lower()]

# Combinar as motos Harley de ambos os sites
combined_motos = harley_sodre_motos + copart_motos

# Enviar e-mail com dados combinados
if combined_motos:
    table_data = tabulate(combined_motos, headers=["Nome", "Lance", "Ano", "Local", "Link"], tablefmt="html")
    body = f"<p>Abaixo estão as motos Harley Davidson encontradas nos leilões:</p>{table_data}"
    send_email("Motos Harley Davidson - Leilões", body, "j.nisi@proton.me")

# Fechar o navegador
driver.quit()
