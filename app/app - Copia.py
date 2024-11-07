from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import requests
import datetime
import time
import csv
import os
import math
import pandas as pd
import numpy as np

def obter_linhas(n, driver, objeto_pregao, UASG_Gerenciadora, numero_licitacao, ano_licitacao, modalidade_licitacao): # n é o total de itens na página
    
    # Localiza a tabela
    tabela_itens = driver.find_element(By.ID, 'item')
    
    # Captura a linha da tabela (tbody)
    linha = tabela_itens.find_element(By.XPATH, './/tbody/tr['+ str(n) +']')
    colunas = linha.find_elements(By.TAG_NAME, 'td')

    tipo_item = colunas[1].text
    
    # Armazena os dados da primeira linha em uma lista
    linha = [
        colunas[0].text,  # Nº do Item
        tipo_item,  # Tipo do Item
        colunas[2].text,  # Descrição do Item
        #colunas[3].text,  # Qtde do Item
        colunas[4].text   # Unidade de Fornecimento
    ]

    print(f"Coletando Item {colunas[0].text}")
    
    # Clica no link da coluna Ações
    acao_link = colunas[5].find_element(By.TAG_NAME, 'a')
    acao_link.click()
    
    # Espera um tempo para a nova página carregar
    time.sleep(2)  # Ajuste conforme necessário
    
    # Acesse a tabela de descrição detalhada
    descricao_detalhada_element = driver.find_element(By.NAME, 'cabecalhoItemSRP.descricaoDetalhadaItem')
    
    # Armazena o texto na variável
    descricao_detalhada = descricao_detalhada_element.get_attribute('value')
    
    # Acesse a aba "Solicitações do Item" e clique no link
    aba_solicitacoes_link = driver.find_element(By.ID, 'ui-id-2')
    aba_solicitacoes_link.click()
    
    # Espera um tempo para a aba carregar
    #time.sleep(2)  # Ajuste conforme necessário
    
    # Clique na aba "UASGs do Item"
    aba_uasg_link = driver.find_element(By.ID, 'ui-id-3')
    aba_uasg_link.click()
    
    # Espera um tempo para a aba carregar
    #time.sleep(2)  # Ajuste conforme necessário
    
    # Acesse a tabela de UASGs
    uasg_table = driver.find_element(By.ID, 'uasgItemSRP')
    
    # Localize todas as linhas da tabela
    rows = uasg_table.find_elements(By.TAG_NAME, 'tr')
    
    # Inicializa as variáveis
    #UASG_Gerenciadora = UASG
    quantidade_homologada = None

    if UASG_Gerenciadora == "160224 - PARQUE REGIONAL DE MANUTENCAO/5":

        # Itera sobre as linhas, começando a partir da segunda linha (ignora cabeçalho)
        for row in rows[1:]:
            columns = row.find_elements(By.TAG_NAME, 'td')
            
            # Verifica se há pelo menos 2 colunas
            if len(columns) >= 2:
                tipo_uasg = columns[1].text.strip()
                if tipo_uasg == "Gerenciadora":
                    # Armazena os valores desejados
                    #UASG_Gerenciadora = columns[0].text.strip()
                    quantidade_homologada = columns[2].text.strip()
                    break  # Para a busca após encontrar

    else:
    
        # Itera sobre as linhas, começando a partir da segunda linha (ignora cabeçalho)
        for row in rows[1:]:
            columns = row.find_elements(By.TAG_NAME, 'td')
            
            # Verifica se há pelo menos 2 colunas
            if len(columns) >= 2:
                ug_participante = columns[0].text.strip()
                if ug_participante == "160224 - PARQUE REGIONAL DE MANUTENCAO/5":
                    # Armazena os valores desejados
                    #UASG_Gerenciadora = columns[0].text.strip()
                    quantidade_homologada = columns[2].text.strip()
                    break  # Para a busca após encontrar

    
    # Acesse a aba "Fornecedores do Item"
    fornecedor_tab = driver.find_element(By.ID, 'ui-id-4')
    fornecedor_tab.click()
    
    # Espera a aba carregar
    #time.sleep(2)  # Ajuste conforme necessário

    try:
    
        # Acesse a tabela de fornecedores
        fornecedor_table = driver.find_element(By.ID, 'fornecedorSRP')
        
        # Localize todas as linhas da tabela
        rows = fornecedor_table.find_elements(By.TAG_NAME, 'tr')
        
        # Inicializa as variáveis
        fornecedor = None
        marca_material = None
        valor_unitario = None
        
        # Obtém a primeira linha da tabela (excluindo o cabeçalho)
        
        if len(rows) > 1:
            columns = rows[1].find_elements(By.TAG_NAME, 'td')
            
            # Armazena os valores desejados
            if len(columns) >= 3:

                #para itens do tipo 'Material'

                if tipo_item == 'Material':
                    fornecedor = columns[1].text.strip()
                    marca_material = columns[2].text.strip()
                    valor_unitario = columns[5].text.strip()

                if tipo_item == 'Serviço':
                    fornecedor = columns[1].text.strip()
                    
                    valor_unitario = columns[4].text.strip()
                    

    except:

        fornecedor = None
        marca_material = None
        valor_unitario = None

    # Append os dados apenas se for encontrado o ug_participante "160224 - PARQUE REGIONAL DE MANUTENCAO/5" ou UASG_Gerenciadora for "160224"
    
    if UASG_Gerenciadora == "160224 - PARQUE REGIONAL DE MANUTENCAO/5" or ug_participante == "160224 - PARQUE REGIONAL DE MANUTENCAO/5":

        linha.append(descricao_detalhada)
        linha.append(UASG_Gerenciadora)
        linha.append(quantidade_homologada)
        linha.append(fornecedor)
        linha.append(marca_material)
        linha.append(valor_unitario)
        linha.append(objeto_pregao)
        linha.append(numero_licitacao)
        linha.append(ano_licitacao)
        linha.append(modalidade_licitacao)

        
        return linha

        

    else:

        return None






