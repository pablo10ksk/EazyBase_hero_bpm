from tools.MakeTaskDecisionTool import MakeTaskDecisionTool
from tools.PendingTasksTool import PendingTasksTool
from tools.PendingTaskTool import PendingTaskTool
from tools.QueryPendingTasks import QueryPendingTasksTool
from tools.XyzTool import XyzTool

"""
A list of all the tools available in the chatbot.
"""
all_tools: list[XyzTool] = [
    PendingTasksTool(),
    QueryPendingTasksTool(),
    PendingTaskTool(),
    MakeTaskDecisionTool(),
]

# We add the Summary tool at the end
# to avoid circular dependencies
from tools.SummaryTool import SummaryTool

all_tools.append(SummaryTool())
