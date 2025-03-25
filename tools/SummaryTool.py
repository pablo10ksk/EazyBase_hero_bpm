from Chatbot import chatbot
from tools.ExampleQuestion import ExampleQuestion
from tools.SimpleXyzTool import SimpleXyzTool
from tools.tools import all_tools


class SummaryTool(SimpleXyzTool):
    def __init__(self):
        super().__init__(
            name="summary",
            description="This is the summary tool. Use this when the user asks for a summary of the capabilities or tools of the chatbot. For instance: _¿Qué puedo hacer en este chat?_, _¿Qué herramientas están disponibles?_, etc. Also use this when the user asks for help, or says hi.",
            human_name="Resumen de capacidades",
            human_description="Muestra un resumen de las capacidades del chatbot.",
            example_questions=[
                ExampleQuestion(
                    "¿Qué puedo hacer en este chat?",
                    "¿Qué puedo hacer?",
                    icon="❓",
                )
            ],
        )

    def run(self, prompt: str) -> dict:
        return {"tools": all_tools}

    def text(self, data: dict) -> str:
        name = chatbot.fancy_name
        description = chatbot.description.strip()
        tools_description = self._get_tools_description()

        return f"""Te damos la bienvenida a **{name}**: _{description}_ Aquí, puedes:\n\n{tools_description}"""

    def _get_tools_description(self) -> str:
        res = ""
        for idx, tool in enumerate(all_tools):
            name = tool.human_name
            description = tool.human_description
            res += f"{idx+1}. **{name}**: {description}\n"
        return res
