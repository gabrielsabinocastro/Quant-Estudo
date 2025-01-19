from func_tools import *



class Medias_Moveis:

    '''
    #deve funcionar para 1 ou mais ativos na carteira
    #se a média longa cruza a média curta dentro da janela de rebalanço, vende ou compra
    #então a cada janela de rebalanço deve calcular as médias de todos, efetuar as operações e registrar os históricos
    # tipo de média simples ou exponencial
    # VERIFICAR SE A CLASSE VAI MODIFICAR OS HISTÓRICOS DE PREÇOS, se será necessário criar um a deepycopy
    # seria interessante um parâmetro opcional para calibrar a posição venda ou compra para níveis entre 0 e 1.
    
    '''

    def __init__(self, carteira, series_historicas, jan_rebalanco, jan_md_curta, jan_md_longa, moeda_base, valor='open', tipo="simples"):
        
        self.carteira = carteira
        self.historico = []
        self.series_historicas = copy.deepcopy(series_historicas)
        self.jan_rebalanco = jan_rebalanco
        self.jan_md_curta = jan_md_curta
        self.jan_md_long = jan_md_longa
        self.moeda_base = moeda_base
        self.valor = valor
        self.tipo = tipo
        self.info = {
            "Janela de Rebalanço": self.jan_rebalanco, 
            "Janela de Média Curta": self.jan_md_curta,
            "Janela de Média Longa": self.jan_md_longa,
            "Tipo de Mèdia": self.tipo
        }

        pass


    def media_curta(self):
        
        for par_ticket in self.series_historicas[par_ticket]:
            if self.tipo == 'simples':
                self.series_historicas[par_ticket]
                ['short_mean'] = self.series_historicas[par_ticket]
                [self.valor].rolling(window=self.jan_md_curta).mean()
            else:
                self.series_historicas[par_ticket]
                ['short_mean'] = self.series_historicas[par_ticket]
                [self.valor].ewm(span=self.jan_md_curta, adjust=False).mean()

    def media_longa(self):
        
        for par_ticket in self.series_historicas[par_ticket]:
            if self.tipo == 'simples':
                self.series_historicas[par_ticket]
                ['long_mean'] = self.series_historicas[par_ticket]
                [self.valor].rolling(window=self.jan_md_longa).mean()
            else:
                self.series_historicas[par_ticket]
                ['long_mean'] = self.series_historicas[par_ticket]
                [self.valor].ewm(span=self.jan_md_longa, adjust=False).mean()
