from Chatbot import chatbot
from tools.ExampleQuestion import ExampleQuestion
from tools.SimpleXyzTool import SimpleXyzTool
from tools.tools import all_tools


class SummaryTool(SimpleXyzTool):
    def __init__(self):
        super().__init__(
            name="summary",
            description="This is the summary tool. Use this when the user asks for a summary of the capabilities or tools of the chatbot. For instance: _What can I do here?_, _Which tools are available?_, etc. Also use this when the user asks for help, or says hi.",
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
        description = chatbot.description
        res = f"Welcome to **{name}**: {description} Here, you can:\n\n"
        res = f"Te damos la bienvenida a **{name}**: {description} Aquí, puedes:\n\n"
        for idx, tool in enumerate(data["tools"]):
            res += f"{idx+1}. **{tool.human_name}**: {tool.human_description}\n"
        return res
