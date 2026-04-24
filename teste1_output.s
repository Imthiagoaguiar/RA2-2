.syntax unified
.cpu cortex-a9
.fpu vfpv3-d16
.text
.global _start

_start:
    @ Habilita VFP
    MRC p15, 0, r0, c1, c0, 2
    ORR r0, r0, #0xF00000
    MCR p15, 0, r0, c1, c0, 2
    MOV r0, #0x40000000
    FMXR FPEXC, r0

    @ Inicializa ponteiro de pilha RPN
    LDR r4, =rpn_stack
    MOV r5, #0              @ r5 = profundidade da pilha RPN

    @ expr op='+'
    LDR r0, =cst_0
    VLDR d0, [r0]         @ load 3.0
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    LDR r0, =cst_1
    VLDR d0, [r0]         @ load 2.0
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    @ pop -> d1
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d1, [r4]
    @ pop -> d0
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d0, [r4]
    VADD.F64 d0, d0, d1
    @ salva resultado linha 1
    LDR r0, =res_history
    ADD r0, r0, #0
    VSTR d0, [r0]

    @ expr op='-'
    LDR r0, =cst_2
    VLDR d0, [r0]         @ load 10.5
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    LDR r0, =cst_3
    VLDR d0, [r0]         @ load 4.5
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    @ pop -> d1
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d1, [r4]
    @ pop -> d0
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d0, [r4]
    VSUB.F64 d0, d0, d1
    @ salva resultado linha 2
    LDR r0, =res_history
    ADD r0, r0, #8
    VSTR d0, [r0]

    @ expr op='*'
    LDR r0, =cst_4
    VLDR d0, [r0]         @ load 2.5
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    LDR r0, =cst_5
    VLDR d0, [r0]         @ load 4.0
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    @ pop -> d1
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d1, [r4]
    @ pop -> d0
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d0, [r4]
    VMUL.F64 d0, d0, d1
    @ salva resultado linha 3
    LDR r0, =res_history
    ADD r0, r0, #16
    VSTR d0, [r0]

    @ expr op='|'
    LDR r0, =cst_6
    VLDR d0, [r0]         @ load 9.0
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    LDR r0, =cst_7
    VLDR d0, [r0]         @ load 2.0
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    @ pop -> d1
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d1, [r4]
    @ pop -> d0
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d0, [r4]
    VDIV.F64 d0, d0, d1
    @ salva resultado linha 4
    LDR r0, =res_history
    ADD r0, r0, #24
    VSTR d0, [r0]

    @ expr op='/'
    LDR r0, =cst_8
    VLDR d0, [r0]         @ load 9
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    LDR r0, =cst_9
    VLDR d0, [r0]         @ load 2
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    @ pop -> d1
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d1, [r4]
    @ pop -> d0
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d0, [r4]
    @ divisão inteira (subtração repetida)
    VCVT.S32.F64 s0, d0
    VCVT.S32.F64 s1, d1
    VMOV r0, s0
    VMOV r1, s1
    EOR r3, r0, r1
    CMP r0, #0
    RSBLT r0, r0, #0
    CMP r1, #0
    RSBLT r1, r1, #0
    MOV r2, #0
div_loop_1:
    CMP r0, r1
    BLT div_end_2
    SUB r0, r0, r1
    ADD r2, r2, #1
    B div_loop_1
div_end_2:
    CMP r3, #0
    RSBLT r2, r2, #0
    VMOV s0, r2
    VCVT.F64.S32 d0, s0
    @ salva resultado linha 5
    LDR r0, =res_history
    ADD r0, r0, #32
    VSTR d0, [r0]

    @ expr op='%'
    LDR r0, =cst_10
    VLDR d0, [r0]         @ load 10
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    LDR r0, =cst_11
    VLDR d0, [r0]         @ load 3
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    @ pop -> d1
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d1, [r4]
    @ pop -> d0
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d0, [r4]
    @ resto inteiro (subtração repetida)
    VCVT.S32.F64 s0, d0
    VCVT.S32.F64 s1, d1
    VMOV r0, s0
    VMOV r1, s1
    CMP r0, #0
    RSBLT r0, r0, #0
    CMP r1, #0
    RSBLT r1, r1, #0
mod_loop_3:
    CMP r0, r1
    BLT mod_end_4
    SUB r0, r0, r1
    B mod_loop_3
mod_end_4:
    VMOV s0, r0
    VCVT.F64.S32 d0, s0
    @ salva resultado linha 6
    LDR r0, =res_history
    ADD r0, r0, #40
    VSTR d0, [r0]

    @ expr op='^'
    LDR r0, =cst_12
    VLDR d0, [r0]         @ load 2.0
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    LDR r0, =cst_13
    VLDR d0, [r0]         @ load 8
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    @ pop -> d1
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d1, [r4]
    @ pop -> d0
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d0, [r4]
    @ potenciação A^B
    VMOV.F64 d3, d0           @ base
    VCVT.S32.F64 s1, d1
    VMOV r1, s1               @ expoente
    LDR r0, =cst_one_7
    VLDR d2, [r0]             @ acumulador = 1.0
pow_loop_6:
    CMP r1, #0
    BLE pow_end_7
    VMUL.F64 d2, d2, d3
    SUB r1, r1, #1
    B pow_loop_6
