#---------------------------------------------------
# Tradutor para a linguagem B-A-BA
#---------------------------------------------------

from lexico import TOKEN

class Sintatico:

    def __init__(self, lexico):
        self.lexico = lexico

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
        self.consome(TOKEN.eof)

    def funcao(self):
        # <funcao> -> function ident ( <params> ) <tipoResultado> <corpo>
        if self.tokenLido[0] == TOKEN.FUNCTION:
            self.consome(TOKEN.FUNCTION)
            self.consome(TOKEN.ident)
            self.consome(TOKEN.abrePar)
            self.params()
            self.consome(TOKEN.fechaPar)
            self.tipo_resultado()
            self.corpo()

    def resto_funcoes(self):
        # <funcao> <RestoFuncoes> | LAMBDA
        if self.tokenLido[0] == TOKEN.FUNCTION:
            self.funcao()
            self.resto_funcoes()

    def tipo_resultado(self):
        # <tipoResultado> -> LAMBDA | -> <tipo>
        if self.tokenLido[0] == TOKEN.seta:
            self.consome(TOKEN.seta)
            self.tipo()

    def corpo(self):
        # <corpo> -> begin <declaracoes> <calculo> end
        self.consome(TOKEN.BEGIN)
        self.declaracoes()
        self.calculo()
        self.consome(TOKEN.END)

    def params(self):
        if self.tokenLido[0] in TOKEN.tokens_tipo():
            self.tipo()
            self.consome(TOKEN.ident)
            self.resto_params()

    def resto_params(self):
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            self.tipo()
            self.consome(TOKEN.ident)
            self.resto_params()

    def tipo(self):
        if self.tokenLido[0] == TOKEN.STRING:
            self.consome(TOKEN.STRING)
            self.opc_lista()
        elif self.tokenLido[0] == TOKEN.FLOAT:
            self.consome(TOKEN.FLOAT)
            self.opc_lista()
        else:
            self.consome(TOKEN.INT)
            self.opc_lista()

    def declaracoes(self):
        if self.tokenLido[0] in TOKEN.tokens_tipo():
            self.declara()
            self.declaracoes()

    def declara(self):
        self.tipo()
        self.idents()
        self.consome(TOKEN.ptoVirg)

    def idents(self):
        if self.tokenLido[0] == TOKEN.ident:
            self.consome(TOKEN.ident)
            self.resto_idents()

    def resto_idents(self):
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            self.consome(TOKEN.ident)
            self.resto_idents()

    def opc_lista(self):
        if self.tokenLido[0] not in [TOKEN.BEGIN, TOKEN.ident]:
            self.consome(TOKEN.abreCol)
            self.consome(TOKEN.LIST)
            self.consome(TOKEN.fechaCol)

    def calculo(self):
        if self.tokenLido[0] not in [TOKEN.fechaChave, TOKEN.END]:
            self.com()
            self.calculo()

    def com(self):
        # <com> -> <atrib> | <if> | <leitura> | <escrita> | <bloco> | <for> | <while> | <retorna> | <call>
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
        elif token == TOKEN.RETURN:
            self.retorna()
        else:
            # TODO: Quando ver ident deve consultar a tabela para acionar call ou atrib
            # self.call()
            self.atrib()

    def para(self):
        self.consome(TOKEN.FOR)
        self.consome(TOKEN.ident)
        self.consome(TOKEN.IN)
        self.faixa()
        self.consome(TOKEN.DO)
        self.com()

    def enquanto(self):
        self.consome(TOKEN.WHILE)
        self.consome(TOKEN.abrePar)
        self.exp()
        self.consome(TOKEN.fechaPar)
        self.com()

    def retorna(self):
        # <retorna> -> return <expOpc> ;
        self.consome(TOKEN.RETURN)
        self.exp_opc()
        self.consome(TOKEN.ptoVirg)

    def faixa(self):
        if self.tokenLido[0] == TOKEN.ident:
            self.lista()
        else:
            self.consome(TOKEN.RANGE)
            self.consome(TOKEN.abrePar)
            self.exp()
            self.consome(TOKEN.virg)
            self.exp()
            self.opc_range()
            self.consome(TOKEN.fechaPar)

    def lista(self):
        if self.tokenLido[0] == TOKEN.ident:
            self.consome(TOKEN.ident)
            self.opc_indice()
        else:
            self.consome(TOKEN.abreCol)
            self.elemento_lista()
            self.consome(TOKEN.fechaCol)

    def opc_indice(self):
        if self.tokenLido[0] not in TOKEN.nao_indices():
            self.consome(TOKEN.abreCol)
            self.exp()
            self.resto_indice()
            self.consome(TOKEN.fechaCol)

    def resto_indice(self):
        if self.tokenLido[0] == TOKEN.doisPto:
            self.consome(TOKEN.doisPto)
            self.exp()

    def elemento_lista(self):
        if self.tokenLido[0] in TOKEN.tokens_valor():
            self.elemento()
            self.resto_elem_lista()

    def elemento(self):
        if self.tokenLido[0] == TOKEN.intVal:
            self.consome(TOKEN.intVal)
        elif self.tokenLido[0] == TOKEN.floatVal:
            self.consome(TOKEN.floatVal)
        elif self.tokenLido[0] == TOKEN.strVal:
            self.consome(TOKEN.strVal)
        else:
            self.consome(TOKEN.ident)

    def resto_elem_lista(self):
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            self.elemento()
            self.resto_elem_lista()

    def opc_range(self):
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            self.exp()

    def exp_opc(self):
        # <expOpc> -> LAMBDA | <exp>
        if self.tokenLido[0] not in [TOKEN.ptoVirg]:
            self.exp()

    def atrib(self):
        # <atrib> -> ident = <exp> ;
        self.consome(TOKEN.ident)
        self.consome(TOKEN.atrib)
        self.exp()
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
        self.out()
        self.resto_lista_outs()

    def out(self):
        # <out> -> <folha>
        self.folha()

    def resto_lista_outs(self):
        # <restoLista_outs> -> LAMBDA | , <out> <restoLista_outs>
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            self.out()
            self.resto_lista_outs()

    def se(self):
        # <if> -> if ( <exp> ) then <com> <else_opc>
        self.consome(TOKEN.IF)
        self.consome(TOKEN.abrePar)
        self.exp()
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
        self.disj()

    def disj(self):
        # <disj> -> <conj> <resto_disj>
        self.conj()
        self.resto_disj()

    def resto_disj(self):
        # <restoOr> -> LAMBDA | or <conj> <resto_disj>
        token = self.tokenLido[0]

        if token == TOKEN.OR:
            self.consome(TOKEN.OR)
            self.conj()
            self.resto_disj()

    def conj(self):
        # <conj> -> <nao> <resto_conj>
        self.nao()
        self.resto_conj()

    def resto_conj(self):
        # <restoConj> -> LAMBDA | and <nao> <resto_conj>
        token = self.tokenLido[0]

        if token == TOKEN.AND:
            self.consome(TOKEN.AND)
            self.nao()
            self.resto_conj()

    def nao(self):
        # <not> -> not <nao> | <rel>
        token = self.tokenLido[0]

        if token == TOKEN.NOT:
            self.consome(TOKEN.NOT)
            self.nao()
        else:
            self.rel()

    def rel(self):
        # <rel> -> <uno> <restoRel>
        self.soma()
        self.resto_rel()

    def resto_rel(self):
        token = self.tokenLido[0]

        if token == TOKEN.oprel:
            self.consome(TOKEN.oprel)
            self.soma()

    def soma(self):
        # <soma> -> <mult> <resto_soma>
        self.mult()
        self.resto_soma()

    def resto_soma(self):
        # <resto_soma> -> LAMBDA | + <mult> <resto_soma> | - <mult> <resto_soma>
        token = self.tokenLido[0]

        if token == TOKEN.mais:
            self.consome(TOKEN.mais)
            self.mult()
            self.resto_soma()
        elif token == TOKEN.menos:
            self.consome(TOKEN.menos)
            self.mult()
            self.resto_soma()

    def mult(self):
        # <mult> -> <uno> <resto_mult>
        self.uno()
        self.resto_mult()

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

    def resto_mult(self):
        # <restoMult> -> LAMBDA | / <uno> <restoMult> | * <uno> <restoMult> | % <uno> <restoMult>
        if self.tokenLido[0] == TOKEN.multiplica:
            self.consome(TOKEN.multiplica)
            self.uno()
            self.resto_mult()
        elif self.tokenLido[0] == TOKEN.divide:
            self.consome(TOKEN.divide)
            self.uno()
            self.resto_mult()
        elif self.tokenLido[0] == TOKEN.mod:
            self.consome(TOKEN.mod)
            self.uno()
            self.resto_mult()

    def folha(self):
        # <folha> -> intVal | floatVal | strVal | <call> | <lista> | ( <exp> )
        if self.tokenLido[0] == TOKEN.intVal:
            self.consome(TOKEN.intVal)
        elif self.tokenLido[0] == TOKEN.floatVal:
            self.consome(TOKEN.floatVal)
        elif self.tokenLido[0] == TOKEN.strVal:
            self.consome(TOKEN.strVal)
        elif self.tokenLido[0] == TOKEN.abrePar:
            self.consome(TOKEN.abrePar)
            self.exp()
            self.consome(TOKEN.fechaPar)
        else:
            # TODO: Ajustar no semantico para identificar o que o ident identifica (variável ou funcão)
            self.lista()
            # self.call()



if __name__ == '__main__':
    print("Para testar, chame o Tradutor")