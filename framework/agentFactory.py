from autogen_agentchat.agents import AssistantAgent

from framework.mcp_config import McpConfig


class AgentFactory:
    def __init__(self, model_client):
        self.model_client = model_client
        self.mcp_config = McpConfig()

    def create_database_agent(self,system_message):
        database_agent = AssistantAgent(name="DatabaseAgent",
                                     model_client=self.model_client,
                                     workbench= self.mcp_config.get_mysql_workbench(),
                                     system_message= system_message)
        return database_agent

    def create_api_agent(self,system_message):
        rest_api_work_bench = self.mcp_config.get_rest_api_workbench()
        file_system_workbench = self.mcp_config.get_file_system_workbench()

        api_agent = AssistantAgent(name="APIAgent",
                                   model_client=self.model_client,
                                   workbench=[rest_api_work_bench, file_system_workbench],
                                   system_message=system_message)
        return api_agent

    def create_excel_agent(self, system_message):
        excel_workbench = self.mcp_config.get_excel_workbench()
        return AssistantAgent(name="ExcelAgent",
                                     model_client=self.model_client,
                                     workbench=excel_workbench,
                                     system_message=system_message)
