import string

# Clases de caracteres
ALPHA = set(string.ascii_letters)
DIGIT = set(string.digits)
ALNUM = ALPHA | DIGIT
LOCAL_OK = ALNUM | set(['.', '_', '-', '+'])
DOMAIN_OK = ALNUM | set(['-', '.'])

# Estados
(
    q0,
    qL_ALNUM,
    qL_DOT_WAIT_ALNUM,
    qL_USCORE,
    qL_PLUS,
    qL_HYPHEN,
    qL_ERROR,
    qAT,
    qD_LABEL_START,
    qD_LABEL_ALNUM,
    qD_LABEL_HYPHEN,
    qD_DOT_EXPECT_LABEL,
    # TLD length tracker (implemented as (qT_base, length))
) = range(12)

# Representaremos TLD como (estado_base, tld_len>0) a partir de una bandera
# para no crear 24 constantes distintas en código,
# pero a efectos del DIAGRAMA cuentas qT_1 ... qT_24 como estados separados.

def is_valid_email(s: str) -> bool:
    if not s or '@' not in s:
        return False

    state = q0
    tld_len = 0        # longitud de TLD (solo letras)
    seen_at = False
    seen_dot_in_domain = False
    i = 0

    while i < len(s):
        c = s[i]

        # Clasificación básica
        if state == q0:
            if c in ALNUM:
                state = qL_ALNUM
            else:
                return False

        elif state == qL_ALNUM:
            if c in ALNUM:
                pass  # sigue en local
            elif c == '.':
                # no permitir '.' doble ni final: lo controlamos por estado de espera
                state = qL_DOT_WAIT_ALNUM
            elif c in {'_', '+', '-'}:
                # permitidos en local, pero no pueden cerrar el local ni duplicarse con '.'
                # (se mantiene en ALNUM-subgrupo; el estado sirve para el diagrama)
                # Para el DFA minimal, bastaría qL_ALNUM, pero dejamos estados diferenciados
                state = { '_': qL_USCORE, '+': qL_PLUS, '-': qL_HYPHEN }[c]
            elif c == '@':
                # local no puede terminar con '.' ni '-' ni vacío
                # Verificamos último char válido:
                if i == 0:
                    return False
                if s[i-1] in {'.', '-'}:
                    return False
                seen_at = True
                state = qAT
            else:
                return False

        elif state in (qL_USCORE, qL_PLUS, qL_HYPHEN):
            # Tras estos símbolos, debe venir ALNUM o '.' (pero controlamos '..' aparte)
            if c in ALNUM:
                state = qL_ALNUM
            elif c == '.':
                state = qL_DOT_WAIT_ALNUM
            elif c == '@':
                # no puede cerrar en '_' '+' '-' antes de '@'
                return False
            else:
                return False

        elif state == qL_DOT_WAIT_ALNUM:
            # obliga a alfanumérico luego de '.'
            if c in ALNUM:
                state = qL_ALNUM
            else:
                return False

        elif state == qAT:
            # Comienza DOMINIO: debe iniciar con letra/dígito
            if c in ALNUM:
                state = qD_LABEL_ALNUM
                seen_dot_in_domain = False
                tld_len = 0  # aún no sabemos si es TLD; lo sabremos después del último '.'
            else:
                return False

        elif state == qD_LABEL_ALNUM:
            if c in ALNUM:
                # sigue en etiqueta
                pass
            elif c == '-':
                # no puede terminar en '-', pero aquí está en medio
                state = qD_LABEL_HYPHEN
            elif c == '.':
                # fin de etiqueta -> ¿era TLD? Aún no; hay otra etiqueta
                state = qD_DOT_EXPECT_LABEL
            else:
                return False

        elif state == qD_LABEL_HYPHEN:
            if c in ALNUM:
                # el '-' quedó en medio, válido
                state = qD_LABEL_ALNUM
            elif c == '.':
                # etiqueta no puede terminar con '-'
                return False
            else:
                return False

        elif state == qD_DOT_EXPECT_LABEL:
            # Tras un '.', debe iniciar nueva etiqueta con letra/dígito
            if c in ALNUM:
                state = qD_LABEL_ALNUM
                seen_dot_in_domain = True
            else:
                return False

        else:
            return False

        i += 1

    # Fin de cadena: decidir si el último tramo es TLD válido
    # Recorremos desde el último '.' para medir TLD:
    if not seen_at:
        return False

    try:
        domain = s.split('@', 1)[1]
    except:
        return False

    if '.' not in domain:
        # debe tener al menos un punto en el dominio
        return False

    # Validar última etiqueta (TLD): solo letras y 2..24
    last_label = domain.rsplit('.', 1)[1]
    if len(last_label) < 2 or len(last_label) > 24:
        return False
    if not all(ch in ALPHA for ch in last_label):
        return False

    # Validar que ninguna etiqueta empiece/termine con '-' o esté vacía
    labels = domain.split('.')
    for lab in labels:
        if not lab:
            return False
        if lab[0] == '-' or lab[-1] == '-':
            return False

    # Validaciones de local part:
    local = s.split('@',1)[0]
    if local[0] == '.' or local[-1] in {'.','-'}:
        return False
    if '..' in local:
        return False

    return True


# --- Pequeña demo ---
if __name__ == "__main__":
    correo = input("Ingresa un correo electrónico: ")
    print("¿Es válido?:", is_valid_email(correo))
