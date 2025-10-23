# validador_dfa.py
# DFA de 35 estados reales para validar correos de forma razonable (no RFC completo)
# Estructura de estados:
# q0                 -> inicio
# q1..q15 (local)    -> parte usuario; impares = "después de alnum", pares = "después de símbolo (._+-) requiere alnum"
# q16                -> después de '@'
# q17..q26 (dominio) -> dominio; impares = "después de alnum", pares = "después de guion '-' requiere alnum"
# q27                -> después de '.' que separa dominio y TLD
# q28..q33 (TLD)     -> longitud 1..6 (solo letras)
# q34                -> aceptación (solo se alcanza al final si TLD>=2)
# qError             -> pozo

import string

ALPHA = set(string.ascii_letters)
DIGIT = set(string.digits)
ALNUM = ALPHA | DIGIT
LOCAL_SYM = set("._+-")  # símbolos permitidos en local-part
DOMAIN_SYM = set("-")    # símbolo permitido en el dominio

ALL_STATES = (
    ["q0"]
    + [f"q{i}" for i in range(1, 35)]
    + ["qError"]
)

ACCEPT_STATE = "q34"

def _is_local_allowed(ch):   return (ch in ALNUM) or (ch in LOCAL_SYM) or (ch == '@')
def _is_domain_allowed(ch):  return (ch in ALNUM) or (ch in DOMAIN_SYM) or (ch == '.')
def _is_tld_letter(ch):      return ch in ALPHA

def _next_local_state(state_idx_is_odd, i, ch):
    """
    Manejo de q1..q15 (local). Impares = después de alnum; Pares = después de símbolo (._+-)
    - Desde impar: alnum -> permanece en impar (o avanza hasta q15), símbolo -> va a par siguiente (i+1), '@' -> q16
    - Desde par:   requiere alnum -> va al impar siguiente (i+1). '@' y otro símbolo -> error
    """
    if state_idx_is_odd:
        # en impar (después de alnum)
        if ch in ALNUM:
            return min(i, 15)  # se queda en la "banda" impar, cap en q15
        if ch in LOCAL_SYM:
            return min(i + 1, 15)  # va a par (i+1)
        if ch == '@':
            return 16
        return "Error"
    else:
        # en par (después de símbolo) -> debe venir alnum
        if ch in ALNUM:
            return min(i + 1, 15)  # vuelve a impar
        # no se permite símbolo seguido ni '@' inmediatamente
        return "Error"

def _next_domain_state(state_idx_is_odd, i, ch):
    """
    Manejo de q17..q26 (dominio). Impares = después de alnum; Pares = después de '-'
    - Desde impar: alnum -> queda en impar (cap en q25), '-' -> par (i+1), '.' -> q27
    - Desde par:   requiere alnum -> impar (i+1); '.' o '-' -> error
    """
    if state_idx_is_odd:
        if ch in ALNUM:
            # mantenerse en impar, cap al último impar del bloque (q25)
            return min(i, 25)
        if ch == '-':
            return min(i + 1, 26)  # a par
        if ch == '.':
            return 27
        return "Error"
    else:
        # en par (tras '-') requiere alnum
        if ch in ALNUM:
            return min(i + 1, 25)  # a impar
        return "Error"

def simulate(email: str):
    """
    Simula el DFA carácter por carácter y devuelve:
      path: lista de estados visitados (strings)
      accepted: bool
    Reglas principales:
      - Local-part: empieza con ALNUM, permite . _ + - pero no consecutivos (se modela con par que exige alnum).
      - Debe haber exactamente un '@'.
      - Dominio: letras/dígitos y guion, sin guion final ni doble guion (se modela con par que exige alnum).
      - Debe haber un '.' que separa dominio y TLD.
      - TLD: solo letras, longitud 2..6.
    """
    if not email:
        return (["q0", "qError"], False)

    state = "q0"
    path = [state]
    at_seen = False
    tld_len = 0

    for ch in email:
        # Filtrar caracteres de alfabeto global
        if ch not in (ALNUM | LOCAL_SYM | {'@', '.'}):
            state = "qError"
            path.append(state)
            break

        if state == "q0":
            if ch in ALNUM:
                state = "q1"
            else:
                state = "qError"

        # q1..q15: local-part
        elif state.startswith("q") and 1 <= int(state[1:]) <= 15:
            i = int(state[1:])
            odd = (i % 2 == 1)
            nxt = _next_local_state(odd, i, ch)
            if nxt == "Error":
                state = "qError"
            else:
                if nxt == 16:
                    at_seen = True
                    state = "q16"
                else:
                    state = f"q{nxt}"

        # q16: justo después de '@' (debe venir ALNUM)
        elif state == "q16":
            if ch in ALNUM:
                state = "q17"
            else:
                state = "qError"

        # q17..q26: dominio
        elif state.startswith("q") and 17 <= int(state[1:]) <= 26:
            i = int(state[1:])
            odd = (i % 2 == 1)
            if not _is_domain_allowed(ch):
                state = "qError"
            else:
                nxt = _next_domain_state(odd, i, ch)
                if nxt == "Error":
                    state = "qError"
                elif nxt == 27:
                    state = "q27"
                else:
                    state = f"q{nxt}"

        # q27: después del '.' que inicia TLD (debe venir letra)
        elif state == "q27":
            if _is_tld_letter(ch):
                state = "q28"
                tld_len = 1
            else:
                state = "qError"

        # q28..q33: TLD de 1..6 letras
        elif state.startswith("q") and 28 <= int(state[1:]) <= 33:
            if _is_tld_letter(ch):
                # avanzar en contador de TLD hasta q33 (cap 6 letras)
                cur = int(state[1:])
                tld_len = min(tld_len + 1, 6)
                state = f"q{min(cur + 1, 33)}"
            else:
                state = "qError"

        else:
            state = "qError"

        path.append(state)
        if state == "qError":
            break

    # Fin de la entrada: decidir aceptación
    accepted = False
    if at_seen and state.startswith("q"):
        idx = int(state[1:]) if state[1:].isdigit() else -1
        # Acepta solo si está en TLD con longitud >= 2 (q29..q33)
        if 29 <= idx <= 33:
            state = ACCEPT_STATE
            path.append(state)
            accepted = True

    return (path, accepted)
