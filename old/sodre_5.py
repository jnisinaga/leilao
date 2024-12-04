import time
from time import sleep
import smtplib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tabulate import tabulate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Função para enviar o e-mail
def send_email(subject, body, to_email):
    from_email = "jnisinaga@gmail.com"  # Seu e-mail
    password = "fyvx uqdm ojax ukfb"  # Senha do seu e-mail (use senhas de app no caso de Gmail)

    # Configura o servidor SMTP
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)

    # Configura a mensagem
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))  # Enviar como HTML

    # Envia o e-mail
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()

    print("E-mail enviado com sucesso!")

# Configura o WebDriver do Safari
options = webdriver.SafariOptions()
driver = webdriver.Safari(options=options)

# URL base com a paginação
base_url = "https://www.sodresantoro.com.br/veiculos/lotes?lot_category=motos&order=0&page="

## Função para extrair as motos de uma página
def get_motos_from_page(url, retries=1):
    driver.get(url)
    
    wait = WebDriverWait(driver, 20)
    motos_data = []
    
    for attempt in range(retries):
        sleep(4)
        try:
            # Localiza os elementos de nome, preço, data e link
            elementos = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "w-full")]/a/h2')))
            precos = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "w-full")]/a/p[2]')))
            datas = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "w-full")]/a/div/div[1]/p/span')))
            links = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@id, "card-")]/div/div[1]/div[1]/div[1]/div[1]/a')))

            if not elementos or not precos or not datas or not links:
                print("Nenhuma moto, preço, data ou link encontrada na página. Finalizando a busca.")
                return False
            
            # Adiciona os dados de cada moto à lista
            for nome, preco, data, link in zip(elementos, precos, datas, links):
                moto_link = link.get_attribute('href')
                motos_data.append([nome.text, preco.text, data.text, moto_link])

            return motos_data

        except Exception as e:
            print(f"Erro ao buscar motos: {e}")
            print(f"Tentando novamente... ({attempt + 1}/{retries})")
            time.sleep(5)

    return False

# Cabeçalho da tabela atualizado
headers = ["Nome", "Preço", "Data", "Link"]

# Iterar pelas páginas, começando da 1
page_number = 1
all_motos_data = []  # Lista para armazenar todas as motos coletadas

while True:
    url = base_url + str(page_number)  # Concatena a URL com o número da página
    print(f"Buscando motos na página {page_number}...")
    
    # Chama a função para buscar motos e verifica se encontrou motos
    motos_data = get_motos_from_page(url)
    
    if not motos_data:
        break  # Encerra o loop se não houver motos
    
    all_motos_data.extend(motos_data)  # Adiciona os dados encontrados à lista geral
    
    # Imprime os dados da página atual enquanto os coleta
    print("\nDados encontrados na página", page_number)
    print(tabulate(motos_data, headers=headers, tablefmt="grid"))
    
    # Incrementa o número da página para a próxima
    page_number += 1
    time.sleep(2)  # Intervalo entre as requisições para dar tempo ao carregamento

# Filtro para motos da marca Harley Davidson
filtered_motos_data = [data for data in all_motos_data if 'harley' in data[0].lower()]

# Exibindo os dados filtrados em formato tabular ao final
if filtered_motos_data:
    # Converte a lista de motos filtradas para formato HTML
    table_data = tabulate(filtered_motos_data, headers=headers, tablefmt="html")
    
    # Corpo do e-mail em HTML
    body = f"""
    <p>Abaixo estão as motos Harley Davidson encontradas no leilão:</p>
    {table_data}
    """

    print("\nTodas as motos Harley Davidson encontradas:")
    print(table_data)

    # Enviar o e-mail com os dados filtrados
    subject = "Motos Harley Davidson Encontradas"
    to_email = "j.nisi@proton.me"  # E-mail de destino
    send_email(subject, body, to_email)

# Fechar o driver após o processo
driver.quit()