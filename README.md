# Fase 2 — Analisador Sintático LL(1)

**Instituição:** Pontifícia Universidade Católica do Paraná - PUCPR\n
**Disciplina:** Linguagens Formais e Autômatos  
**Professor:** Frank de Alcantara  
**Ano:** 2026  
**Grupo:** RA2 2 (Canvas)

## Integrantes (ordem alfabética)

| Nome | GitHub |
|------|--------|
| Thiago Aguiar Moreira | https://github.com/Imthiagoaguiar|

---

## Descrição

Fase 2 do compilador RPN: implementa um **analisador sintático descendente recursivo LL(1)** para a linguagem RPN estendida com estruturas de controle (`IF` e `LOOP`). Gera a árvore sintática e código Assembly ARMv7 para o [CPUlator DEC1-SOC v16.1](https://cpulator.01xz.net/?sys=arm-de1soc).

---

## Estrutura do Projeto

```
fase2/
├── parser.py                  # Código principal (léxico + sintático + assembly)
├── testes_sintatico.py        # 54 testes automatizados
├── teste1.txt                 # Arquivo de teste 1
├── teste2.txt                 # Arquivo de teste 2
├── teste3.txt                 # Arquivo de teste 3
├── gramatica.md               # Gramática, FIRST/FOLLOW, Tabela LL(1)
├── teste1_arvore.json         # Árvore sintática (última execução)
├── teste1_arvore.txt          # Árvore sintática em texto
├── teste1_output.s            # Assembly gerado (última execução)
└── README.md
```

---

## Como Executar

### Pré-requisitos
- Python 3.8+
- Sem dependências externas

### Executar o compilador

```bash
python3 parser.py teste1.txt
python3 parser.py teste2.txt
python3 parser.py teste3.txt
```

Cada execução gera:
- `<base>_arvore.json` — árvore sintática em JSON
- `<base>_arvore.txt` — árvore sintática em texto
- `<base>_output.s` — Assembly ARMv7 para o CPUlator

### Executar os testes

```bash
python3 testes_sintatico.py
```

---

## Sintaxe da Linguagem

Todo programa deve começar com `(START)` e terminar com `(END)`.

### Operadores Aritméticos

| Sintaxe | Operação |
|---------|----------|
| `(A B +)` | Adição |
| `(A B -)` | Subtração |
| `(A B *)` | Multiplicação |
| `(A B \|)` | Divisão real (IEEE 754 64-bit) |
| `(A B /)` | Divisão inteira |
| `(A B %)` | Resto da divisão inteira |
| `(A B ^)` | Potenciação (B inteiro positivo) |

### Operadores Relacionais

| Sintaxe | Operação |
|---------|----------|
| `(A B >)` | A maior que B |
| `(A B <)` | A menor que B |
| `(A B >=)` | A maior ou igual a B |
| `(A B <=)` | A menor ou igual a B |
| `(A B ==)` | A igual a B |
| `(A B !=)` | A diferente de B |

### Comandos Especiais

| Sintaxe | Descrição |
|---------|-----------|
| `(V MEM)` | Armazena valor `V` na variável `MEM` |
| `(MEM)` | Retorna valor armazenado em `MEM` |
| `(N RES)` | Retorna resultado `N` linhas anteriores |

### Estruturas de Controle

#### Decisão — `IF`
```
(cond bloco IF)
```
Executa `bloco` se `cond` for verdadeiro (≠ 0.0).

**Exemplo:**
```
((3.0 2.0 >) (5.0 1.0 +) IF)
```

#### Laço — `LOOP`
```
(N bloco LOOP)
```
Executa `bloco` exatamente `N` vezes.

**Exemplo:**
```
(3 (2.0 1.0 +) LOOP)
```

### Aninhamento

Expressões podem ser aninhadas sem limite:
```
((2.0 3.0 *) (4.0 5.0 *) +)
```

---

## Usar o Assembly no CPUlator

1. Acesse [https://cpulator.01xz.net/?sys=arm-de1soc](https://cpulator.01xz.net/?sys=arm-de1soc)
2. Cole o conteúdo do arquivo `*_output.s` no editor
3. Clique **Compile and Load**
4. Clique **Continue**
5. Verifique os resultados em **Memory → res_history**

---

## Documentação Técnica

Ver [`gramatica.md`](gramatica.md) para:
- Regras de produção completas (EBNF)
- Conjuntos FIRST e FOLLOW
- Tabela de análise LL(1)
- Exemplo de árvore sintática
