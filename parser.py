
# Fase 2 - Analisador Sintático LL(1) + Gerador de Assembly ARMv7
# Integrantes do grupo:
#   Thiago Aguiar Moreira - (https://github.com/Imthiagoaguiar)
# Grupo: RA2 2 (Canvas)
#
# SINTAXE DA LINGUAGEM:
#   Programas começam com (START) e terminam com (END)
#   Expressões RPN:  (A B op)
#   Divisão real:    (A B |)
#   Divisão inteira: (A B /)
#   Decisão:         (cond bloco IF)
#   Laço:            (N bloco LOOP)
#   Memória store:   (V MEM)
#   Memória load:    (MEM)
#   Resultado ant.:  (N RES)

import sys
import json
import os

# léxico — AFD sem regex, cada estado é uma função
OPERADORES_REL = {'>', '<', '=', '!'}

def estado_inicial(texto, pos, tokens):
    if pos >= len(texto):
        return pos, tokens
    c = texto[pos]
    if c in (' ', '\t', '\r'):
        return estado_inicial(texto, pos + 1, tokens)
    if c == '(':
        tokens.append(('LPAREN', '('))
        return estado_inicial(texto, pos + 1, tokens)
    if c == ')':
        tokens.append(('RPAREN', ')'))
        return estado_inicial(texto, pos + 1, tokens)
    if c in ('+', '*', '^', '%', '|'):
        tokens.append(('OP', c))
        return estado_inicial(texto, pos + 1, tokens)
    if c == '-':
        return estado_menos(texto, pos, tokens)
    if c == '/':
        tokens.append(('OP', '/'))
        return estado_inicial(texto, pos + 1, tokens)
    if c == '>':
        return estado_maior(texto, pos, tokens)
    if c == '<':
        return estado_menor(texto, pos, tokens)
    if c == '=':
        return estado_igual(texto, pos, tokens)
    if c == '!':
        return estado_nao(texto, pos, tokens)
    if c.isdigit():
        return estado_numero_inteiro(texto, pos, tokens, '')
    if c == '.':
        return estado_numero_decimal(texto, pos, tokens, '0')
    if c.isupper():
        return estado_identificador(texto, pos, tokens, '')
    raise ValueError(f"Token inválido na posição {pos}: '{c}'")


def estado_menos(texto, pos, tokens):
    tokens.append(('OP', '-'))
    return estado_inicial(texto, pos + 1, tokens)


def estado_maior(texto, pos, tokens):
    if pos + 1 < len(texto) and texto[pos + 1] == '=':
        tokens.append(('RELOP', '>='))
        return estado_inicial(texto, pos + 2, tokens)
    tokens.append(('RELOP', '>'))
    return estado_inicial(texto, pos + 1, tokens)


def estado_menor(texto, pos, tokens):
    if pos + 1 < len(texto) and texto[pos + 1] == '=':
        tokens.append(('RELOP', '<='))
        return estado_inicial(texto, pos + 2, tokens)
    tokens.append(('RELOP', '<'))
    return estado_inicial(texto, pos + 1, tokens)


def estado_igual(texto, pos, tokens):
    if pos + 1 < len(texto) and texto[pos + 1] == '=':
        tokens.append(('RELOP', '=='))
        return estado_inicial(texto, pos + 2, tokens)
    raise ValueError(f"Token inválido '=' sem '=' seguinte na posição {pos}")


def estado_nao(texto, pos, tokens):
    if pos + 1 < len(texto) and texto[pos + 1] == '=':
        tokens.append(('RELOP', '!='))
        return estado_inicial(texto, pos + 2, tokens)
    raise ValueError(f"Token inválido '!' sem '=' seguinte na posição {pos}")


def estado_numero_inteiro(texto, pos, tokens, acumulado):
    if pos >= len(texto):
        tokens.append(('NUM', acumulado))
        return pos, tokens
    c = texto[pos]
    if c.isdigit():
        return estado_numero_inteiro(texto, pos + 1, tokens, acumulado + c)
    if c == '.':
        return estado_numero_ponto(texto, pos + 1, tokens, acumulado + '.')
    tokens.append(('NUM', acumulado))
    return estado_inicial(texto, pos, tokens)


def estado_numero_ponto(texto, pos, tokens, acumulado):
    if pos >= len(texto):
        raise ValueError(f"Número malformado (termina em ponto): '{acumulado}'")
    c = texto[pos]
    if c.isdigit():
        return estado_numero_decimal(texto, pos + 1, tokens, acumulado + c)
    raise ValueError(f"Número malformado: '{acumulado}{c}'")


