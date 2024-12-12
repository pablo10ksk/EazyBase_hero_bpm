from tools.SimpleXyzTool import SimpleXyzTool


class VacationsTool(SimpleXyzTool):
    def __init__(self):
        super().__init__(
            name="vacations",
            description="Show the vacation periods of the current user.",
            human_name="Vacaciones",
            human_description="Muestra los periodos de vacaciones.",
        )

    def run(self, prompt: str) -> dict:
        return {}

    def text(self, data: dict) -> str:
        return "Tienes vacaciones el dia DD-MM-YYYY."
