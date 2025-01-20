#---------------------------------------------------
# Tradutor para a linguagem B-A-BA
#---------------------------------------------------

from lexico import TOKEN
from semantico import Semantico


class Sintatico:

    def __init__(self, lexico):
        self.lexico = lexico
        self.semantico = Semantico("saida.out")

    def traduz(self):
        self.tokenLido = self.lexico.getToken()

        try:
            self.prog()
            print('Traduzido com sucesso.')
        except:
            pass

    def consome(self, tokenAtual):
        (token, lexema, linha, coluna) = self.tokenLido
        if tokenAtual == token:
            self.tokenLido = self.lexico.getToken()
        else:
            msgTokenLido = TOKEN.msg(token)
            msgTokenAtual = TOKEN.msg(tokenAtual)
            print(f'Erro na linha {linha}, coluna {coluna}:')
            if token == TOKEN.erro:
                msg = lexema
            else:
                msg = msgTokenLido
            print(f'Era esperado {msgTokenAtual} mas veio {msg}')
            raise Exception

    def testaLexico(self):
        self.tokenLido = self.lexico.getToken()
        (token, lexema, linha, coluna) = self.tokenLido
        while token != TOKEN.eof:
            self.lexico.imprimeToken(self.tokenLido)
            self.tokenLido = self.lexico.getToken()
            (token, lexema, linha, coluna) = self.tokenLido

