import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
#import requests
import copy

import ccxt #acessa dados de crpytos






class Carteira:

    '''
    Classe que modela a carteira de ativos que é alferida a partir de uma moeda base, viesando as transações para
    uma relação de várias para uma (diferente de várias para várias).
    O valor 0.1% é arbitrado para taxa de transação e cobrado sempre no saldo da moeda base.
    Após todas as atualizações de posição é necessário chamar o método que registra o histórico para avaliações futuras.
    '''

    def __init__(self, moeda_base="USDT", saldo=0):

        self.moeda_base = moeda_base
        self.saldo = saldo
        self.posicoes = {
            moeda_base: {
                "quantidade": saldo,
                "preco_medio": 1.0  # Sempre 1.0 para moeda base
            }

        }

    def atualiza_saldo(self):
        self.saldo = sum(
                    posicao["quantidade"] * posicao["preco_medio"]
                            for posicao in self.posicoes.values())
        return self.saldo

    def atualiza_posicao(self, ticket, quantidade, preco_medio, taxa=0.001):
            '''
            Adiciona ou atualiza uma posição no registro,
            quantidade < 0 para venda.

            '''
            if ticket in self.posicoes:
                posicao = self.posicoes[ticket]
                posicao["quantidade"] += quantidade
                posicao["preco_medio"] = (
                    (posicao["preco_medio"] * posicao["quantidade"] + preco_medio * quantidade) /
                    (posicao["quantidade"] + quantidade)
                )
            else:
                self.posicoes[ticket] = {
                    "quantidade": quantidade,
                    "preco_medio": preco_medio
                }
            i = -1 if quantidade < 0 else 1
            self.posicoes[self.moeda_base]["quantidade"] -= quantidade * preco_medio * (1 + i * taxa)

            self.atualiza_saldo()



def baixa_series(inicio, janela, par, exchange=ccxt.binanceus()):
    '''
    Função que busca dados histórisco de um PAR no modelo OHLCV
    recebe:
        inicio   - data como string no tipo "AAAA-MM-DD"
        janela   - intervalo de tempo, ex.: "1d", "1h", "1m"
        par      - string do ticket conforme regra da exchange, ex.: "BTC/USDT"
        exchange - exchange da biblioteca ccxt, ex.: ccxt.binanceus()
    retorna:
        df - DataFrame em Pandas
    '''

    dados = []
    since = exchange.parse8601(inicio + "T00:00:00Z")
    colunas = ["timestamp", "open", "high", "low", "close", "volume"]

    while since < exchange.milliseconds():
        ohlcv = exchange.fetch_ohlcv(par, timeframe=janela, since=since, limit=1000) # OHLCV (Timstamp, Open, High, Low, Close, Volume) retornados pela função fetch_ohlcv
        if len(ohlcv) == 0:
            break
        dados.extend(ohlcv)
        since = ohlcv[-1][0] + 1  # Atualiza o timestamp para continuar
        #datetime.sleep(1)  # Evitar limite de taxa
    df = pd.DataFrame(dados, columns=colunas)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["logreturns"] = np.log(df["close"] / df["close"].shift(1))

    return df



def separa_pares(par):
    '''
    Função que separa o par AAAA/BBBB em duas strings.
    '''
    try:
        ticket, moeda_base = par.split("/")
        return ticket, moeda_base

    except ValueError:
        print("Verifique o par informado no formato AAAA/BBBB")
        return None, None



def lista_pares(exchange='binanceus', filtro=None):
    '''
    Função que retorna a lista de tickers disponíveis em uma exchange usando a biblioteca CCXT.
    recebe:
        exchange - string nome da exchange (padrão: 'binance').
        filtro   - filtro opcional para buscar tickers que contenham essa string.
    retorna:
        tickers  - lista de tickers disponíveis, filtrados ou não.
    '''

    try:
        exchange = getattr(ccxt, exchange)()
        markets = exchange.load_markets()
        tickers = list(markets.keys())

        if filtro:
            tickers = [ticker for ticker in tickers if filtro.upper() in ticker]

        return tickers

    except Exception as e:
        print(f"Erro ao acessar a API da exchange {exchange}: {e}")
        return []



def realiza_operacao(carteira, par, ticket_ohlcv, quantidade, operacao_data, valor='open', taxa=0.001):
    '''
    Função que simula operação de compra/venda na carteira a partir dos parâmtros dados. Não opera vendido.
    recebe:
        carteira      - objeto carteira para registro da operação.
        par           - string do tipo AAAA/BBBB ticket/moeda_base.
        ticket_ohlcv  - pandasDF com o histórico de cotações do par.
        quantidade    - float quantidade a ser comprada/vendida.
        operacao_data - string data em que será realizada a operação.
        valor         - string que determina o parâmetro de preço 'open', 'high', 'close', 'low'.
        taxa          - float taxa de operação.
    retorna:
        Nada
    '''

    ticket, moeda_base = separa_pares(par)
    df = ticket_ohlcv[ticket_ohlcv['timestamp'] == operacao_data]

    preco = df[valor].iloc[0]


    if quantidade < 0:
        carteira.atualiza_posicao(ticket, quantidade, preco, taxa)
        return

    if carteira.posicoes[carteira.moeda_base]["quantidade"] >= quantidade * preco * (1 + taxa):
        carteira.atualiza_posicao(ticket, quantidade, preco, taxa)

    else:
        print(f"Saldo insuficiente em {moeda_base} para realizar operação")

    return



def registra_historico(carteira, operacao_data, historico):
    '''
    Função que adiciona estado atual da carteira em uma lista de estados anteriorer
    recebe:
        carteira      - objeto carteira para registro da operação.
        operacao_data - string do tipo AAAA-DD-MM data da operação.
        historico     - lista com os históricos de posição da carteira.
    retorna:
        Nada
    '''

    historico.append((copy.deepcopy(carteira.posicoes), operacao_data, {"saldo": carteira.atualiza_saldo()}))



def dicionario_series(pares, inicio, janela, exchange=ccxt.binanceus()):
    '''
    Função que a partir de uma lista de pares, retorna um dicionário com as Séries dos tickets
    recebe:
        pares    - lista de strings pares tickets do tipo "AAAA/BBBB".
        inicio   - data como string no tipo "AAAA-MM-DD".
        janela   - intervalo de tempo, ex.: "1d", "1h", "1m".
        exchange - exchange da biblioteca ccxt, ex.: ccxt.binanceus().
    retorna:
        series   - dicionário com chave par e valor serie histórica.
    '''

    series = {}
    for par in pares:
        series[par] = baixa_series(inicio, janela, par, exchange)


    return series



def atualiza_data(data_str, dias=0, semanas=0, meses=0):
    '''
    Realiza operações com datas a partir de uma string no formato "AAAA-MM-DD".
    recebe:
        data_str - string representando a data no formato "AAAA-MM-DD".
        dias     - número de dias a adicionar ou subtrair (positivo ou negativo).
        semanas  - número de semanas a adicionar ou subtrair.
        meses    - número de meses a adicionar ou subtrair.
    retorna:
        data     - string representando a nova data no formato "AAAA-MM-DD" ou None em caso de erro.
    '''

    try:
        ano, mes, dia = map(int, data_str.split('-'))
        data = datetime.date(ano, mes, dia)

        data += datetime.timedelta(days=dias, weeks=semanas)

        if meses != 0:
            data = data.replace(month=data.month + meses)

        return data.strftime("%Y-%m-%d")

    except ValueError:
        print("Formato de data inválido. Use AAAA-MM-DD")
        return None
    