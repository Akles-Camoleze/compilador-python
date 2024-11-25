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
        self.declara((TOKEN.ident, 'len', None, None), (TOKEN.FUNCTION, [(None, True), (TOKEN.INT, False)]))
        self.declara((TOKEN.ident, 'num2str', None, None), (TOKEN.FUNCTION, [(TOKEN.FLOAT, False), (TOKEN.STRING, False)]))
        self.declara((TOKEN.ident, 'str2num', None, None), (TOKEN.FUNCTION, [(TOKEN.STRING, False), (TOKEN.FLOAT, False)]))
        self.declara((TOKEN.ident, 'trunc', None, None), (TOKEN.FUNCTION, [(TOKEN.FLOAT, False), (TOKEN.INT, False)]))

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

    def declara(self, token, tipo):
        """ nome = lexema do ident
            tipo = (base, lista)
            base = int | float | strig | function | None # None para listas genericas
            Se base in [int,float,string]
                lista = boolean # True se o tipo for uma lista da base
            else
                Lista = lista com os tipos dos arguentos, sendo
                o tipo de cada argumento um par (base,lista)
                Retorno = o ultimo tipo da lista sera o tipo do retorno
        """
        if token[1] in self.tabelaSimbolos:
            msg = f'Variavel {token[1]} redeclarada'
            self.erroSemantico(token, msg)
        else:
            self.tabelaSimbolos[token[1]] = tipo