def obter_dados(UASG,num_licitacao,ano_licitacao):

    linhas = []

    url = "https://www2.comprasnet.gov.br/siasgnet-atasrp/public/pesquisarItemSRP.do?method=iniciar&parametro.identificacaoCompra.numeroUasg="+str(UASG)+"&parametro.identificacaoCompra.modalidadeCompra=5&parametro.identificacaoCompra.numeroCompra="+str(num_licitacao)+"&parametro.identificacaoCompra.anoCompra="+str(ano_licitacao)

    driver = webdriver.Chrome()
    driver.get(url)
    # Espera um pouco para garantir que a nova página carregue
    time.sleep(5)  # Ajuste o tempo conforme necessário

    # Obtém o texto do objeto da licitação
    objeto_pregao = driver.find_element(By.XPATH, "//textarea[@name='cabecalhoLicitacaoSRP.objeto']").get_attribute('value')

    # Obtém a UASG gerenciadora
    UASG_gerenciadora_input = driver.find_element(By.NAME, 'cabecalhoLicitacaoSRP.uasgGerenciadora.uasgFormatada')
    UASG_gerenciadora = UASG_gerenciadora_input.get_attribute('value')
    
    # Obtém o número da licitação
    numero_licitacao_input = driver.find_element(By.NAME, 'cabecalhoLicitacaoSRP.numeroLicitacaoFormatado')
    numero_licitacao = numero_licitacao_input.get_attribute('value')
    
    # Obtém a modalidade da licitação
    modalidade_licitacao_input = driver.find_element(By.NAME, 'cabecalhoLicitacaoSRP.modalidadeLicitacao')
    modalidade_licitacao = modalidade_licitacao_input.get_attribute('value')
    
    # Obtém a quantidade de itens
    quantidade_itens_element = driver.find_element(By.NAME, 'cabecalhoLicitacaoSRP.quantidadeItens')
    
    qtd_itens = int(quantidade_itens_element.get_attribute('value'))
    
    # Obtém o número de páginas
    n_paginas = math.ceil(qtd_itens/20)

    print(f'Iniciando a coleta dos itens do pregão {numero_licitacao}...')
    
    #iniciar obtenção dos dados

    print(f'\nIndo para página 1.')
   
    for n in range(1,21):

        try:
    
            linha = obter_linhas(n, driver, objeto_pregao, UASG_gerenciadora, numero_licitacao, ano_licitacao, modalidade_licitacao)
    
            if linha != None:
            
                linhas.append(linha)
            
            # Acesse a tabela de navegação e clique no botão "Pesquisar Item SRP"
            pesquisar_button = driver.find_element(By.ID, 'btnPesquisarItemSRP')
            pesquisar_button.click() #volta para página inicial dos itens

        except:
            
            break


    try:
    
        for i in range(2,n_paginas+1):
    
            print(f'\nIndo para página {i}.')
        
            for n in range(1,21):
        
                page_link = driver.find_element(By.LINK_TEXT, str(i))
                page_link.click()                
    
                try:
    
                    linha = obter_linhas(n, driver, objeto_pregao, UASG_gerenciadora, numero_licitacao, ano_licitacao, modalidade_licitacao)
    
                    if linha != None:
                        linhas.append(linha)
                    
                    # Acesse a tabela de navegação e clique no botão "Pesquisar Item SRP"
                    pesquisar_button = driver.find_element(By.ID, 'btnPesquisarItemSRP')
                    pesquisar_button.click()
    
                except:
    
                    print(f'A coleta dos dados do pregão {numero_licitacao} chegou ao fim.')
    
                    break

    except:

        print(f'A coleta dos dados do pregão {numero_licitacao} chegou ao fim.')
        

    
    # Fechar o driver
    driver.quit()

    return linhas


