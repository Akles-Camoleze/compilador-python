# ---------------------------------------------------
# Tradutor para a linguagem B-A-BA
#
# versao 1a (out-2024)
# ---------------------------------------------------
from ttoken import TOKEN


class Lexico:

    def __init__(self, arqFonte):
        self.arqFonte = arqFonte  # objeto file
        self.fonte = self.arqFonte.read()  # string contendo file
        self.tamFonte = len(self.fonte)
        self.indiceFonte = 0
        self.tokenLido = None  # (token, lexema, linha, coluna)
        self.linha = 1  # linha atual no fonte
        self.coluna = 0  # coluna atual no fonte

    def fimDoArquivo(self):
        return self.indiceFonte >= self.tamFonte

    def getchar(self):
        if self.fimDoArquivo():
            return '\0'
        car = self.fonte[self.indiceFonte]
        self.indiceFonte += 1
        if car == '\n':
            self.linha += 1
            # colocar self.coluna = 1 também está funcionando, ver qual dos dois está realmente certo
            self.coluna = 0
        else:
            self.coluna += 1
        return car

    def ungetchar(self, simbolo):
        if simbolo == '\0':
            return

        if simbolo == '\n':
            self.linha -= 1

        if self.indiceFonte > 0:
            self.indiceFonte -= 1

        self.coluna -= 1

    def imprimeToken(self, tokenCorrente):
        (token, lexema, linha, coluna) = tokenCorrente
        msg = TOKEN.msg(token)
        print(f'(tk={msg} lex="{lexema}" lin={linha} col={coluna})')

    def getToken(self):
        estado = 1
        simbolo = self.getchar()
        lexema = ''
        while simbolo in ['#', ' ', '\t', '\n']:
            # descarta comentarios (que iniciam com # ate o fim da linha)
            if simbolo == '#':  # DEFINIMOS COMENTÁRIOS COMO #
                simbolo = self.getchar()
                while simbolo != '\n':
                    simbolo = self.getchar()
            # descarta linhas brancas e espaços
            while simbolo in [' ', '\t', '\n']:
                simbolo = self.getchar()
        # aqui vai começar a pegar um token...
        lin = self.linha  # onde inicia o token, para msgs
        col = self.coluna  # onde inicia o token, para msgs
        while (True):

            if estado == 1:
                # inicio do automato
                if simbolo.isalpha():
                    estado = 2  # idents, pal.reservadas
                elif simbolo.isdigit():
                    estado = 3  # numeros
                elif simbolo == '"':
                    estado = 4  # strings
                elif simbolo == "(":
                    return (TOKEN.abrePar, "(", lin, col)
                elif simbolo == ")":
                    return (TOKEN.fechaPar, ")", lin, col)
                elif simbolo == ",":
                    return (TOKEN.virg, ",", lin, col)
                elif simbolo == ";":
                    return (TOKEN.ptoVirg, ";", lin, col)
                elif simbolo == "+":
                    return (TOKEN.mais, "+", lin, col)
                elif simbolo == "-":
                    estado = 9
                elif simbolo == "*":
                    return (TOKEN.multiplica, "*", lin, col)
                elif simbolo == "/":
                    return (TOKEN.divide, "/", lin, col)
                elif simbolo == "{":
                    return (TOKEN.abreChave, "{", lin, col)
                elif simbolo == "}":
                    return (TOKEN.fechaChave, "}", lin, col)
                elif simbolo == "[":
                    return (TOKEN.abreCol, "[", lin, col)
                elif simbolo == "]":
                    return (TOKEN.fechaCol, "]", lin, col)
                elif simbolo == "%":
                    return (TOKEN.mod, "%", lin, col)
                elif simbolo == "<":
                    estado = 5  # < ou <=
                elif simbolo == ">":
                    estado = 6  # > ou >=
                elif simbolo == "=":
                    estado = 7  # = ou ==
                elif simbolo == "!":  # !=
                    estado = 8
                elif simbolo == ":":
                    return (TOKEN.doisPto, ":", lin, col)
                elif simbolo == '\0':
                    return (TOKEN.eof, '<eof>', lin, col)
                else:
                    lexema += simbolo
                    return (TOKEN.erro, lexema, lin, col)

            elif estado == 2:
                # identificadores e palavras reservadas
                if simbolo.isalnum():
                    estado = 2
                else:
                    self.ungetchar(simbolo)
                    token = TOKEN.reservada(lexema)
                    return (token, lexema, lin, col)

            elif estado == 3:
                # numeros
                if simbolo.isdigit():
                    estado = 3
                elif simbolo == '.':
                    estado = 31
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.intVal, lexema, lin, col)

            elif estado == 31:
                # parte real do numero
                if simbolo.isdigit():
                    estado = 32
                elif simbolo.isalpha():
                    estado = 33
                else:
                    return (TOKEN.erro, lexema, lin, col)

            elif estado == 32:
                # parte real do numero
                if simbolo.isdigit():
                    estado = 32
                elif simbolo.isalpha() or simbolo == '.':
                    estado = 33
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.floatVal, lexema, lin, col)


            elif estado == 33:
                while not simbolo in TOKEN.tokens_unarios():
                    lexema += simbolo
                    simbolo = self.getchar()

                return (TOKEN.erro, lexema, lin, col)

            elif estado == 4:
                # strings
                while True:
                    if simbolo == '"':
                        lexema += simbolo
                        return (TOKEN.strVal, lexema, lin, col)
                    if simbolo in ['\n', '\0']:
                        return (TOKEN.erro, lexema, lin, col)
                    if simbolo == '\\':  # isso é por causa do python
                        lexema += simbolo
                        simbolo = self.getchar()
                        if simbolo in ['\n', '\0']:
                            return (TOKEN.erro, lexema, lin, col)

                    lexema = lexema + simbolo
                    simbolo = self.getchar()

            elif estado == 5:
                if simbolo == '=':
                    lexema = lexema + simbolo
                else:
                    self.ungetchar(simbolo)

                return (TOKEN.oprel, lexema, lin, col)

            elif estado == 6:
                if simbolo == '=':
                    lexema = lexema + simbolo
                else:
                    self.ungetchar(simbolo)

                return (TOKEN.oprel, lexema, lin, col)

            elif estado == 7:
                if simbolo == '=':
                    lexema += simbolo
                    return (TOKEN.oprel, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.atrib, lexema, lin, col)

            elif estado == 8:
                if simbolo == '=':
                    lexema += simbolo
                    return (TOKEN.oprel, lexema, lin, col)
                else:  # se o proximo simbolo nao for = , quer dizer que tem um ! solto no código
                    self.ungetchar(simbolo)  # eu volto o "ponteiro" pra posicao que eu encontrei a !
                    return (TOKEN.erro, lexema, lin, col)  # retorno o ! dizendo que ele é um erro

            elif estado == 9:
                if simbolo == '>':
                    lexema += simbolo
                    return (TOKEN.seta, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.menos, lexema, lin, col)

            else:
                print('BUG!!!')

            lexema = lexema + simbolo
            simbolo = self.getchar()


# inicia a traducao
if __name__ == '__main__':
    print("Para testar, chame o Tradutor no main.py")
