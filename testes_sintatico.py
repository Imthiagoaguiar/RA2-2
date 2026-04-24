
# testes_sintatico.py — Testes do Analisador Sintático LL(1)

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import (tokenizar_linha, parsear, construirGramatica,
                    gerarArvore, gerarAssembly, _flatten_tokens, lerTokens)

_total = 0
_passou = 0

def checar(descricao, condicao):
    global _total, _passou
    _total += 1
    if condicao:
        _passou += 1
        print(f"  [OK] {descricao}")
    else:
        print(f"  [FALHOU] {descricao}")

def tokenizar(linha):
    return tokenizar_linha(linha)

def parsear_programa(linhas):
    """Helper: tokeniza lista de linhas e parseia."""
    g = construirGramatica()
    toks = []
    for l in linhas:
        t = tokenizar(l)
        if t is not None:
            toks.extend(t)
    arvore, erros = parsear(toks, g)
    return arvore, erros

# Testes Léxicos (tokens válidos e inválidos)

def teste_tokens_validos():
    print("\n--- Tokens válidos ---")
    casos = [
        ("(3.0 2.0 +)", ['LPAREN','NUM','NUM','OP','RPAREN']),
        ("(10 5 /)",     ['LPAREN','NUM','NUM','OP','RPAREN']),
        ("(9.0 3.0 |)",  ['LPAREN','NUM','NUM','OP','RPAREN']),
        ("(2.0 8 ^)",    ['LPAREN','NUM','NUM','OP','RPAREN']),
        ("(5.0 MEM)",    ['LPAREN','NUM','ID','RPAREN']),
        ("(MEM)",        ['LPAREN','ID','RPAREN']),
        ("(3 RES)",      ['LPAREN','NUM','RES','RPAREN']),
        ("(START)",      ['LPAREN','START','RPAREN']),
        ("(END)",        ['LPAREN','END','RPAREN']),
        ("(3.0 2.0 >)",  ['LPAREN','NUM','NUM','RELOP','RPAREN']),
        ("(3.0 2.0 >=)", ['LPAREN','NUM','NUM','RELOP','RPAREN']),
        ("(3.0 2.0 ==)", ['LPAREN','NUM','NUM','RELOP','RPAREN']),
        ("(3.0 2.0 !=)", ['LPAREN','NUM','NUM','RELOP','RPAREN']),
    ]
    for expr, tipos_esperados in casos:
        t = tokenizar(expr)
        tipos = [tk[0] for tk in (t or [])]
        checar(f"'{expr}'", tipos == tipos_esperados)

def teste_tokens_invalidos():
    print("\n--- Tokens inválidos ---")
    checar("número malformado '3.14.5'", tokenizar("(3.14.5 2.0 +)") is None)
    checar("operador inválido '&'",       tokenizar("(3.0 2.0 &)") is None)
    checar("'=' sem par",                 tokenizar("(3.0 2.0 =)") is None)
    checar("'!' sem par",                 tokenizar("(3.0 !)") is None)
    checar("número termina em ponto",     tokenizar("(3. 2.0 +)") is None)

# Testes Sintáticos — programas válidos

def teste_programa_simples():
    print("\n--- Programa simples ---")
    linhas = ["(START)", "(3.0 2.0 +)", "(END)"]
    arvore, erros = parsear_programa(linhas)
    checar("sem erros sintáticos", len(erros) == 0)
    checar("tipo raiz = programa", arvore.get('tipo') == 'programa')

def teste_programa_com_todas_ops():
    print("\n--- Todas as operações ---")
    linhas = [
        "(START)",
        "(3.0 2.0 +)",
        "(3.0 2.0 -)",
        "(3.0 2.0 *)",
        "(3.0 2.0 |)",
        "(6 2 /)",
        "(7 3 %)",
        "(2.0 4 ^)",
        "(END)"
    ]
    _, erros = parsear_programa(linhas)
    checar("sem erros", len(erros) == 0)

def teste_mem_store_load():
    print("\n--- Memória store/load ---")
    linhas = ["(START)", "(42.0 VAR)", "(VAR)", "(END)"]
    arvore, erros = parsear_programa(linhas)
    checar("sem erros", len(erros) == 0)
    bloco = arvore['filhos'][0]
    checar("mem_store presente", any(f.get('tipo') == 'mem_store' for f in bloco['filhos']))
    checar("mem_load presente",  any(f.get('tipo') == 'mem_load'  for f in bloco['filhos']))

def teste_res_ref():
    print("\n--- Comando RES ---")
    linhas = ["(START)", "(5.0 2.0 +)", "(1 RES)", "(END)"]
    _, erros = parsear_programa(linhas)
    checar("sem erros", len(erros) == 0)

def teste_aninhamento():
    print("\n--- Aninhamento ---")
    linhas = ["(START)", "((2.0 3.0 *) (4.0 5.0 *) +)", "(END)"]
    _, erros = parsear_programa(linhas)
    checar("sem erros", len(erros) == 0)

def teste_decisao():
    print("\n--- Decisão IF ---")
    linhas = [
        "(START)",
        "((3.0 2.0 >) ((5.0 1.0 +) (2.0 3.0 *) -) IF)",
        "(END)"
    ]
    arvore, erros = parsear_programa(linhas)
    checar("sem erros", len(erros) == 0)
    bloco = arvore['filhos'][0]
    checar("decisao presente", any(f.get('tipo') == 'decisao' for f in bloco['filhos']))