def estado_numero_decimal(texto, pos, tokens, acumulado):
    if pos >= len(texto):
        tokens.append(('NUM', acumulado))
        return pos, tokens
    c = texto[pos]
    if c.isdigit():
        return estado_numero_decimal(texto, pos + 1, tokens, acumulado + c)
    if c == '.':
        raise ValueError(f"Número malformado (ponto duplo): '{acumulado}.'")
    tokens.append(('NUM', acumulado))
    return estado_inicial(texto, pos, tokens)


def estado_identificador(texto, pos, tokens, acumulado):
    if pos >= len(texto):
        tokens.append((_classifica_id(acumulado), acumulado))
        return pos, tokens
    c = texto[pos]
    if c.isupper():
        return estado_identificador(texto, pos + 1, tokens, acumulado + c)
    tokens.append((_classifica_id(acumulado), acumulado))
    return estado_inicial(texto, pos, tokens)


def _classifica_id(nome):
    # palavras reservadas da linguagem
    kws = {'RES': 'RES', 'IF': 'IF', 'LOOP': 'LOOP', 'START': 'START', 'END': 'END'}
    return kws.get(nome, 'ID')


def tokenizar_linha(linha):
    linha = linha.strip()
    if not linha or linha.startswith('#'):
        return []
    try:
        _, tokens = estado_inicial(linha, 0, [])
        return tokens
    except ValueError as e:
        print(f"[ERRO LÉXICO] {e} | linha: '{linha}'")
        return None


# gramática LL(1)
#
# EBNF (não-terminais minúsculo, terminais MAIÚSCULO):
#   programa    → LPAREN START RPAREN bloco LPAREN END RPAREN
#   bloco       → instrucao bloco | ε
#   instrucao   → expr | cmd_especial | decisao | laco
#   expr        → LPAREN operando operando op RPAREN
#               | LPAREN operando operando RELOP RPAREN
#   operando    → NUM | LPAREN operando operando op RPAREN | mem_load | res_ref
#   op          → OP | RELOP
#   cmd_especial → mem_store | mem_load | res_ref
#   mem_store   → LPAREN NUM ID RPAREN
#   mem_load    → LPAREN ID RPAREN
#   res_ref     → LPAREN NUM RES RPAREN
#   decisao     → LPAREN expr bloco IF RPAREN
#   laco        → LPAREN NUM bloco LOOP RPAREN

def construirGramatica():
    nts = ['programa', 'bloco', 'instrucao', 'expr',
           'operando', 'cmd_especial', 'mem_store',
           'mem_load', 'res_ref', 'decisao', 'laco']

    terminais = ['LPAREN', 'RPAREN', 'START', 'END',
                 'NUM', 'ID', 'OP', 'RELOP', 'RES', 'IF', 'LOOP', '$']

    producoes = {
        'programa':     [['LPAREN', 'START', 'RPAREN', 'bloco', 'LPAREN', 'END', 'RPAREN']],
        'bloco':        [['instrucao', 'bloco'], ['ε']],
        'instrucao':    [['expr'], ['cmd_especial'], ['decisao'], ['laco']],
        'expr':         [['LPAREN', 'operando', 'operando', 'OP', 'RPAREN'],
                         ['LPAREN', 'operando', 'operando', 'RELOP', 'RPAREN']],
        'operando':     [['NUM'], ['expr'], ['mem_load'], ['res_ref']],
        'cmd_especial': [['mem_store'], ['mem_load'], ['res_ref']],
        'mem_store':    [['LPAREN', 'NUM', 'ID', 'RPAREN']],
        'mem_load':     [['LPAREN', 'ID', 'RPAREN']],
        'res_ref':      [['LPAREN', 'NUM', 'RES', 'RPAREN']],
        'decisao':      [['LPAREN', 'expr', 'bloco', 'IF', 'RPAREN']],
        'laco':         [['LPAREN', 'NUM', 'bloco', 'LOOP', 'RPAREN']],
    }

    # FIRST calculado na mão — como nossa linguagem tem tudo começando
    # com LPAREN ficou simples, exceto operando que aceita NUM direto
    first = {
        'programa':     {'LPAREN'},
        'bloco':        {'LPAREN', 'ε'},
        'instrucao':    {'LPAREN'},
        'expr':         {'LPAREN'},
        'operando':     {'NUM', 'LPAREN'},
        'cmd_especial': {'LPAREN'},
        'mem_store':    {'LPAREN'},
        'mem_load':     {'LPAREN'},
        'res_ref':      {'LPAREN'},
        'decisao':      {'LPAREN'},
        'laco':         {'LPAREN'},
    }

    # FOLLOW — calculado seguindo as regras da gramática
    follow = {
        'programa':     {'$'},
        'bloco':        {'LPAREN', 'END', 'IF', 'LOOP', '$'},
        'instrucao':    {'LPAREN', 'END', 'IF', 'LOOP', '$'},
        'expr':         {'LPAREN', 'END', 'IF', 'LOOP', 'OP', 'RELOP', 'RPAREN', '$'},
        'operando':     {'NUM', 'LPAREN', 'OP', 'RELOP'},
        'cmd_especial': {'LPAREN', 'END', 'IF', 'LOOP', '$'},
        'mem_store':    {'LPAREN', 'END', 'IF', 'LOOP', '$'},
        'mem_load':     {'LPAREN', 'END', 'IF', 'LOOP', 'OP', 'RELOP', 'RPAREN', '$'},
        'res_ref':      {'LPAREN', 'END', 'IF', 'LOOP', 'OP', 'RELOP', 'RPAREN', '$'},
        'decisao':      {'LPAREN', 'END', 'IF', 'LOOP', '$'},
        'laco':         {'LPAREN', 'END', 'IF', 'LOOP', '$'},
    }

    gramatica = {
        'nao_terminais': nts,
        'terminais': terminais,
        'producoes': producoes,
        'FIRST': first,
        'FOLLOW': follow,
    }

    gramatica['tabela_ll1'] = _construir_tabela(gramatica)
    return gramatica


