# constants.py
from typing import FrozenSet, Literal

# Префикс → тип сущности: "account" для счёта, "card" для карты
PREFIX_TO_TYPE: dict[str, Literal["account", "card"]] = {
    # Счёт
    "Счет": "account",
    # Visa
    "Visa": "card",
    "Visa Classic": "card",
    "Visa Gold": "card",
    "Visa Platinum": "card",
    "Visa Signature": "card",
    "Visa Infinite": "card",
    "Visa Electron": "card",
    "Visa Business": "card",
    "Visa Corporate": "card",
    # MasterCard
    "MasterCard": "card",
    "MasterCard Standard": "card",
    "MasterCard Gold": "card",
    "MasterCard Platinum": "card",
    "MasterCard World": "card",
    "MasterCard Black": "card",
    "MasterCard Business": "card",
    # American Express
    "AmericanExpress": "card",
    "American Express": "card",
    "AmEx": "card",
    # Maestro
    "Maestro": "card",
    "Maestro Standard": "card",
    "Maestro Premier": "card",
    # МИР
    "МИР": "card",
    "MIR": "card",
    "МИР Premium": "card",
    "МИР Classic": "card",
    "МИР Gold": "card",
    "МИР Platinum": "card",
    # Discover
    "Discover": "card",
    "Discover it": "card",
    # JCB
    "JCB": "card",
    "JCB Standard": "card",
    "JCB Gold": "card",
    # Diners Club
    "DinersClub": "card",
    "Diners Club": "card",
    # UnionPay
    "UnionPay": "card",
    "Union Pay": "card",
    # Cirrus
    "Cirrus": "card",
}

# Все разрешённые префиксы как неизменяемое множество
VALID_CARD_PREFIXES: FrozenSet[str] = frozenset(PREFIX_TO_TYPE.keys())
