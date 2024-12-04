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
    msg.attach(MIMEText(body, 'plain'))

    # Envia o e-mail
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()

    print("E-mail enviado com sucesso!")

# Configura o WebDriver do Safari
options = webdriver.SafariOptions()
driver = webdriver.Safari(options=options)

# Função para extrair as motos de uma página
def get_motos_from_page(url, retries=2):
    driver.get(url)
    
    # Espera explícita para garantir que o conteúdo tenha carregado
    wait = WebDriverWait(driver, 20)
    
    # Lista para armazenar os dados das motos
    motos_data = []
    
    for attempt in range(retries):
        try:
            # Tentativa de localizar os elementos
            elementos = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "w-full")]/a/h2')))
            precos = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "w-full")]/a/p[2]')))  # Preço
            datas = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "w-full")]/a/div/div[1]/p/span')))  # Data
            
            # Verifica se a lista de motos, preços ou datas está vazia
            if not elementos or not precos or not datas:
                print("Nenhuma moto, preço ou data encontrada na página. Finalizando a busca.")
                return False  # Retorna False para indicar que não há motos, preços ou datas na página
            
            # Adicionando dados na lista para exibição posterior
            for nome, preco, data in zip(elementos, precos, datas):
                motos_data.append([nome.text, preco.text, data.text])  # Adiciona os dados na lista

            return motos_data  # Retorna os dados coletados

        except Exception as e:
            print(f"Erro ao buscar motos, preços ou datas: {e}")
            # Se falhar, tenta novamente após um pequeno intervalo
            print(f"Tentando novamente... ({attempt + 1}/{retries})")
            time.sleep(2)  # Espera antes de tentar novamente

    return False  # Se todas as tentativas falharem, retorna False

# URL base com a paginação
base_url = "https://www.sodresantoro.com.br/veiculos/lotes?lot_category=motos&order=0&page="

# Cabeçalho da tabela
headers = ["Nome", "Preço", "Data"]

# Iterar pelas páginas, começando da 1
page_number = 1
all_motos_data = []  # Lista para armazenar todas as motos coletadas

while True:
    url = base_url + str(page_number)
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

# Exibindo os dados coletados em formato tabular ao final
if all_motos_data:
    table_data = tabulate(all_motos_data, headers=headers, tablefmt="grid")
    print("\nTodos os dados coletados:")
    print(table_data)

    # Enviar o e-mail com os dados coletados
    subject = "Motos Harley Davidson Encontradas"
    body = f"Abaixo estão as motos Harley Davidson encontradas no leilão:\n\n{table_data}"
    to_email = "j.nisi@proton.me"  # E-mail de destino
    send_email(subject, body, to_email)

# Fechar o driver após o processo
driver.quit()
