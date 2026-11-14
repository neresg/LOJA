"""Funções auxiliares para ler e validar o que o usuário digita."""
from decimal import Decimal, InvalidOperation


def ler_texto(msg, padrao=None):
    """Lê um texto obrigatório. Se houver 'padrao', Enter em branco mantém o padrão."""
    while True:
        texto = input(msg).strip()
        if texto:
            return texto
        if padrao is not None:
            return padrao
        print("Campo obrigatório.")


def ler_inteiro(msg, minimo=None, padrao=None):
    """Lê um número inteiro. Se houver 'padrao', Enter em branco mantém o padrão."""
    while True:
        texto = input(msg).strip()
        if texto == "" and padrao is not None:
            return padrao
        try:
            valor = int(texto)
        except ValueError:
            print("Digite um número inteiro.")
            continue
        if minimo is not None and valor < minimo:
            print(f"O valor deve ser maior ou igual a {minimo}.")
            continue
        return valor


def ler_decimal(msg, padrao=None):
    """Lê um valor monetário maior que zero (aceita vírgula ou ponto)."""
    while True:
        texto = input(msg).strip().replace(",", ".")
        if texto == "" and padrao is not None:
            return padrao
        try:
            valor = Decimal(texto)
        except InvalidOperation:
            print("Digite um valor válido. Exemplo: 12.50")
            continue
        if valor <= 0:
            print("O valor deve ser maior que zero.")
            continue
        return valor


def ler_cpf(msg, padrao=None):
    """Lê um CPF (só confere os 11 dígitos) e devolve formatado: 000.000.000-00."""
    while True:
        texto = input(msg).strip()
        if texto == "" and padrao is not None:
            return padrao
        digitos = "".join(c for c in texto if c.isdigit())
        if len(digitos) != 11:
            print("O CPF deve ter 11 dígitos.")
            continue
        return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"


def pausar():
    input("\nPressione Enter para continuar...")
