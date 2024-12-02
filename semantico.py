# ---------------------------------------------------
# Tradutor para a linguagem B-A-BA plus
#
# versao 2a (28/nov/2024)
# ---------------------------------------------------
from ttoken import TOKEN


class Semantico:

    def __init__(self, nomeAlvo):
        self.tabelaSimbolos = list()
        self.tabelaSimbolos = [dict()] + self.tabelaSimbolos
        self.alvo = open(nomeAlvo, "wt")
        self.declara((TOKEN.ident, 'len', None, None), (
            TOKEN.FUNCTION,
            [(None, True), (TOKEN.INT, False)]
        ))
        self.declara((TOKEN.ident, 'num2str', None, None), (
            TOKEN.FUNCTION,
            [(TOKEN.FLOAT, False), (TOKEN.STRING, False)]
        ))
        self.declara((TOKEN.ident, 'str2num', None, None), (
            TOKEN.FUNCTION, [(TOKEN.STRING, False), (TOKEN.FLOAT, False)]
        ))
        self.declara((TOKEN.ident, 'trunc', None, None), (
            TOKEN.FUNCTION,
            [(TOKEN.FLOAT, False), (TOKEN.INT, False)]
        ))

    def finaliza(self):
        self.alvo.close()

    def erroSemantico(self, tokenAtual, msg):
        (token, lexema, linha, coluna) = tokenAtual
        print(f'Erro na linha {linha}, coluna {coluna}:')
        print(f'{msg}')
        raise Exception

    def gera(self, nivel, codigo):
        identacao = ' ' * 3 * nivel
        linha = identacao + codigo
        self.alvo.write(linha)

    def declara(self, tokenAtual, tipo):
        """ nome = lexema do ident
            tipo = (base, lista)
            base = int | float | strig | function | None # listas genericas
            Se base in [int,float,string]
                lista = boolean # True se o tipo for lista
            else
                Lista = lista com os tipos dos argumentos, mais tipo do retorno
        """
        (token, nome, linha, coluna) = tokenAtual
        if self.existe_no_escopo(tokenAtual):
            msg = f'Variavel {nome} redeclarada'
            self.erroSemantico(tokenAtual, msg)
        else:
            escopo = self.tabelaSimbolos[0]
            escopo[nome] = tipo

    def consulta(self, tokenAtual):
        (token, nome, linha, coluna) = tokenAtual
        for escopo in self.tabelaSimbolos:
            if nome in escopo:
                return escopo[nome]
        msg = f'Variavel {nome} nao declarada'
        self.erroSemantico(tokenAtual, msg)


    def existe_no_escopo(self, tokenAtual):
        (token, nome, linha, coluna) = tokenAtual
        for escopo in self.tabelaSimbolos:
            if nome in escopo:
                return True
        return False

    def iniciaFuncao(self):
        self.tabelaSimbolos = [dict()] + self.tabelaSimbolos

    def terminaFuncao(self):
        self.tabelaSimbolos = self.tabelaSimbolos[1:]
