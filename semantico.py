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
        self.operacoes_validas = {
            ((TOKEN.INT, False), TOKEN.mais, (TOKEN.INT, False)): (TOKEN.INT, False),
            ((TOKEN.INT, False), TOKEN.menos, (TOKEN.INT, False)): (TOKEN.INT, False),
            ((TOKEN.INT, False), TOKEN.multiplica, (TOKEN.INT, False)): (TOKEN.INT, False),
            ((TOKEN.INT, False), TOKEN.divide, (TOKEN.INT, False)): (TOKEN.INT, False),
            ((TOKEN.INT, False), TOKEN.oprel, (TOKEN.INT, False)): (TOKEN.INT, False),

            ((TOKEN.INT, False), TOKEN.mais, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.INT, False), TOKEN.menos, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.INT, False), TOKEN.multiplica, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.INT, False), TOKEN.divide, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.INT, False), TOKEN.oprel, (TOKEN.FLOAT, False)): (TOKEN.INT, False),

            ((TOKEN.FLOAT, False), TOKEN.mais, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.FLOAT, False), TOKEN.menos, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.FLOAT, False), TOKEN.multiplica, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.FLOAT, False), TOKEN.divide, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
            ((TOKEN.FLOAT, False), TOKEN.oprel, (TOKEN.FLOAT, False)): (TOKEN.INT, False),

            ((TOKEN.STRING, False), TOKEN.mais, (TOKEN.STRING, False)): (TOKEN.STRING, False),

            # Add operations for list types
            ((TOKEN.INT, True), TOKEN.oprel, (TOKEN.INT, True)): (TOKEN.INT, False),
            ((TOKEN.FLOAT, True), TOKEN.oprel, (TOKEN.FLOAT, True)): (TOKEN.INT, False),
            ((TOKEN.STRING, True), TOKEN.oprel, (TOKEN.STRING, True)): (TOKEN.INT, False),
        }

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

    def consulta(self, token_atual):
        (token, nome, linha, coluna) = token_atual
        for escopo in self.tabelaSimbolos:
            if nome in escopo:
                return escopo[nome]
        msg = f'Variavel {nome} nao declarada'
        self.erroSemantico(token_atual, msg)

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

    def escopo_atual(self):
        return self.tabelaSimbolos[0]

    def checa_operacao(self, token_src, oprel, token_tgt):
        """
        Verifica se uma operação entre dois tipos é válida e retorna o tipo resultante.
        Se a operação não for válida, retorna None.

        Args:
            token_src: Tupla (tipo, is_list) do primeiro operando
            oprel: Token do operador
            token_tgt: Tupla (tipo, is_list) do segundo operando

        Returns:
            Tupla (tipo, is_list) do resultado ou None se operação inválida
        """
        # Verifica a operação direta
        result = self.operacoes_validas.get((token_src, oprel, token_tgt))
        if result is not None:
            return result

        # Verifica a operação com argumentos invertidos
        result = self.operacoes_validas.get((token_tgt, oprel, token_src))
        if result is not None:
            return result

        # Se chegou aqui, a operação é inválida
        return None

    def verifica_compatibilidade(self, token_atual, tipo_src, tipo_tgt):
        """
        Verifica se dois tipos são compatíveis para atribuição/comparação
        e lança erro semântico se não forem.

        Args:
            token_atual: Token atual para mensagem de erro
            tipo_src: Tupla (tipo, is_list) da origem
            tipo_tgt: Tupla (tipo, is_list) do destino
        """
        if tipo_src is not None and tipo_tgt[0] is None and tipo_tgt[1] == True and tipo_tgt[1] == tipo_src[1]:
            return

        if tipo_src != tipo_tgt:
            (_, lexema, _, _) = token_atual
            msg = f'Tipos incompatíveis na operação com {lexema}: ' \
                  f'esperado {tipo_tgt[0]} mas recebeu {TOKEN.msg(tipo_src[0])}'
            if tipo_tgt[1] != tipo_src[1]:
                msg += f' (um é lista e outro não)'
            # else:
            #     return
            self.erroSemantico(token_atual, msg)

    def tipo_retorno_atual(self):
        """
        Retorna o tipo de retorno esperado da função atual.
        Para funções regulares, retorna o último tipo da lista de tipos.
        Para funções void (sem retorno), retorna (None, False).

        Returns:
            Tupla (tipo, is_list) do tipo de retorno esperado da função atual
        """
        escopo_global = self.tabelaSimbolos[-1]  # pega o escopo global
        escopo_atual = self.tabelaSimbolos[0]  # pega o escopo da função atual

        # Procura a função atual no escopo global
        for nome, tipo in escopo_global.items():
            # Se é uma função e está no escopo atual (mesmos símbolos)
            if (tipo[0] == TOKEN.FUNCTION and
                    nome in escopo_atual):
                # Retorna o último tipo da lista de tipos (tipo de retorno)
                return tipo[1][-1]

        # Se não encontrou a função ou não está em um contexto de função
        return (None, False)