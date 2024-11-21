# ---------------------------------------------------
# Tradutor para a linguagem CALC
#
# versao 1a (mar-2024)
# ---------------------------------------------------
from ttoken import TOKEN

class Semantico:

    def __init__(self, nomeAlvo):
        self.tabelaSimbolos = dict()
        self.alvo = open(nomeAlvo, "wt")

    def finaliza(self):
        self.alvo.close()

    def erroSemantico(self, tokenAtual, msg):
        (token, lexema, linha, coluna) = tokenAtual
        print(f'Erro na linha {linha}, coluna {coluna}:')
        print(f'{msg}')
        raise Exception

    def gera(self, nivel, codigo):
        identacao = ' ' * 4 * nivel
        linha = identacao + codigo
        self.alvo.write(linha)

    def declara(self, token):
        if token[1] in self.tabelaSimbolos:
            msg = f'Variavel {token[1]} redeclarada'
            self.erroSemantico(token, msg)
        else:
            self.tabelaSimbolos[token[1]] = token[0]