#-------- segue a gramatica -----------------------------------------
    def prog(self):
        # <prog> -> <funcao> <RestoFuncoes>

        self.funcao()
        self.resto_funcoes()

        for chave, valor in self.semantico.escopo_atual().items():
            print(f'Escopo Global -> {chave}: {valor}')

        self.consome(TOKEN.eof)

    def funcao(self):
        # <funcao> -> function ident ( <params> ) <tipoResultado> <corpo>
        self.consome(TOKEN.FUNCTION)
        token = self.tokenLido
        self.consome(TOKEN.ident)
        self.consome(TOKEN.abrePar)
        args = self.params()
        self.consome(TOKEN.fechaPar)
        result = self.tipo_resultado()
        types = args + result
        self.semantico.declara(token, (TOKEN.FUNCTION, types))
        self.semantico.iniciaFuncao()

        for p in args:
            (tt, (tipo, info)) = p
            self.semantico.declara(tt, (tipo, info))

        self.corpo()

        for chave, valor in self.semantico.escopo_atual().items():
            print(f'Escopo {token[1]} -> {chave}: {valor}')

        self.semantico.terminaFuncao()

    def resto_funcoes(self):
        # <funcao> <RestoFuncoes> | LAMBDA
        if self.tokenLido[0] == TOKEN.FUNCTION:
            self.funcao()
            self.resto_funcoes()

    def tipo_resultado(self):
        # <tipoResultado> -> LAMBDA | -> <tipo>
        if self.tokenLido[0] == TOKEN.seta:
            self.consome(TOKEN.seta)
            tipo = self.tipo()
        else:
            tipo = (None, False)

        return [tipo]


    def corpo(self):
        # <corpo> -> begin <declaracoes> <calculo> end
        self.consome(TOKEN.BEGIN)
        self.declaracoes()
        self.calculo()
        self.consome(TOKEN.END)

    def params(self):
        if self.tokenLido[0] in TOKEN.tokens_tipo():
            tipo = self.tipo()
            token = self.tokenLido
            self.consome(TOKEN.ident)
            param_type = (token, tipo)
            params = self.resto_params()
            args_types = [param_type] + params
            return args_types
        else:
            return []

    def resto_params(self):
        # <restoParams> -> LAMBDA |, <tipo> ident <restoParams>
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            param_type = self.tipo()
            self.consome(TOKEN.ident)
            resto = self.resto_params()
            return [param_type] + resto
        else:
            return []

    def tipo(self):
        if self.tokenLido[0] == TOKEN.STRING:
            tipo = TOKEN.STRING
            self.consome(TOKEN.STRING)
        elif self.tokenLido[0] == TOKEN.FLOAT:
            tipo = TOKEN.FLOAT
            self.consome(TOKEN.FLOAT)
        else:
            tipo = TOKEN.INT
            self.consome(TOKEN.INT)

        return tipo, self.opc_lista()

    def declaracoes(self):
        if self.tokenLido[0] in TOKEN.tokens_tipo():
            self.declara()
            self.declaracoes()

    def declara(self):
        # <declara> -> <tipo> <idents> ;
        tipo = self.tipo()
        tokens = self.idents()
        self.consome(TOKEN.ptoVirg)

        for token in tokens:
            self.semantico.declara(token, tipo)

    def idents(self):
        if self.tokenLido[0] == TOKEN.ident:
            token = self.tokenLido
            self.consome(TOKEN.ident)
            tokens = self.resto_idents()
            return [token] + tokens

    def resto_idents(self):
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            token = self.tokenLido
            self.consome(TOKEN.ident)
            return [token] + self.resto_idents()
        else:
            return []

    def opc_lista(self):
        if self.tokenLido[0] not in [TOKEN.BEGIN, TOKEN.ident]:
            self.consome(TOKEN.abreCol)
            self.consome(TOKEN.LIST)
            self.consome(TOKEN.fechaCol)

            return True

        return False

    def calculo(self):
        if self.tokenLido[0] not in [TOKEN.fechaChave, TOKEN.END]:
            self.com()
            self.calculo()

    def com(self):
        # <com> -> <atrib> | <if> | <leitura> | <escrita> | <bloco> | <for> | <while> | <retorna> | <call>;
        token = self.tokenLido[0]

        if token == TOKEN.abreChave:
            self.bloco()
        elif token == TOKEN.IF:
            self.se()
        elif token == TOKEN.READ:
            self.leitura()
        elif token == TOKEN.WRITE:
            self.impressao()
        elif token == TOKEN.FOR:
            self.para()
        elif token == TOKEN.WHILE:
            self.enquanto()
        elif token == TOKEN.ident:
            token = self.semantico.consulta(self.tokenLido)

            if token[0] == TOKEN.FUNCTION:
                self.call()
                self.consome(TOKEN.ptoVirg)
            else:
                self.atrib()
        else:
            self.retorna()

    def call(self):
        # <call> -> ident ( <lista_outs> )
        token_func = self.tokenLido
        self.consome(TOKEN.ident)
        tipo_func = self.semantico.consulta(token_func)

        if tipo_func[0] != TOKEN.FUNCTION:
            self.semantico.erroSemantico(token_func, f"{token_func[1]} não é uma função")

        self.consome(TOKEN.abrePar)
        tipos_args = self.lista_outs()
        self.consome(TOKEN.fechaPar)

        # Verifica se os argumentos correspondem aos parâmetros da função
        args_esperados = tipo_func[1][:-1]  # todos exceto o tipo de retorno
        if len(tipos_args) != len(args_esperados):
            self.semantico.erroSemantico(token_func,
                                         f"Número incorreto de argumentos para {token_func[1]}. Esperado {len(args_esperados)}, recebido {len(tipos_args)}")

        for i, (tipo_arg, tipo_esperado) in enumerate(zip(tipos_args, args_esperados)):
            self.semantico.verifica_compatibilidade(token_func, tipo_arg, tipo_esperado)

        return tipo_func[1][-1]

    def para(self):
        self.consome(TOKEN.FOR)
        token_var = self.tokenLido
        self.consome(TOKEN.ident)
        tipo_var = self.semantico.consulta(token_var)

        self.consome(TOKEN.IN)
        tipo_faixa = self.faixa()

        # Verifica compatibilidade entre variável de iteração e elementos da faixa
        self.semantico.verifica_compatibilidade(token_var, tipo_faixa, tipo_var)

        self.consome(TOKEN.DO)
        self.com()

    def enquanto(self):
        self.consome(TOKEN.WHILE)
        self.consome(TOKEN.abrePar)
        tipo_cond = self.exp()

        # Verifica se a condição é booleana
        if tipo_cond != (TOKEN.INT, False):
            self.semantico.erroSemantico(self.tokenLido, "Condição do while deve ser uma expressão booleana")

        self.consome(TOKEN.fechaPar)
        self.com()

    def retorna(self):
        # <retorna> -> return <expOpc>;
        self.consome(TOKEN.RETURN)

        # Obtém o tipo de retorno esperado da função atual
        tipo_esperado = self.semantico.tipo_retorno_atual()

        # Se não há tipo de retorno esperado mas há expressão, erro
        if tipo_esperado[0] is None:
            if self.tokenLido[0] not in [TOKEN.ptoVirg]:
                self.semantico.erroSemantico(self.tokenLido, "Função void não deve retornar valor")
            self.exp_opc()
            self.consome(TOKEN.ptoVirg)
            return

        # Se há tipo de retorno esperado mas não há expressão, erro
        if self.tokenLido[0] == TOKEN.ptoVirg:
            self.semantico.erroSemantico(self.tokenLido,
                                         f"Função deve retornar valor do tipo {TOKEN.msg(tipo_esperado[0])}")

        tipo_retornado = self.exp_opc()

        # Se há expressão, verifica compatibilidade com tipo esperado
        if tipo_retornado:
            self.semantico.verifica_compatibilidade(self.tokenLido, tipo_retornado, tipo_esperado)

        self.consome(TOKEN.ptoVirg)

    def faixa(self):
        if self.tokenLido[0] == TOKEN.ident:
            return self.lista()
        else:
            self.consome(TOKEN.RANGE)
            self.consome(TOKEN.abrePar)
            tipo_inicio = self.exp()

            # Início do range deve ser inteiro
            if tipo_inicio != (TOKEN.INT, False):
                self.semantico.erroSemantico(self.tokenLido, "Início do range deve ser inteiro")

            self.consome(TOKEN.virg)
            tipo_fim = self.exp()

            # Fim do range deve ser inteiro
            if tipo_fim != (TOKEN.INT, False):
                self.semantico.erroSemantico(self.tokenLido, "Fim do range deve ser inteiro")

            if self.opc_range():
                tipo_passo = self.exp()
                # Passo do range deve ser inteiro
                if tipo_passo != (TOKEN.INT, False):
                    self.semantico.erroSemantico(self.tokenLido, "Passo do range deve ser inteiro")

            self.consome(TOKEN.fechaPar)
            return (TOKEN.INT, False)

    def nao(self):
        # <not> -> not <nao> | <rel>
        token = self.tokenLido[0]

        if token == TOKEN.NOT:
            token_op = self.tokenLido
            self.consome(TOKEN.NOT)
            tipo = self.nao()

            # Verifica se o tipo é compatível com operação NOT (deve ser booleano/int)
            if tipo != (TOKEN.INT, False):
                self.semantico.erroSemantico(token_op, "Operação NOT requer operando booleano")
            return tipo
        else:
            return self.rel()

    def lista(self):
        # <lista> -> ident <opcIndice> | [ <elemLista> ]
        if self.tokenLido[0] == TOKEN.ident:
            token = self.tokenLido
            self.consome(TOKEN.ident)
            tipo = self.semantico.consulta(token)
            tem_indice = self.opc_indice()

            # Se acessou índice em tipo não-lista, erro
            if tem_indice and not tipo[1]:
                self.semantico.erroSemantico(token, f"Tentativa de acessar índice em variável não-lista")

            return tipo
        else:
            self.consome(TOKEN.abreCol)
            tipo_base = self.elemento_lista()
            self.consome(TOKEN.fechaCol)
            return (tipo_base[0], True)  # Retorna como lista

    def opc_indice(self):
        # <opcIndice> -> LAMBDA | [ <exp> <restoIndice> ]
        if self.tokenLido[0] == TOKEN.abreCol:
            self.consome(TOKEN.abreCol)
            tipo_indice = self.exp()

            # Índice deve ser inteiro
            if tipo_indice != (TOKEN.INT, False):
                self.semantico.erroSemantico(self.tokenLido, "Índice deve ser inteiro")

            self.resto_indice()
            self.consome(TOKEN.fechaCol)
            return True
        return False

    def resto_indice(self):
        # <restoIndice> -> LAMBDA | : <exp>
        if self.tokenLido[0] == TOKEN.doisPto:
            self.consome(TOKEN.doisPto)
            tipo_indice = self.exp()

            # Índice do slice também deve ser inteiro
            if tipo_indice != (TOKEN.INT, False):
                self.semantico.erroSemantico(self.tokenLido, "Índice de slice deve ser inteiro")

    def elemento_lista(self):
        if self.tokenLido[0] in TOKEN.tokens_valor():
            tipo = self.elemento()
            tipos_resto = self.resto_elem_lista()

            # Verifica se todos os elementos são do mesmo tipo
            for tipo_elem in tipos_resto:
                if tipo != tipo_elem:
                    self.semantico.erroSemantico(self.tokenLido, "Elementos da lista devem ser do mesmo tipo")

            return tipo
        return None

    def elemento(self):
        if self.tokenLido[0] == TOKEN.intVal:
            self.consome(TOKEN.intVal)
            return (TOKEN.INT, False)
        elif self.tokenLido[0] == TOKEN.floatVal:
            self.consome(TOKEN.floatVal)
            return (TOKEN.FLOAT, False)
        elif self.tokenLido[0] == TOKEN.strVal:
            self.consome(TOKEN.strVal)
            return (TOKEN.STRING, False)
        else:
            token = self.tokenLido
            self.consome(TOKEN.ident)
            return self.semantico.consulta(token)

    def resto_elem_lista(self):
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            tipo = self.elemento()
            tipos_resto = self.resto_elem_lista()
            return [tipo] + tipos_resto
        else:
            return []

    def opc_range(self):
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            self.exp()

    def exp_opc(self):
        # <expOpc> -> LAMBDA | <exp>
        if self.tokenLido[0] not in [TOKEN.ptoVirg]:
            return self.exp()
        return None

    def atrib(self):
        # <atrib> -> ident <opcIndice> = <exp> ;
        token_var = self.tokenLido  # guarda o token da variável
        self.consome(TOKEN.ident)
        tipo_var = self.semantico.consulta(token_var)  # tipo da variável
        tem_indice = self.opc_indice()
        self.consome(TOKEN.atrib)
        tipo_exp = self.exp()  # pega o tipo da expressão

        # Verifica compatibilidade entre tipo da variável e expressão
        self.semantico.verifica_compatibilidade(token_var, tipo_exp, tipo_var)

        self.consome(TOKEN.ptoVirg)

    def leitura(self):
        # <leitura> -> read ( strVal , ident ) ;
        self.consome(TOKEN.READ)
        self.consome(TOKEN.abrePar)
        self.consome(TOKEN.strVal)
        self.consome(TOKEN.virg)
        self.consome(TOKEN.ident)
        self.consome(TOKEN.fechaPar)
        self.consome(TOKEN.ptoVirg)


    def impressao(self):
        # <impressao> -> write ( <lista_out> ) ;
        self.consome(TOKEN.WRITE)
        self.consome(TOKEN.abrePar)
        self.lista_outs()
        self.consome(TOKEN.fechaPar)
        self.consome(TOKEN.ptoVirg)

    def lista_outs(self):
        # <lista_outs> -> <out> <restoLista_outs>
        tipo_out = self.out()
        tipos_resto = self.resto_lista_outs()
        return [tipo_out] + tipos_resto if tipos_resto else [tipo_out]

    def out(self):
        # <out> -> <folha>
        return self.folha()

    def resto_lista_outs(self):
        # <restoLista_outs> -> LAMBDA | , <out> <restoLista_outs>
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            tipo_out = self.out()
            tipos_resto = self.resto_lista_outs()
            return [tipo_out] + tipos_resto if tipos_resto else [tipo_out]
        return []

    def se(self):
        # <if> -> if ( <exp> ) then <com> <else_opc>
        self.consome(TOKEN.IF)
        self.consome(TOKEN.abrePar)
        tipo_cond = self.exp()

        # Verifica se a condição é booleana (resultado de operação relacional)
        if tipo_cond != (TOKEN.INT, False):  # assumindo que booleano é representado como INT
            self.semantico.erroSemantico(self.tokenLido, "Condição do if deve ser uma expressão booleana")

        self.consome(TOKEN.fechaPar)
        self.consome(TOKEN.THEN)
        self.com()
        self.else_opc()

    def else_opc(self):
        # <else_opc> -> LAMBDA | else <com>
        if self.tokenLido[0] == TOKEN.ELSE:
            self.consome(TOKEN.ELSE)
            self.com()
        else:
            pass

    def bloco(self):
        # <bloco> -> { <calculo> }
        self.consome(TOKEN.abreChave)
        self.calculo()
        self.consome(TOKEN.fechaChave)

    def exp(self):
        # <exp> -> <or>
        return self.disj()

    def disj(self):
        # <disj> -> <conj> <resto_disj>
        tipo_conj = self.conj()
        return self.resto_disj(tipo_conj)

    def resto_disj(self, tipo_esq):
        # <restoOr> -> LAMBDA | or <conj> <resto_disj>
        token = self.tokenLido[0]

        if token == TOKEN.OR:
            token_op = self.tokenLido
            self.consome(TOKEN.OR)
            tipo_dir = self.conj()

            # Verifica se os tipos são compatíveis com operação OR
            tipo_res = self.semantico.checa_operacao(tipo_esq, TOKEN.OR, tipo_dir)
            if tipo_res is None:
                self.semantico.erroSemantico(token_op, f"Operação OR inválida entre os tipos")

            return self.resto_disj(tipo_res)
        return tipo_esq

    def conj(self):
        # <conj> -> <nao> <resto_conj>
        tipo_nao = self.nao()
        return self.resto_conj(tipo_nao)

    def resto_conj(self, tipo_esq):
        # <restoConj> -> LAMBDA | and <nao> <resto_conj>
        token = self.tokenLido[0]

        if token == TOKEN.AND:
            token_op = self.tokenLido
            self.consome(TOKEN.AND)
            tipo_dir = self.nao()

            # Verifica se os tipos são compatíveis com operação AND
            tipo_res = self.semantico.checa_operacao(tipo_esq, TOKEN.AND, tipo_dir)
            if tipo_res is None:
                self.semantico.erroSemantico(token_op, f"Operação AND inválida entre os tipos")

            return self.resto_conj(tipo_res)
        return tipo_esq

    def rel(self):
        # <rel> -> <soma> <restoRel>
        tipo_soma = self.soma()
        return self.resto_rel(tipo_soma)

    def resto_rel(self, tipo_esq):
        token = self.tokenLido[0]

        if token == TOKEN.oprel:
            token_op = self.tokenLido
            self.consome(TOKEN.oprel)
            tipo_dir = self.soma()

            # Verifica se os tipos são compatíveis com operação relacional
            tipo_res = self.semantico.checa_operacao(tipo_esq, TOKEN.oprel, tipo_dir)
            if tipo_res is None:
                self.semantico.erroSemantico(token_op, f"Operação relacional inválida entre os tipos")

            return tipo_res
        return tipo_esq

    def soma(self):
        # <soma> -> <mult> <resto_soma>
        tipo_mult = self.mult()
        return self.resto_soma(tipo_mult)

    def resto_soma(self, tipo_esq):
        # <resto_soma> -> LAMBDA | + <mult> <resto_soma> | - <mult> <resto_soma>
        token = self.tokenLido[0]

        if token in [TOKEN.mais, TOKEN.menos]:
            token_op = self.tokenLido
            self.consome(token)
            tipo_dir = self.mult()

            # Verifica se os tipos são compatíveis com a operação
            tipo_res = self.semantico.checa_operacao(tipo_esq, token, tipo_dir)
            if tipo_res is None:
                op_nome = "soma" if token == TOKEN.mais else "subtração"
                self.semantico.erroSemantico(token_op, f"Operação de {op_nome} inválida entre os tipos")

            return self.resto_soma(tipo_res)
        return tipo_esq

    def mult(self):
        # <mult> -> <uno> <resto_mult>
        tipo_uno = self.uno()
        return self.resto_mult(tipo_uno)

    def uno(self):
        # <uno> -> + <uno> | - <uno> | <folha>
        if self.tokenLido[0] == TOKEN.mais:
            self.consome(TOKEN.mais)
            self.uno()
        elif self.tokenLido[0] == TOKEN.menos:
            self.consome(TOKEN.menos)
            self.uno()
        else:
            self.folha()

    def resto_mult(self, tipo_esq):
        # <restoMult> -> LAMBDA | * <uno> <restoMult> | / <uno> <restoMult> | % <uno> <restoMult>
        if self.tokenLido[0] in [TOKEN.multiplica, TOKEN.divide, TOKEN.mod]:
            token_op = self.tokenLido
            op = self.tokenLido[0]
            self.consome(op)
            tipo_dir = self.uno()

            # Verifica se os tipos são compatíveis com a operação
            tipo_res = self.semantico.checa_operacao(tipo_esq, op, tipo_dir)
            if tipo_res is None:
                op_nome = "multiplicação" if op == TOKEN.multiplica else "divisão" if op == TOKEN.divide else "módulo"
                self.semantico.erroSemantico(token_op, f"Operação de {op_nome} inválida entre os tipos")

            return self.resto_mult(tipo_res)
        return tipo_esq

    def folha(self):
        # <folha> -> intVal | floatVal | strVal | <call> | <lista> | ( <exp> )
        if self.tokenLido[0] == TOKEN.intVal:
            self.consome(TOKEN.intVal)
            return (TOKEN.INT, False)
        elif self.tokenLido[0] == TOKEN.floatVal:
            self.consome(TOKEN.floatVal)
            return (TOKEN.FLOAT, False)
        elif self.tokenLido[0] == TOKEN.strVal:
            self.consome(TOKEN.strVal)
            return (TOKEN.STRING, False)
        elif self.tokenLido[0] == TOKEN.abrePar:
            self.consome(TOKEN.abrePar)
            tipo = self.exp()
            self.consome(TOKEN.fechaPar)
            return tipo
        elif self.tokenLido[0] == TOKEN.ident:
            token = self.tokenLido
            tipo = self.semantico.consulta(token)

            if tipo[0] == TOKEN.FUNCTION:
                return self.call()
            else:
                return self.lista()
        else:
            return self.lista()




if __name__ == '__main__':
    print("Para testar, chame o Tradutor")