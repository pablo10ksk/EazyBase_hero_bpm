def get_name(type_cd: str) -> str:
    return {
        "115": "Vacaciones",
        "120": "Anticipo de nómina",
        "214": "Nota de gastos y kilómetros",
    }[type_cd]