def gerar_df(linhas):

    
    #atribuir nome às colunas do df obtido
    
    colunas = ['Número do Item',
               'Tipo do Item',
               'Descrição',
               'Unidade de Fornecimento',
               'Descrição Detalhada',
               'UASG',
               'Qtd. Saldo',
               'Fornecedor',
               'Marca',
               'Val. Unitário',
                'Objeto',
               'Número da Compra',
               'Ano do Pregão',
               'Tipo de Compra',
              ]
    
    df_itens_gerenciadora = pd.DataFrame(linhas, columns = colunas)
    
    colunas_novas = ['Número da Compra',
               'Número do Item',
               'Descrição',
               'Descrição Detalhada',
               'Início da Vigência',
               'Fim da Vigência',
               'Unidade',
               'Qtd. Autorizada',
               'Fornecedor',
               'Val. Unitário',
               'Qtd. Saldo',
               'Marca',
               'Tipo de Compra',
               'Número do Pregão',
               'Ano do Pregão',
               'UASG',
               'Objeto',
               'Unidade de Fornecimento'
              ]
    
    inicio_vigencia = None
    fim_vigencia = None
    qtd_autorizada = df_itens_gerenciadora['Qtd. Saldo']
    unidade =  df_itens_gerenciadora['UASG']
    
    df_itens_gerenciadora['Início da Vigência'] = inicio_vigencia
    df_itens_gerenciadora['Fim da Vigência'] = fim_vigencia
    df_itens_gerenciadora['Unidade'] = unidade
    df_itens_gerenciadora['Qtd. Autorizada'] = qtd_autorizada
    df_itens_gerenciadora['Número do Pregão'] = df_itens_gerenciadora['Número da Compra'].str.split('/').str[0]
    
    df_itens_gerenciadora = df_itens_gerenciadora[colunas_novas]

    #Corrigir dados de Valor Unitário
    
    df_itens_gerenciadora['Val. Unitário'] = df_itens_gerenciadora['Val. Unitário'].str.replace('.','')
    df_itens_gerenciadora['Val. Unitário'] = df_itens_gerenciadora['Val. Unitário'].str.replace(',','.')
    df_itens_gerenciadora['Descrição Detalhada'] = df_itens_gerenciadora['Descrição Detalhada'].str.replace(';',',')
    
    #Corrigir Tipo de dados das colunas
    
    #df_itens_gerenciadora.loc[:,'Número do Pregão'] = df_itens_gerenciadora.loc[:,'Número do Pregão'].astype(int)
    df_itens_gerenciadora.loc[:,'Número do Item'] = df_itens_gerenciadora.loc[:,'Número do Item'].astype(int)
    df_itens_gerenciadora.loc[:,'Val. Unitário'] = df_itens_gerenciadora.loc[:,'Val. Unitário'].astype(float)
    
    #Mudar a coluna Número da Compra
    df_itens_gerenciadora.loc[:,'UASG'] = df_itens_gerenciadora.loc[:,'UASG'].astype(str)
    df_itens_gerenciadora['Número da Compra'] = df_itens_gerenciadora['UASG'].str[:6] + "-"+ df_itens_gerenciadora['Número da Compra']
    #df_itens_gerenciadora.loc[:,'UASG'] = df_itens_gerenciadora.loc[:,'UASG'].astype(int)

    #Ordenar dados
    df_itens_gerenciadora = df_itens_gerenciadora.sort_values(['Número da Compra','Número do Pregão','Número do Item'])

    return df_itens_gerenciadora