def _construir_tabela(g):
    tabela = {nt: {} for nt in g['nao_terminais']}

    tabela['programa']['LPAREN'] = g['producoes']['programa'][0]

    tabela['bloco']['LPAREN'] = g['producoes']['bloco'][0]
    for t in g['FOLLOW']['bloco']:
        if t != 'LPAREN':
            tabela['bloco'][t] = ['ε']

    # instrucao: todas começam com LPAREN, diferenciação é feita por lookahead no parser
    tabela['instrucao']['LPAREN'] = ['LPAREN']

    tabela['expr']['LPAREN'] = g['producoes']['expr'][0]

    tabela['operando']['NUM']    = ['NUM']
    tabela['operando']['LPAREN'] = ['expr']

    tabela['cmd_especial']['LPAREN'] = ['LPAREN']

    tabela['mem_store']['LPAREN'] = g['producoes']['mem_store'][0]
    tabela['mem_load']['LPAREN']  = g['producoes']['mem_load'][0]
    tabela['res_ref']['LPAREN']   = g['producoes']['res_ref'][0]

    tabela['decisao']['LPAREN'] = g['producoes']['decisao'][0]
    tabela['laco']['LPAREN']    = g['producoes']['laco'][0]

    return tabela


def lerTokens(arquivo):
    if not os.path.exists(arquivo):
        print(f"[ERRO] Arquivo não encontrado: '{arquivo}'")
        return None
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            linhas = [l.rstrip('\n') for l in f if l.strip() and not l.strip().startswith('#')]
    except IOError as e:
        print(f"[ERRO] Falha ao ler arquivo: {e}")
        return None

    resultado = []
    for i, linha in enumerate(linhas):
        toks = tokenizar_linha(linha)
        if toks is None:
            print(f"[AVISO] Linha {i+1} ignorada por erro léxico: '{linha}'")
        elif toks:
            resultado.append((i + 1, linha, toks))
    return resultado


class ParserError(Exception):
    def __init__(self, msg, linha=None):
        self.msg = msg
        self.linha = linha
        super().__init__(msg)


