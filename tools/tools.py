from tools.MakeTaskDecisionTool import MakeTaskDecisionTool
from tools.PendingTasksTool import NEWPendingTasksTool
from tools.PendingTaskTool import PendingTaskTool
from tools.PhasedPendingTasksTool import PhasedPendingTasksTool
from tools.QueryPendingTasks import GraphPendingTasksTool
from tools.TesisAvailableTypes import TesisAvailableTypesTool
from tools.TesisTypeDescriptions import TesisTypeDescriptionsTool
from tools.TesisTypeExecution import TesisTypeExecutionTool
from tools.XyzTool import XyzTool

"""
A list of all the tools available in the chatbot.
"""
all_tools: list[XyzTool] = [
    NEWPendingTasksTool(),
    GraphPendingTasksTool(),
    PendingTaskTool(),
    MakeTaskDecisionTool(),
    PhasedPendingTasksTool(),
    # TESIS:
    TesisAvailableTypesTool(),
    TesisTypeDescriptionsTool(),
    TesisTypeExecutionTool(),
]

# We add the Summary tool at the end
# to avoid circular dependencies
from tools.SummaryTool import SummaryTool

all_tools.append(SummaryTool())
