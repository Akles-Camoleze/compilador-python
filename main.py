#---------------------------------------------------
# Tradutor para a linguagem CALC
#
# versao 1a (mar-2024)
#---------------------------------------------------
from lexico import Lexico
from sintatico import Sintatico
# from sintatico import Sintatico
from ttoken import TOKEN

class Tradutor:

    def __init__(self, nomeArq):
        self.nomeArq = nomeArq

    def inicializa(self):
        self.arq = open(self.nomeArq, "r")
        self.lexico = Lexico(self.arq)
        self.sintatico = Sintatico(self.lexico)

    def traduz(self):
        self.sintatico.traduz()

    def testaLexico(self):
        self.tokenLido = self.lexico.getToken()
        (token, lexema, linha, coluna) = self.tokenLido
        while token != TOKEN.eof:
            self.lexico.imprimeToken(self.tokenLido)
            self.tokenLido = self.lexico.getToken()
            (token, lexema, linha, coluna) = self.tokenLido

    def finaliza(self):
        self.arq.close()

# inicia a traducao
if __name__ == '__main__':
    x = Tradutor('codigoFonte.txt')
    x.inicializa()
    # x.traduz()
    x.testaLexico()
    x.finaliza()