def concatenar_arquivos_empenho_CSV():
    
    # Defina o caminho da pasta que contém os arquivos CSV
    pasta_csv = 'empenhos/'
    
    # Lista para armazenar os DataFrames
    dataframes = []
    
    # Variável para controlar se é o primeiro arquivo
    primeiro_arquivo = True
    
    # Loop através dos arquivos na pasta
    for arquivo in os.listdir(pasta_csv):
        if arquivo.endswith('.csv'):
            # Cria o caminho completo do arquivo
            caminho_arquivo = os.path.join(pasta_csv, arquivo)
            
            # Lê o arquivo CSV
            if primeiro_arquivo:
                # Preserva todas as linhas do primeiro arquivo
                df = pd.read_csv(caminho_arquivo)
                primeiro_arquivo = False
            else:
                # Lê o arquivo, exclui a primeira e a última linha
                df = pd.read_csv(caminho_arquivo)
                df = df.iloc[1:-1]  # Remove a primeira e a última linha
            
            # Adiciona o DataFrame à lista
            dataframes.append(df)
    
    # Concatena todos os DataFrames em um único DataFrame
    df_empenhos_concatenado = pd.concat(dataframes, ignore_index=True)

    return df_empenhos_concatenado

def obter_vigencia():
    
    df = pd.read_csv('dados_SAG.csv')
    df = df[:-1]
    df = df[['UG','NR','ANO','ITEM NR', 'DATA DE ATUALIZAÇÃO DO ITEM']].copy()
    
    df['UG'] = df['UG'].astype(int)
    df['NR'] = df['NR'].astype(int)
    df['ANO'] = df['ANO'].astype(int)
    df['ITEM NR'] = df['ITEM NR'].astype(int)
    df.loc[:,'DATA DE ATUALIZAÇÃO DO ITEM'] = df['DATA DE ATUALIZAÇÃO DO ITEM'].str[:10]
    
    df.columns = ['UASG', 'Número do Pregão', 'Ano do Pregão', 'Número do Item', 'Início da Vigência']
    
    df['UASG'] = df['UASG'].astype(str)
    df['Número do Pregão'] = df['Número do Pregão'].astype(str)
    df['Ano do Pregão'] = df['Ano do Pregão'].astype(str)
    df['Número do Item'] = df['Número do Item'].astype(str)
    df['Início da Vigência'] = df['Início da Vigência'].astype(str)
    
    df['key'] = df['UASG'] + "_"+ df['Número do Pregão'] + "_"+ df['Ano do Pregão'] + "_"+ df['Número do Item']
    
    # Converte a coluna 'Início da Vigência' para o tipo datetime
    df['Início da Vigência'] = pd.to_datetime(df['Início da Vigência'], format='%d/%m/%Y')
    
    # Cria a coluna 'Fim da Vigência' adicionando 1 ano à 'Início da Vigência'
    df['Fim da Vigência'] = df['Início da Vigência'] + pd.DateOffset(years=1)
    
    # Formata a coluna 'Fim da Vigência' para o formato DD/MM/YYYY
    df['Fim da Vigência'] = df['Fim da Vigência'].dt.strftime('%d/%m/%Y')
    
    #Voltando a coluna Início da Vigência ao formato inicial
    df['Início da Vigência'] = df['Início da Vigência'].dt.strftime('%d/%m/%Y')

    df = df[['key','Início da Vigência','Fim da Vigência']].copy()

    return df      
    