class Parser:
    def __init__(self, tokens_flat, gramatica):
        self.tokens = tokens_flat
        self.pos = 0
        self.gramatica = gramatica
        self.erros = []

    def atual(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return ('$', '$')

    def proximo(self, offset=1):
        p = self.pos + offset
        if p < len(self.tokens):
            return self.tokens[p]
        return ('$', '$')

    def consumir(self, tipo_esperado=None):
        tok = self.atual()
        if tipo_esperado and tok[0] != tipo_esperado:
            raise ParserError(
                f"Esperado '{tipo_esperado}', encontrado '{tok[0]}' ('{tok[1]}')"
            )
        self.pos += 1
        return tok

    def parse_programa(self):
        no = {'tipo': 'programa', 'filhos': []}
        try:
            self.consumir('LPAREN')
            self.consumir('START')
            self.consumir('RPAREN')
            no['filhos'].append(self.parse_bloco())
            self.consumir('LPAREN')
            self.consumir('END')
            self.consumir('RPAREN')
        except ParserError as e:
            self.erros.append(e.msg)
        return no

    def parse_bloco(self):
        no = {'tipo': 'bloco', 'filhos': []}
        fim_bloco = {'END', 'IF', 'LOOP', '$'}
        while True:
            tok = self.atual()
            if tok[0] in fim_bloco or tok[0] == '$':
                break
            if tok[0] == 'LPAREN':
                prox = self.proximo()
                if prox[0] == 'END':
                    break
                try:
                    inst = self.parse_instrucao()
                    no['filhos'].append(inst)
                except ParserError as e:
                    self.erros.append(e.msg)
                    self._sincronizar()
            else:
                self.erros.append(f"Token inesperado no bloco: '{tok[1]}' (tipo {tok[0]})")
                self._sincronizar()
        return no

    def parse_instrucao(self):
        # usa lookahead de 2 pra decidir qual regra usar
        tok2 = self.proximo(1)
        tok3 = self.proximo(2)

        if tok2[0] == 'START':
            raise ParserError("START inesperado dentro de bloco")

        if tok2[0] == 'NUM' and tok3[0] == 'LPAREN':
            return self._tentar_laco_ou_expr()

        if tok2[0] == 'NUM':
            if self._tem_keyword_em_nivel('LOOP'):
                return self.parse_laco()
            if tok3[0] == 'RES':
                return self.parse_res_ref()
            if tok3[0] == 'ID':
                return self.parse_mem_store()
            return self.parse_expr()

        if tok2[0] == 'ID' and tok3[0] == 'RPAREN':
            return self.parse_mem_load()

        if self._tem_keyword_em_nivel('IF'):
            return self.parse_decisao()

        return self.parse_expr()

    def _tem_keyword_em_nivel(self, kw):
        nivel = 0
        p = self.pos
        while p < len(self.tokens):
            t = self.tokens[p]
            if t[0] == 'LPAREN':
                nivel += 1
            elif t[0] == 'RPAREN':
                nivel -= 1
                if nivel == 0:
                    break
            elif t[0] == kw and nivel == 1:
                return True
            p += 1
        return False

    def _tentar_laco_ou_expr(self):
        if self._tem_keyword_em_nivel('LOOP'):
            return self.parse_laco()
        return self.parse_expr()

    def _sincronizar(self):
        # recuperação de erro: avança até fechar o parêntese atual
        nivel = 0
        while self.pos < len(self.tokens):
            tok = self.tokens[self.pos]
            if tok[0] == 'LPAREN':
                nivel += 1
            elif tok[0] == 'RPAREN':
                if nivel <= 1:
                    self.pos += 1
                    break
                nivel -= 1
            self.pos += 1

    def parse_expr(self):
        no = {'tipo': 'expr', 'filhos': [], 'op': None}
        self.consumir('LPAREN')
        no['filhos'].append(self.parse_operando())
        no['filhos'].append(self.parse_operando())
        tok = self.atual()
        if tok[0] in ('OP', 'RELOP'):
            no['op'] = tok[1]
            self.consumir(tok[0])
        else:
            raise ParserError(f"Esperado operador, encontrado '{tok[1]}' (tipo {tok[0]})")
        self.consumir('RPAREN')
        return no

    def parse_operando(self):
        tok = self.atual()
        if tok[0] == 'NUM':
            self.consumir('NUM')
            return {'tipo': 'num', 'valor': tok[1]}
        if tok[0] == 'ID':
            self.consumir('ID')
            return {'tipo': 'mem_load', 'nome': tok[1]}
        if tok[0] == 'LPAREN':
            prox = self.proximo(1)
            if prox[0] == 'ID' and self.proximo(2)[0] == 'RPAREN':
                return self.parse_mem_load()
            if prox[0] == 'NUM' and self.proximo(2)[0] == 'RES':
                return self.parse_res_ref()
            return self.parse_expr()
        raise ParserError(f"Operando inválido: '{tok[1]}' (tipo {tok[0]})")

    def parse_mem_store(self):
        no = {'tipo': 'mem_store', 'valor': None, 'nome': None}
        self.consumir('LPAREN')
        tok_val = self.consumir('NUM')
        tok_id  = self.consumir('ID')
        self.consumir('RPAREN')
        no['valor'] = tok_val[1]
        no['nome']  = tok_id[1]
        return no

    def parse_mem_load(self):
        no = {'tipo': 'mem_load', 'nome': None}
        self.consumir('LPAREN')
        tok_id = self.consumir('ID')
        self.consumir('RPAREN')
        no['nome'] = tok_id[1]
        return no

    def parse_res_ref(self):
        no = {'tipo': 'res_ref', 'n': None}
        self.consumir('LPAREN')
        tok_n = self.consumir('NUM')
        self.consumir('RES')
        self.consumir('RPAREN')
        no['n'] = tok_n[1]
        return no

    def parse_decisao(self):
        no = {'tipo': 'decisao', 'filhos': []}
        self.consumir('LPAREN')
        no['filhos'].append(self.parse_expr())
        no['filhos'].append(self.parse_bloco())
        self.consumir('IF')
        self.consumir('RPAREN')
        return no

    def parse_laco(self):
        no = {'tipo': 'laco', 'n': None, 'filhos': []}
        self.consumir('LPAREN')
        tok_n = self.consumir('NUM')
        no['n'] = tok_n[1]
        no['filhos'].append(self.parse_bloco())
        self.consumir('LOOP')
        self.consumir('RPAREN')
        return no


def parsear(tokens_flat, gramatica):
    p = Parser(tokens_flat, gramatica)
    arvore = p.parse_programa()
    return arvore, p.erros


def gerarArvore(arvore, indent=0):
    linhas = []
    prefixo = '  ' * indent
    tipo = arvore.get('tipo', '?')

    if tipo == 'programa':
        linhas.append(f"{prefixo}[programa]")
        for f in arvore.get('filhos', []):
            linhas.append(gerarArvore(f, indent + 1))

    elif tipo == 'bloco':
        linhas.append(f"{prefixo}[bloco]")
        for f in arvore.get('filhos', []):
            linhas.append(gerarArvore(f, indent + 1))

    elif tipo == 'expr':
        op = arvore.get('op', '?')
        linhas.append(f"{prefixo}[expr op='{op}']")
        for f in arvore.get('filhos', []):
            linhas.append(gerarArvore(f, indent + 1))

    elif tipo == 'num':
        linhas.append(f"{prefixo}[num valor={arvore.get('valor')}]")

    elif tipo == 'mem_store':
        linhas.append(f"{prefixo}[mem_store {arvore.get('nome')} = {arvore.get('valor')}]")

    elif tipo == 'mem_load':
        linhas.append(f"{prefixo}[mem_load {arvore.get('nome')}]")

    elif tipo == 'res_ref':
        linhas.append(f"{prefixo}[res_ref n={arvore.get('n')}]")

    elif tipo == 'decisao':
        linhas.append(f"{prefixo}[decisao IF]")
        for f in arvore.get('filhos', []):
            linhas.append(gerarArvore(f, indent + 1))

    elif tipo == 'laco':
        linhas.append(f"{prefixo}[laco N={arvore.get('n')}]")
        for f in arvore.get('filhos', []):
            linhas.append(gerarArvore(f, indent + 1))

    else:
        linhas.append(f"{prefixo}[{tipo}]")

    return '\n'.join(l for l in linhas if l.strip())


class GeradorAssembly:

    def __init__(self):
        self.asm = []
        self.constantes = {}
        self.const_cnt = 0
        self.label_cnt = 0
        self.res_history_size = 0
        self.res_idx = 0
        self.vars = set()

    def novo_label(self, prefixo='lbl'):
        self.label_cnt += 1
        return f"{prefixo}_{self.label_cnt}"

    def nova_constante(self, valor_str):
        label = f"cst_{self.const_cnt}"
        self.const_cnt += 1
        self.constantes[label] = valor_str if '.' in valor_str else valor_str + '.0'
        return label

    def emit(self, linha):
        self.asm.append(linha)

    def gerar(self, arvore):
        self._cabecalho()
        if arvore.get('tipo') == 'programa':
            for filho in arvore.get('filhos', []):
                self._gerar_no(filho)
        self._rodape()
        self._secao_dados()
        return '\n'.join(self.asm)

    def _cabecalho(self):
        self.emit(".syntax unified")
        self.emit(".cpu cortex-a9")
        self.emit(".fpu vfpv3-d16")
        self.emit(".text")
        self.emit(".global _start")
        self.emit("")
        self.emit("_start:")
        self.emit("    @ Habilita VFP")
        self.emit("    MRC p15, 0, r0, c1, c0, 2")
        self.emit("    ORR r0, r0, #0xF00000")
        self.emit("    MCR p15, 0, r0, c1, c0, 2")
        self.emit("    MOV r0, #0x40000000")
        self.emit("    FMXR FPEXC, r0")
        self.emit("")
        self.emit("    @ Inicializa ponteiro de pilha RPN")
        self.emit("    LDR r4, =rpn_stack")
        self.emit("    MOV r5, #0              @ r5 = profundidade da pilha RPN")
        self.emit("")

    def _rodape(self):
        self.emit("end_loop:")
        self.emit("    B end_loop")
        self.emit("")

    def _secao_dados(self):
        self.emit(".data")
        self.emit(".align 3")
        tamanho = max(self.res_history_size, 1) * 8
        self.emit(f"res_history: .space {tamanho}  @ histórico de resultados")
        self.emit(".align 3")
        self.emit("rpn_stack: .space 512     @ pilha RPN (64 doubles)")
        for nome in sorted(self.vars):
            self.emit(".align 3")
            self.emit(f"var_{nome.lower()}: .double 0.0  @ variável {nome}")
        self.emit(".align 3")
        for lbl, val in self.constantes.items():
            self.emit(f".align 3")
            self.emit(f"{lbl}: .double {val}")

    def _push_d0(self):
        self.emit("    @ push d0 na pilha RPN")
        self.emit("    LSL r6, r5, #3          @ offset = profundidade * 8")
        self.emit("    LDR r4, =rpn_stack")
        self.emit("    ADD r4, r4, r6")
        self.emit("    VSTR d0, [r4]")
        self.emit("    ADD r5, r5, #1")

    def _pop_d0(self):
        self.emit("    @ pop -> d0")
        self.emit("    SUB r5, r5, #1")
        self.emit("    LSL r6, r5, #3")
        self.emit("    LDR r4, =rpn_stack")
        self.emit("    ADD r4, r4, r6")
        self.emit("    VLDR d0, [r4]")

    def _pop_d1(self):
        self.emit("    @ pop -> d1")
        self.emit("    SUB r5, r5, #1")
        self.emit("    LSL r6, r5, #3")
        self.emit("    LDR r4, =rpn_stack")
        self.emit("    ADD r4, r4, r6")
        self.emit("    VLDR d1, [r4]")

    def _gerar_no(self, no):
        if no is None:
            return
        tipo = no.get('tipo')
        if tipo == 'bloco':
            for f in no.get('filhos', []):
                self._gerar_no(f)
        elif tipo == 'expr':
            self._gerar_expr(no)
            self._salvar_resultado()
        elif tipo == 'mem_store':
            self._gerar_mem_store(no)
            self._salvar_resultado()
        elif tipo == 'mem_load':
            self._gerar_mem_load(no)
            self._salvar_resultado()
        elif tipo == 'res_ref':
            self._gerar_res_ref(no)
            self._salvar_resultado()
        elif tipo == 'decisao':
            self._gerar_decisao(no)
        elif tipo == 'laco':
            self._gerar_laco(no)

    def _salvar_resultado(self):
        offset = self.res_idx * 8
        self.emit(f"    @ salva resultado linha {self.res_idx + 1}")
        self.emit(f"    LDR r0, =res_history")
        self.emit(f"    ADD r0, r0, #{offset}")
        self.emit(f"    VSTR d0, [r0]")
        self.res_idx += 1
        self.res_history_size = self.res_idx
        self.emit("")

    def _gerar_expr(self, no):
        filhos = no.get('filhos', [])
        op = no.get('op', '+')
        self.emit(f"    @ expr op='{op}'")
        self._gerar_operando(filhos[0])
        self._push_d0()
        self._gerar_operando(filhos[1])
        self._push_d0()
        self._pop_d1()  # B
        self._pop_d0()  # A

        if op == '+':
            self.emit("    VADD.F64 d0, d0, d1")
        elif op == '-':
            self.emit("    VSUB.F64 d0, d0, d1")
        elif op == '*':
            self.emit("    VMUL.F64 d0, d0, d1")
        elif op == '|':
            self.emit("    VDIV.F64 d0, d0, d1")
        elif op == '/':
            self._gerar_div_inteira()
        elif op == '%':
            self._gerar_resto()
        elif op == '^':
            self._gerar_potencia()
        elif op in ('>', '<', '>=', '<=', '==', '!='):
            self._gerar_comparacao(op)

    def _gerar_operando(self, no):
        if no is None:
            return
        tipo = no.get('tipo')
        if tipo == 'num':
            lbl = self.nova_constante(no['valor'])
            self.emit(f"    LDR r0, ={lbl}")
            self.emit(f"    VLDR d0, [r0]         @ load {no['valor']}")
        elif tipo == 'expr':
            self._gerar_expr(no)
        elif tipo == 'mem_load':
            self._gerar_mem_load(no)
        elif tipo == 'res_ref':
            self._gerar_res_ref(no)

    def _gerar_mem_store(self, no):
        nome = no['nome']
        valor = no['valor']
        self.vars.add(nome)
        lbl_val = self.nova_constante(valor)
        lbl_var = f"var_{nome.lower()}"
        self.emit(f"    @ store {valor} -> {nome}")
        self.emit(f"    LDR r0, ={lbl_val}")
        self.emit(f"    VLDR d0, [r0]")
        self.emit(f"    LDR r0, ={lbl_var}")
        self.emit(f"    VSTR d0, [r0]")

    def _gerar_mem_load(self, no):
        nome = no['nome']
        self.vars.add(nome)
        lbl_var = f"var_{nome.lower()}"
        self.emit(f"    @ load {nome}")
        self.emit(f"    LDR r0, ={lbl_var}")
        self.emit(f"    VLDR d0, [r0]")

    def _gerar_res_ref(self, no):
        n = int(no['n'])
        idx = max(self.res_idx - n, 0)
        offset = idx * 8
        self.emit(f"    @ RES({n}) — busca resultado {n} linhas atrás")
        self.emit(f"    LDR r0, =res_history")
        self.emit(f"    ADD r0, r0, #{offset}")
        self.emit(f"    VLDR d0, [r0]")

    def _gerar_div_inteira(self):
        lbl_loop = self.novo_label('div_loop')
        lbl_end  = self.novo_label('div_end')
        self.emit("    @ divisão inteira (subtração repetida)")
        self.emit("    VCVT.S32.F64 s0, d0")
        self.emit("    VCVT.S32.F64 s1, d1")
        self.emit("    VMOV r0, s0")
        self.emit("    VMOV r1, s1")
        self.emit("    EOR r3, r0, r1")
        self.emit("    CMP r0, #0")
        self.emit("    RSBLT r0, r0, #0")
        self.emit("    CMP r1, #0")
        self.emit("    RSBLT r1, r1, #0")
        self.emit("    MOV r2, #0")
        self.emit(f"{lbl_loop}:")
        self.emit("    CMP r0, r1")
        self.emit(f"    BLT {lbl_end}")
        self.emit("    SUB r0, r0, r1")
        self.emit("    ADD r2, r2, #1")
        self.emit(f"    B {lbl_loop}")
        self.emit(f"{lbl_end}:")
        self.emit("    CMP r3, #0")
        self.emit("    RSBLT r2, r2, #0")
        self.emit("    VMOV s0, r2")
        self.emit("    VCVT.F64.S32 d0, s0")

    def _gerar_resto(self):
        lbl_loop = self.novo_label('mod_loop')
        lbl_end  = self.novo_label('mod_end')
        self.emit("    @ resto inteiro (subtração repetida)")
        self.emit("    VCVT.S32.F64 s0, d0")
        self.emit("    VCVT.S32.F64 s1, d1")
        self.emit("    VMOV r0, s0")
        self.emit("    VMOV r1, s1")
        self.emit("    CMP r0, #0")
        self.emit("    RSBLT r0, r0, #0")
        self.emit("    CMP r1, #0")
        self.emit("    RSBLT r1, r1, #0")
        self.emit(f"{lbl_loop}:")
        self.emit("    CMP r0, r1")
        self.emit(f"    BLT {lbl_end}")
        self.emit("    SUB r0, r0, r1")
        self.emit(f"    B {lbl_loop}")
        self.emit(f"{lbl_end}:")
        self.emit("    VMOV s0, r0")
        self.emit("    VCVT.F64.S32 d0, s0")

    def _gerar_potencia(self):
        lbl_one  = self.novo_label('pow_one')
        lbl_loop = self.novo_label('pow_loop')
        lbl_end  = self.novo_label('pow_end')
        lbl_cst  = f"cst_one_{self.label_cnt}"
        self.constantes[lbl_cst] = "1.0"
        self.emit("    @ potenciação A^B")
        self.emit("    VMOV.F64 d3, d0           @ base")
        self.emit("    VCVT.S32.F64 s1, d1")
        self.emit("    VMOV r1, s1               @ expoente")
        self.emit(f"    LDR r0, ={lbl_cst}")
        self.emit("    VLDR d2, [r0]             @ acumulador = 1.0")
        self.emit(f"{lbl_loop}:")
        self.emit("    CMP r1, #0")
        self.emit(f"    BLE {lbl_end}")
        self.emit("    VMUL.F64 d2, d2, d3")
        self.emit("    SUB r1, r1, #1")
        self.emit(f"    B {lbl_loop}")
        self.emit(f"{lbl_end}:")
        self.emit("    VMOV.F64 d0, d2")

    def _gerar_comparacao(self, op):
        lbl_true = self.novo_label('cmp_true')
        lbl_end  = self.novo_label('cmp_end')
        lbl_one  = f"cst_cmp1_{self.label_cnt}"
        lbl_zero = f"cst_cmp0_{self.label_cnt}"
        self.constantes[lbl_one]  = "1.0"
        self.constantes[lbl_zero] = "0.0"
        self.emit(f"    @ comparação {op}")
        self.emit("    VCMP.F64 d0, d1")
        self.emit("    VMRS APSR_nzcv, FPSCR")
        branch = {'>':"BGT", '<':"BLT", '>=':"BGE", '<=':"BLE", '==':"BEQ", '!=':"BNE"}[op]
        self.emit(f"    {branch} {lbl_true}")
        self.emit(f"    LDR r0, ={lbl_zero}")
        self.emit("    VLDR d0, [r0]")
        self.emit(f"    B {lbl_end}")
        self.emit(f"{lbl_true}:")
        self.emit(f"    LDR r0, ={lbl_one}")
        self.emit("    VLDR d0, [r0]")
        self.emit(f"{lbl_end}:")

    def _gerar_decisao(self, no):
        lbl_fim = self.novo_label('if_end')
        filhos = no.get('filhos', [])
        self.emit("    @ --- decisao IF ---")
        self._gerar_expr(filhos[0])
        lbl_zero = f"cst_zero_{self.label_cnt}"
        self.constantes[lbl_zero] = "0.0"
        self.emit(f"    LDR r0, ={lbl_zero}")
        self.emit("    VLDR d1, [r0]")
        self.emit("    VCMP.F64 d0, d1")
        self.emit("    VMRS APSR_nzcv, FPSCR")
        self.emit(f"    BEQ {lbl_fim}           @ pula bloco se condição = 0")
        if len(filhos) > 1:
            self._gerar_no(filhos[1])
        self.emit(f"{lbl_fim}:")
        self.emit("")

    def _gerar_laco(self, no):
        n = no.get('n', '1')
        lbl_loop = self.novo_label('loop_start')
        lbl_end  = self.novo_label('loop_end')
        self.emit(f"    @ --- laço LOOP N={n} ---")
        self.emit(f"    MOV r7, #{n}            @ contador de iterações")
        self.emit(f"{lbl_loop}:")
        self.emit(f"    CMP r7, #0")
        self.emit(f"    BLE {lbl_end}")
        filhos = no.get('filhos', [])
        if filhos:
            self._gerar_no(filhos[0])
        self.emit(f"    SUB r7, r7, #1")
        self.emit(f"    B {lbl_loop}")
        self.emit(f"{lbl_end}:")
        self.emit("")


def gerarAssembly(arvore):
    g = GeradorAssembly()
    return g.gerar(arvore)


def _flatten_tokens(tokens_por_linha):
    flat = []
    for _, _, toks in tokens_por_linha:
        flat.extend(toks)
    return flat


def _salvar_arvore(arvore, arquivo):
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(arvore, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Árvore sintática salva em '{arquivo}'")


def _salvar_arvore_texto(texto, arquivo):
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(texto)
    print(f"[INFO] Árvore (texto) salva em '{arquivo}'")


def _salvar_assembly(codigo, arquivo):
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print(f"[INFO] Assembly salvo em '{arquivo}'")


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 parser.py <arquivo.txt>")
        print("Exemplo: python3 parser.py teste1.txt")
        sys.exit(1)

    nome_arquivo = sys.argv[1]
    base = os.path.splitext(os.path.basename(nome_arquivo))[0]

    print(f"[INFO] Lendo '{nome_arquivo}'...")
    tokens_por_linha = lerTokens(nome_arquivo)
    if tokens_por_linha is None:
        sys.exit(1)
    print(f"[INFO] {len(tokens_por_linha)} linha(s) tokenizada(s)")

    print("[INFO] Construindo gramática LL(1)...")
    gramatica = construirGramatica()

    print("[INFO] Parsing...")
    tokens_flat = _flatten_tokens(tokens_por_linha)
    arvore, erros = parsear(tokens_flat, gramatica)

    if erros:
        print(f"\n[ERROS SINTÁTICOS] {len(erros)} erro(s) encontrado(s):")
        for e in erros:
            print(f"  • {e}")
    else:
        print("[INFO] Parsing concluído sem erros.")

    print("[INFO] Gerando árvore sintática...")
    arvore_texto = gerarArvore(arvore)
    print("\n" + arvore_texto)

    _salvar_arvore(arvore, f"{base}_arvore.json")
    _salvar_arvore_texto(arvore_texto, f"{base}_arvore.txt")

    print("[INFO] Gerando Assembly ARMv7...")
    codigo_asm = gerarAssembly(arvore)
    _salvar_assembly(codigo_asm, f"{base}_output.s")

    print(f"\n[INFO] Pronto! Carregue '{base}_output.s' no CPUlator ARMv7 DEC1-SOC (v16.1)")
    print("[INFO] URL: https://cpulator.01xz.net/?sys=arm-de1soc")


if __name__ == '__main__':
    main()
