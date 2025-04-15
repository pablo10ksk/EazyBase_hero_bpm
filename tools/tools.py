from tools.MakeTaskDecisionTool import MakeTaskDecisionTool
from tools.PendingTasksTool import NEWPendingTasksTool
from tools.PendingTaskTool import PendingTaskTool
from tools.PhasedPendingTasksTool import PhasedPendingTasksTool
from tools.QueryPendingTasks import GraphPendingTasksTool
from tools.TesisAvailableTypes import TesisAvailableTypesTool
from tools.TesisTypeDescriptions import TesisTypeDescriptionsTool
from tools.TesisTypeExecution import TesisTypeExecutionTool
from tools.ProviderRegistrationTool import ProviderRegistrationTool
from tools.TesisExecuteTool import TesisExecutionTool
from tools.InformationTool import InformationTool
from tools.ResponseTool import ResponseTool
from tools.XyzTool import XyzTool

"""
A list of all the tools available in the chatbot.
"""
public_tools: list[XyzTool] = [
    NEWPendingTasksTool(),
    GraphPendingTasksTool(),
    PendingTaskTool(),
    MakeTaskDecisionTool(),
    PhasedPendingTasksTool(),
    # TESIS:
    # TesisAvailableTypesTool(),
    # TesisTypeDescriptionsTool(),
    # TesisTypeExecutionTool(),
    TesisExecutionTool(),
    InformationTool(),
    # Proveedores
    ProviderRegistrationTool()
]

private_tools : list[XyzTool] = [
   ResponseTool(),
]

# We add the Summary tool at the end
# to avoid circular dependencies
from tools.SummaryTool import SummaryTool

public_tools.append(SummaryTool())

all_tools = public_tools + private_tools