def tratar_dados_empenho(df_empenhos_concatenado):
    
    #df = pd.read_csv('empenhos/dados_empenhos.csv')
    df = df_empenhos_concatenado[['NR','INFORMAÇÃO COMPLEMENTAR','OBS LI','QUANTIDADE']].copy()
    df.loc[:, 'UASG'] = df['INFORMAÇÃO COMPLEMENTAR'].str[:6]
    df.loc[:, 'Ano do Pregão'] = df['INFORMAÇÃO COMPLEMENTAR'].str[13:17]
    df.loc[:, 'Número do Pregão'] = df['INFORMAÇÃO COMPLEMENTAR'].str[8:13]
    df = df[df['OBS LI'].str.contains('ITEM', na=False)]
    df['OBS LI'].str.split(' ')
    df['Número do Item'] = df['OBS LI'].str.split(' ').str[2]
    df = df[['UASG','Número do Pregão','Ano do Pregão','Número do Item', 'QUANTIDADE']]
    df.to_csv('empenhos/dados_empenho_tratado.csv', sep = ';', index = False)

def calcular_saldo():
    
    df_itens = pd.read_csv('df_itens_gerenciadora.csv',sep=';')
    df_itens['UG'] = df_itens['Unidade'].str[:6]
    df_itens['UG'] = df_itens['UG'].astype(str)
    df_itens['Número do Pregão'] = df_itens['Número do Pregão'].astype(str)
    df_itens['Ano do Pregão'] = df_itens['Ano do Pregão'].astype(str)
    df_itens['Número do Item'] = df_itens['Número do Item'].astype(str)
    df_itens['Qtd. Saldo'] = df_itens['Qtd. Saldo'].astype(float)
    df_itens['key'] = df_itens['UG'] + "_" + df_itens['Número do Pregão']+ "_" + df_itens['Ano do Pregão'] + "_"+ df_itens['Número do Item']
    
    df_qtd = pd.read_csv('empenhos/dados_empenho_tratado.csv', sep = ';')
    df_qtd['UASG'] = df_qtd['UASG'].astype(str)
    df_qtd['Número do Pregão'] = df_qtd['Número do Pregão'].astype(str)
    df_qtd['Ano do Pregão'] = df_qtd['Ano do Pregão'].astype(str)
    df_qtd['Número do Item'] = df_qtd['Número do Item'].astype(str)
    df_qtd['key'] = df_qtd['UASG'] + "_"+ df_qtd['Número do Pregão'] + "_"+ df_qtd['Ano do Pregão'] + "_"+ df_qtd['Número do Item']
    df_qtd = df_qtd.groupby('key', as_index=False)['QUANTIDADE'].sum()
    
    df_final_sem_vigencia = pd.merge(df_itens, df_qtd, on='key', how='left')

    df_vigencia = obter_vigencia()

    df_final = pd.merge(df_final_sem_vigencia, df_vigencia, on='key', how='left')
    
    df_final = df_final[['Número da Compra', 'Número do Item', 'Descrição',
           'Descrição Detalhada', 
           'Unidade', 'Qtd. Autorizada', 'Fornecedor', 'Val. Unitário',
           'Qtd. Saldo', 'Marca', 'Tipo de Compra', 'Número do Pregão',
            'Ano do Pregão', 'UASG','Objeto', 'Unidade de Fornecimento', 'UG',
           'QUANTIDADE','Início da Vigência_y','Fim da Vigência_y']]
    
    df_final.columns = ['Número da Compra', 'Número do Item', 'Descrição',
           'Descrição Detalhada', 
           'Unidade', 'Qtd. Autorizada', 'Fornecedor', 'Val. Unitário',
           'Qtd. Saldo', 'Marca', 'Tipo de Compra', 'Número do Pregão',
           'Ano do Pregão', 'UASG', 'Objeto', 'Unidade de Fornecimento', 'UG',
           'Quantidade Empenhada','Início da Vigência', 'Fim da Vigência']
    
    df_final.loc[:,'Quantidade Empenhada'] = df_final.loc[:,'Quantidade Empenhada'].replace(np.NaN,0)    
    df_final.loc[:,'Qtd. Autorizada'] = df_final.loc[:,'Qtd. Autorizada'].astype(float)    
    df_final.loc[:,'Qtd. Saldo'] = df_final.loc[:,'Qtd. Autorizada'] - df_final.loc[:,'Quantidade Empenhada']    
    df_final['Capacidade de Empenho'] = df_final['Qtd. Saldo']*df_final['Val. Unitário']

    #Excluindo itens sem fornecedor (desertos ou fracassados)
    df_final = df_final[df_final['Fornecedor'].notna()]
    
    #Salvando o df final
    df_final['Número do Item'] = df_final['Número do Item'].astype(int)
    df_final = df_final.sort_values(['Número da Compra','Número do Pregão','Número do Item'])
    df_final.to_csv('df_final.csv', sep=';', encoding='utf-8', index=False)

    return df_final

