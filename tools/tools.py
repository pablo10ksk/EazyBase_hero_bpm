from tools.NEWMakeTaskDecisionTool import NEWMakeTaskDecisionTool
from tools.NEWPendingTask import NEWPendingTask
from tools.NEWPendingTasks import NEWPendingTasks
from tools.NEWQueryPendingTasks import NEWQueryPendingTasks
from tools.XyzTool import XyzTool

"""
A list of all the tools available in the chatbot.
"""
# all_tools: list[XyzTool] = [
#     GetAllPendingTasksTool(),
#     GetAllPendingTasksPhasedTool(),
#     MakeTaskDecisionTool(),
#     GetDecisionsTool(),
#     FilterPendingTasksTool(),
#     PendingTasksPandasAITool(),
# ]
all_tools: list[XyzTool] = [
    NEWPendingTasks(),
    NEWPendingTask(),
    NEWMakeTaskDecisionTool(),
    NEWQueryPendingTasks(),
]


# We add the summary tool at the end to avoid
# circular dependencies
from tools.SummaryTool import SummaryTool

all_tools.append(SummaryTool())
