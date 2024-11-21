# ---------------------------------------------------
# Tradutor para a linguagem B-A-BA
#
# versao 1a (out-2024)
# ---------------------------------------------------

from enum import IntEnum


class TOKEN(IntEnum):
    erro = 1
    eof = 2
    ident = 3
    intVal = 4
    STRING = 5
    IF = 6
    ELSE = 7
    BEGIN = 8
    END = 9
    abrePar = 10
    fechaPar = 11
    virg = 12
    ptoVirg = 13
    oprel = 14
    AND = 15
    OR = 16
    NOT = 17
    mais = 18
    menos = 19
    multiplica = 20
    divide = 21
    READ = 22
    WRITE = 23
    abreChave = 24
    fechaChave = 25
    atrib = 26
    THEN = 27
    FUNCTION = 28
    seta = 29
    doisPto = 30
    abreCol = 31
    fechaCol = 32
    RETURN = 33
    LIST = 34
    LEN = 35
    floatVal = 36
    strVal = 37
    INT = 38
    FLOAT = 39
    FOR = 40
    IN = 41
    DO = 42
    RANGE = 43
    WHILE = 44
    mod = 45

    @classmethod
    def msg(cls, token):
        nomes = {
            1: 'erro',
            2: '<eof>',
            3: 'ident',
            4: 'intVal',
            5: 'string',
            6: 'if',
            7: 'else',
            8: 'begin',
            9: 'end',
            10: '(',
            11: ')',
            12: ',',
            13: ';',
            14: 'oprel',
            15: 'and',
            16: 'or',
            17: 'not',
            18: '+',
            19: '_',
            20: '*',
            21: '/',
            22: 'read',
            23: 'write',
            24: '{',
            25: '}',
            26: '=',
            27: 'then',
            28: 'function',
            29: '->',
            30: ':',
            31: '[',
            32: ']',
            33: 'return',
            34: 'list',
            35: 'len',
            36: 'floatVal',
            37: 'strVal',
            38: 'int',
            39: 'float',
            40: 'for',
            41: 'in',
            42: 'do',
            43: 'range',
            44: 'while',
            45: '%',
        }
        return nomes[token]

    @classmethod
    def reservada(cls, lexema):
        reservadas = {
            'if': TOKEN.IF,
            'begin': TOKEN.BEGIN,
            'end': TOKEN.END,
            'else': TOKEN.ELSE,
            'read': TOKEN.READ,
            'write': TOKEN.WRITE,
            'and': TOKEN.AND,
            'or': TOKEN.OR,
            'not': TOKEN.NOT,
            'then': TOKEN.THEN,
            'function': TOKEN.FUNCTION,
            'return': TOKEN.RETURN,
            'list': TOKEN.LIST,
            'int': TOKEN.INT,
            'float': TOKEN.FLOAT,
            'for': TOKEN.FOR,
            'in': TOKEN.IN,
            'do': TOKEN.DO,
            'range': TOKEN.RANGE,
            'while': TOKEN.WHILE,
            'string': TOKEN.STRING
        }
        if lexema in reservadas:
            return reservadas[lexema]
        else:
            return TOKEN.ident

    @classmethod
    def tokens_unarios(cls):
        return ['(', ')', ',', '<', '>', ';', ' ', '\n', '=', '{', '}', '/', '*', '-', '+', '[', ']', ':', '%', '!', '\t']

    @classmethod
    def tokens_tipo(cls):
        return [TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING]

    @classmethod
    def tokens_tipo_valor(cls):
        return [TOKEN.intVal, TOKEN.floatVal, TOKEN.strVal]