def teste_laco():
    print("\n--- Laço LOOP ---")
    linhas = [
        "(START)",
        "(3 (2.0 1.0 +) LOOP)",
        "(END)"
    ]
    arvore, erros = parsear_programa(linhas)
    checar("sem erros", len(erros) == 0)
    bloco = arvore['filhos'][0]
    checar("laco presente", any(f.get('tipo') == 'laco' for f in bloco['filhos']))

def teste_laco_com_conteudo():
    print("\n--- Laço com múltiplas instruções ---")
    linhas = [
        "(START)",
        "(4 (3.0 2.0 +) (10.0 5.0 -) LOOP)",
        "(END)"
    ]
    _, erros = parsear_programa(linhas)
    checar("sem erros", len(erros) == 0)

# Testes Sintáticos — erros

def teste_sem_start():
    print("\n--- Erro: sem START ---")
    linhas = ["(3.0 2.0 +)", "(END)"]
    _, erros = parsear_programa(linhas)
    checar("detecta erro", len(erros) > 0)

def teste_sem_end():
    print("\n--- Erro: sem END ---")
    linhas = ["(START)", "(3.0 2.0 +)"]
    _, erros = parsear_programa(linhas)
    checar("detecta erro", len(erros) > 0)

def teste_operador_invalido_sintatico():
    print("\n--- Erro: operador ausente ---")
    # (A B C) — três operandos sem operador
    linhas = ["(START)", "(3.0 2.0 1.0)", "(END)"]
    _, erros = parsear_programa(linhas)
    checar("detecta erro", len(erros) > 0)

# Teste da árvore e Assembly

def teste_gerar_arvore():
    print("\n--- Geração da árvore ---")
    linhas = ["(START)", "(3.0 2.0 +)", "(END)"]
    arvore, _ = parsear_programa(linhas)
    texto = gerarArvore(arvore)
    checar("árvore não vazia", len(texto) > 0)
    checar("contém 'programa'", 'programa' in texto)
    checar("contém 'expr'", 'expr' in texto)

def teste_gerar_assembly():
    print("\n--- Geração de Assembly ---")
    linhas = ["(START)", "(3.0 2.0 +)", "(2.0 4.0 *)", "(END)"]
    arvore, erros = parsear_programa(linhas)
    checar("sem erros sintáticos", len(erros) == 0)
    asm = gerarAssembly(arvore)
    checar("assembly não vazio", len(asm) > 0)
    checar("contém _start",      "_start:" in asm)
    checar("contém VADD.F64",    "VADD.F64" in asm)
    checar("contém VMUL.F64",    "VMUL.F64" in asm)
    checar("contém .data",       ".data" in asm)

def teste_assembly_divisao_real():
    print("\n--- Assembly: divisão real '|' ---")
    linhas = ["(START)", "(9.0 2.0 |)", "(END)"]
    arvore, _ = parsear_programa(linhas)
    asm = gerarAssembly(arvore)
    checar("usa VDIV.F64", "VDIV.F64" in asm)

def teste_assembly_potencia():
    print("\n--- Assembly: potenciação '^' ---")
    linhas = ["(START)", "(2.0 8 ^)", "(END)"]
    arvore, _ = parsear_programa(linhas)
    asm = gerarAssembly(arvore)
    checar("contém loop de potência", "pow_loop" in asm or "loop_start" in asm)

def teste_assembly_decisao():
    print("\n--- Assembly: decisão IF ---")
    linhas = ["(START)", "((3.0 2.0 >) (5.0 1.0 +) IF)", "(END)"]
    arvore, _ = parsear_programa(linhas)
    asm = gerarAssembly(arvore)
    checar("contém branch if_end", "if_end" in asm)

def teste_assembly_laco():
    print("\n--- Assembly: laço LOOP ---")
    linhas = ["(START)", "(3 (2.0 1.0 +) LOOP)", "(END)"]
    arvore, _ = parsear_programa(linhas)
    asm = gerarAssembly(arvore)
    checar("contém loop_start", "loop_start" in asm)
    checar("contém loop_end",   "loop_end" in asm)

# Testes dos arquivos de teste

def teste_arquivos():
    print("\n--- Arquivos de teste ---")
    for nome in ['teste1.txt', 'teste2.txt', 'teste3.txt']:
        caminho = os.path.join(os.path.dirname(__file__), nome)
        if not os.path.exists(caminho):
            checar(f"{nome} existe", False)
            continue
        tpl = lerTokens(caminho)
        checar(f"{nome} tokeniza", tpl is not None and len(tpl) > 0)
        if tpl:
            g = construirGramatica()
            flat = _flatten_tokens(tpl)
            _, erros = parsear(flat, g)
            checar(f"{nome} sem erros sintáticos", len(erros) == 0)

# Runner

def rodar_todos():
    print("=" * 55)
    print("  Testes do Analisador Sintático LL(1)")
    print("=" * 55)

    teste_tokens_validos()
    teste_tokens_invalidos()
    teste_programa_simples()
    teste_programa_com_todas_ops()
    teste_mem_store_load()
    teste_res_ref()
    teste_aninhamento()
    teste_decisao()
    teste_laco()
    teste_laco_com_conteudo()
    teste_sem_start()
    teste_sem_end()
    teste_operador_invalido_sintatico()
    teste_gerar_arvore()
    teste_gerar_assembly()
    teste_assembly_divisao_real()
    teste_assembly_potencia()
    teste_assembly_decisao()
    teste_assembly_laco()
    teste_arquivos()

    print("\n" + "=" * 55)
    print(f"  Resultado: {_passou}/{_total} testes passaram")
    print("=" * 55)
    return _passou == _total

if __name__ == '__main__':
    ok = rodar_todos()
    sys.exit(0 if ok else 1)
