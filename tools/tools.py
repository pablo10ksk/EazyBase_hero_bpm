from tools.MakeTaskDecisionTool import MakeTaskDecisionTool
from tools.OldPendingTasksTool import OldPendingTasksTool
from tools.PendingTasksTool import NEWPendingTasksTool
from tools.PendingTaskTool import PendingTaskTool
from tools.QueryPendingTasks import GraphPendingTasksTool
from tools.XyzTool import XyzTool

"""
A list of all the tools available in the chatbot.
"""
all_tools: list[XyzTool] = [
    # OldPendingTasksTool(),
    NEWPendingTasksTool(),
    GraphPendingTasksTool(),
    PendingTaskTool(),
    MakeTaskDecisionTool(),
]

# We add the Summary tool at the end
# to avoid circular dependencies
from tools.SummaryTool import SummaryTool

all_tools.append(SummaryTool())