#######################################################################

from flask import Flask, request, redirect, url_for, flash, render_template_string
import pandas as pd

app = Flask(__name__)
app.secret_key = "chave_secreta"

@app.route('/')
def index():
    # Obter valores únicos se for a opção de "Ver Pregões Salvos"
    valores_unicos = request.args.getlist('valores_unicos')
    html = '''
    <!doctype html>
    <html lang="pt-br">
    <head>
      <meta charset="utf-8">
      <title>Interface Iniciar</title>
      <style>
        table {
          width: 50%;
          border-collapse: collapse;
          margin-top: 20px;
        }
        th, td {
          border: 1px solid #ddd;
          padding: 8px;
          text-align: center;
        }
        th {
          background-color: #f2f2f2;
          font-weight: bold;
        }
      </style>
    </head>
    <body>
      <h1>Escolha uma Opção</h1>
      <form action="{{ url_for('iniciar') }}" method="post">
        <label for="opcao">O que você gostaria de fazer?</label>
        <select name="opcao" id="opcao" onchange="toggleCampos(this.value)">
          <option value="1">Atualizar saldo</option>
          <option value="2">Ver Pregões Salvos</option>
          <option value="3">Obter dados de novo pregão</option>
          <option value="4">Apagar dados de pregão existente</option>
          <option value="5">Sair</option>
        </select>
        
        <!-- Campos adicionais para UASG, número de licitação e ano -->
        <div id="opcao3Campos" style="display: none;">
          <label for="uasg">UASG:</label>
          <input type="text" name="uasg" id="uasg"><br>
          <label for="num_licitacao">Número da Licitação:</label>
          <input type="text" name="num_licitacao" id="num_licitacao"><br>
          <label for="ano_licitacao">Ano da Licitação:</label>
          <input type="text" name="ano_licitacao" id="ano_licitacao"><br>
        </div>

        <button type="submit">Executar</button>
      </form>

      {% if valores_unicos %}
        <h2>Números de Compra Salvos:</h2>
        <table>
          <tr>
            <th>Número da Compra</th>
          </tr>
          {% for valor in valores_unicos %}
            <tr>
              <td>{{ valor }}</td>
            </tr>
          {% endfor %}
        </table>
      {% endif %}

      <script>
        function toggleCampos(opcao) {
          document.getElementById('opcao3Campos').style.display = opcao == "3" ? 'block' : 'none';
        }
      </script>
    </body>
    </html>
    '''
    return render_template_string(html, valores_unicos=valores_unicos)

@app.route('/iniciar', methods=['POST'])
def iniciar():
    opcao = request.form['opcao']

    if opcao == "1":
        try:
            df_empenhos_concatenado = concatenar_arquivos_empenho_CSV()
            tratar_dados_empenho(df_empenhos_concatenado)
            calcular_saldo()
            flash('Saldo atualizado com sucesso!')
        except Exception as e:
            flash(f"Erro ao atualizar o saldo: {e}")
    
    elif opcao == "2":
        try:
            df_itens_gerenciadora = pd.read_csv('df_itens_gerenciadora.csv', sep=';', encoding='utf-8')
            valores_unicos = df_itens_gerenciadora['Número da Compra'].unique()
            return redirect(url_for('index', valores_unicos=valores_unicos))
        except FileNotFoundError:
            flash("O arquivo 'df_itens_gerenciadora.csv' não foi encontrado.")
            return redirect(url_for('index'))
    
    elif opcao == "3":
        uasg = request.form.get('uasg')
        num_licitacao = request.form.get('num_licitacao')
        ano_licitacao = request.form.get('ano_licitacao')
        linhas = obter_dados(uasg, num_licitacao, ano_licitacao)
        df_itens_gerenciadora_novo = gerar_df(linhas)
        df_itens_gerenciadora_novo.to_csv('df_itens_gerenciadora_novo.csv', sep=';', encoding='utf-8', index=False)
        flash("Dados obtidos com sucesso!")
    
    elif opcao == "4":
        flash("Opção de exclusão executada com sucesso.")
    
    elif opcao == "5":
        flash("Saindo do programa.")

    else:
        flash("Opção inválida! Tente novamente.")

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