pow_end_7:
    VMOV.F64 d0, d2
    @ salva resultado linha 7
    LDR r0, =res_history
    ADD r0, r0, #48
    VSTR d0, [r0]

    @ store 20.0 -> SOMA
    LDR r0, =cst_14
    VLDR d0, [r0]
    LDR r0, =var_soma
    VSTR d0, [r0]
    @ salva resultado linha 8
    LDR r0, =res_history
    ADD r0, r0, #56
    VSTR d0, [r0]

    @ load SOMA
    LDR r0, =var_soma
    VLDR d0, [r0]
    @ salva resultado linha 9
    LDR r0, =res_history
    ADD r0, r0, #64
    VSTR d0, [r0]

    @ expr op='+'
    LDR r0, =cst_15
    VLDR d0, [r0]         @ load 3.0
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    @ expr op='*'
    LDR r0, =cst_16
    VLDR d0, [r0]         @ load 2.0
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    LDR r0, =cst_17
    VLDR d0, [r0]         @ load 4.0
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    @ pop -> d1
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d1, [r4]
    @ pop -> d0
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d0, [r4]
    VMUL.F64 d0, d0, d1
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    @ pop -> d1
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d1, [r4]
    @ pop -> d0
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d0, [r4]
    VADD.F64 d0, d0, d1
    @ salva resultado linha 10
    LDR r0, =res_history
    ADD r0, r0, #72
    VSTR d0, [r0]

    @ expr op='>'
    @ expr op='+'
    LDR r0, =cst_18
    VLDR d0, [r0]         @ load 5.0
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    LDR r0, =cst_19
    VLDR d0, [r0]         @ load 3.0
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    @ pop -> d1
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d1, [r4]
    @ pop -> d0
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d0, [r4]
    VADD.F64 d0, d0, d1
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    @ expr op='*'
    LDR r0, =cst_20
    VLDR d0, [r0]         @ load 2.0
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    LDR r0, =cst_21
    VLDR d0, [r0]         @ load 3.0
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    @ pop -> d1
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d1, [r4]
    @ pop -> d0
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d0, [r4]
    VMUL.F64 d0, d0, d1
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    @ pop -> d1
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d1, [r4]
    @ pop -> d0
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d0, [r4]
    @ comparação >
    VCMP.F64 d0, d1
    VMRS APSR_nzcv, FPSCR
    BGT cmp_true_8
    LDR r0, =cst_cmp0_9
    VLDR d0, [r0]
    B cmp_end_9
cmp_true_8:
    LDR r0, =cst_cmp1_9
    VLDR d0, [r0]
cmp_end_9:
    @ salva resultado linha 11
    LDR r0, =res_history
    ADD r0, r0, #80
    VSTR d0, [r0]

    @ --- laço LOOP N=3 ---
    MOV r7, #3            @ contador de iterações
loop_start_10:
    CMP r7, #0
    BLE loop_end_11
    @ expr op='*'
    LDR r0, =cst_22
    VLDR d0, [r0]         @ load 2.0
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    LDR r0, =cst_23
    VLDR d0, [r0]         @ load 2.0
    @ push d0 na pilha RPN
    LSL r6, r5, #3          @ offset = profundidade * 8
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VSTR d0, [r4]
    ADD r5, r5, #1
    @ pop -> d1
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d1, [r4]
    @ pop -> d0
    SUB r5, r5, #1
    LSL r6, r5, #3
    LDR r4, =rpn_stack
    ADD r4, r4, r6
    VLDR d0, [r4]
    VMUL.F64 d0, d0, d1
    @ salva resultado linha 12
    LDR r0, =res_history
    ADD r0, r0, #88
    VSTR d0, [r0]

    SUB r7, r7, #1
    B loop_start_10
loop_end_11:

end_loop:
    B end_loop

.data
.align 3
res_history: .space 96  @ histórico de resultados
.align 3
rpn_stack: .space 512     @ pilha RPN (64 doubles)
.align 3
var_soma: .double 0.0  @ variável SOMA
.align 3
.align 3
cst_0: .double 3.0
.align 3
cst_1: .double 2.0
.align 3
cst_2: .double 10.5
.align 3
cst_3: .double 4.5
.align 3
cst_4: .double 2.5
.align 3
cst_5: .double 4.0
.align 3
cst_6: .double 9.0
.align 3
cst_7: .double 2.0
.align 3
cst_8: .double 9.0
.align 3
cst_9: .double 2.0
.align 3
cst_10: .double 10.0
.align 3
cst_11: .double 3.0
.align 3
cst_12: .double 2.0
.align 3
cst_13: .double 8.0
.align 3
cst_one_7: .double 1.0
.align 3
cst_14: .double 20.0
.align 3
cst_15: .double 3.0
.align 3
cst_16: .double 2.0
.align 3
cst_17: .double 4.0
.align 3
cst_18: .double 5.0
.align 3
cst_19: .double 3.0
.align 3
cst_20: .double 2.0
.align 3
cst_21: .double 3.0
.align 3
cst_cmp1_9: .double 1.0
.align 3
cst_cmp0_9: .double 0.0
.align 3
cst_22: .double 2.0
.align 3
cst_23: .double 2.0