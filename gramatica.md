# Gramática, Conjuntos FIRST/FOLLOW e Tabela LL(1)

## 1. Regras de Produção (EBNF)

> Convenção: não-terminais em minúsculo, terminais em MAIÚSCULO.

```
programa    → LPAREN START RPAREN bloco LPAREN END RPAREN

bloco       → instrucao bloco
            | ε

instrucao   → expr
            | cmd_especial
            | decisao
            | laco

expr        → LPAREN operando operando OP RPAREN
            | LPAREN operando operando RELOP RPAREN

operando    → NUM
            | ID
            | expr
            | mem_load
            | res_ref

cmd_especial → mem_store
             | mem_load
             | res_ref

mem_store   → LPAREN NUM ID RPAREN

mem_load    → LPAREN ID RPAREN

res_ref     → LPAREN NUM RES RPAREN

decisao     → LPAREN expr bloco IF RPAREN

laco        → LPAREN NUM bloco LOOP RPAREN
```

### Terminais

| Terminal | Descrição |
|----------|-----------|
| `LPAREN` | `(` |
| `RPAREN` | `)` |
| `START`  | Keyword de início de programa |
| `END`    | Keyword de fim de programa |
| `NUM`    | Número literal (inteiro ou real) |
| `ID`     | Identificador de variável (letras maiúsculas) |
| `OP`     | Operador aritmético: `+` `-` `*` `\|` `/` `%` `^` |
| `RELOP`  | Operador relacional: `>` `<` `>=` `<=` `==` `!=` |
| `RES`    | Keyword `RES` |
| `IF`     | Keyword `IF` |
| `LOOP`   | Keyword `LOOP` |

---

## 2. Conjuntos FIRST

| Não-terminal | FIRST |
|---|---|
| `programa`     | `{ LPAREN }` |
| `bloco`        | `{ LPAREN, ε }` |
| `instrucao`    | `{ LPAREN }` |
| `expr`         | `{ LPAREN }` |
| `operando`     | `{ NUM, ID, LPAREN }` |
| `cmd_especial` | `{ LPAREN }` |
| `mem_store`    | `{ LPAREN }` |
| `mem_load`     | `{ LPAREN }` |
| `res_ref`      | `{ LPAREN }` |
| `decisao`      | `{ LPAREN }` |
| `laco`         | `{ LPAREN }` |

---

## 3. Conjuntos FOLLOW

| Não-terminal | FOLLOW |
|---|---|
| `programa`     | `{ $ }` |
| `bloco`        | `{ LPAREN, END, IF, LOOP, $ }` |
| `instrucao`    | `{ LPAREN, END, IF, LOOP, $ }` |
| `expr`         | `{ LPAREN, END, IF, LOOP, OP, RELOP, RPAREN, $ }` |
| `operando`     | `{ NUM, ID, LPAREN, OP, RELOP }` |
| `cmd_especial` | `{ LPAREN, END, IF, LOOP, $ }` |
| `mem_store`    | `{ LPAREN, END, IF, LOOP, $ }` |
| `mem_load`     | `{ LPAREN, END, IF, LOOP, OP, RELOP, RPAREN, $ }` |
| `res_ref`      | `{ LPAREN, END, IF, LOOP, OP, RELOP, RPAREN, $ }` |
| `decisao`      | `{ LPAREN, END, IF, LOOP, $ }` |
| `laco`         | `{ LPAREN, END, IF, LOOP, $ }` |

---

## 4. Tabela de Análise LL(1)

| Não-terminal | `LPAREN` | `END` | `IF` | `LOOP` | `NUM` | `ID` | `OP`/`RELOP` | `$` |
|---|---|---|---|---|---|---|---|---|
| `programa`     | `→ (START) bloco (END)` | — | — | — | — | — | — | — |
| `bloco`        | `→ instrucao bloco` | `→ ε` | `→ ε` | `→ ε` | — | — | — | `→ ε` |
| `instrucao`    | ver lookahead² | — | — | — | — | — | — | — |
| `expr`         | `→ (op op OP)` | — | — | — | — | — | — | — |
| `operando`     | `→ expr/mem_load/res_ref` | — | — | — | `→ NUM` | `→ ID` | — | — |
| `mem_store`    | `→ (NUM ID)` | — | — | — | — | — | — | — |
| `mem_load`     | `→ (ID)` | — | — | — | — | — | — | — |
| `res_ref`      | `→ (NUM RES)` | — | — | — | — | — | — | — |
| `decisao`      | `→ (expr bloco IF)` | — | — | — | — | — | — | — |
| `laco`         | `→ (NUM bloco LOOP)` | — | — | — | — | — | — | — |

> ² A instrução iniciada por `LPAREN` é discriminada por lookahead de 2 tokens:
> - `(START` → erro (START fora de posição)
> - `(NUM RES` → `res_ref`
> - `(NUM ID` → `mem_store`
> - `(ID )` → `mem_load`
> - contém `IF` no mesmo nível → `decisao`
> - contém `LOOP` no mesmo nível → `laco`
> - demais → `expr`

---

## 5. Sintaxe das Estruturas de Controle

### 5.1 Tomada de Decisão — `IF`

```
(cond bloco IF)
```

- `cond` é uma expressão relacional que resulta em `1.0` (verdadeiro) ou `0.0` (falso)
- `bloco` é uma sequência de instruções executada se `cond ≠ 0.0`
- Estilo RPN puro: a condição vem antes do bloco, o operador `IF` vem por último

**Exemplo:**
```
((3.0 2.0 >) (5.0 1.0 +) IF)
```
Executa `(5.0 1.0 +)` se `3.0 > 2.0`.

### 5.2 Laço de Repetição — `LOOP`

```
(N bloco LOOP)
```

- `N` é um inteiro positivo indicando o número de repetições
- `bloco` é a sequência de instruções repetida `N` vezes
- Estilo RPN puro: o contador vem antes do bloco, o operador `LOOP` vem por último

**Exemplo:**
```
(3 (2.0 1.0 +) LOOP)
```
Executa `(2.0 1.0 +)` três vezes.

---

## 6. Exemplo de Árvore Sintática

Para o programa:
```
(START)
(3.0 2.0 +)
(5.0 VAR)
((VAR 2.0 >) (VAR 3.0 *) IF)
(END)
```

```
[programa]
  [bloco]
    [expr op='+']
      [num valor=3.0]
      [num valor=2.0]
    [mem_store VAR = 5.0]
    [decisao IF]
      [expr op='>']
        [mem_load VAR]
        [num valor=2.0]
      [bloco]
        [expr op='*']
          [mem_load VAR]
          [num valor=3.0]
```
