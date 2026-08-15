import asyncio

from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

from framework.agentFactory import AgentFactory

MODEL_NAME = "openai/gpt-oss-20b"
BASE_URL = "https://integrate.api.nvidia.com/v1"
API_KEY = "<API_KEY>"



MODEL_INFO = {
    "vision": True,
    "function_calling": True,
    "json_output": True,
    "structured_output": True,
    "family": "openai",
}


async def main():
    model_client = OpenAIChatCompletionClient(
        model=MODEL_NAME, base_url=BASE_URL, api_key=API_KEY, model_info=MODEL_INFO
    )

    factory = AgentFactory(model_client)

    database_agent = factory.create_database_agent(system_message="""
            You are a Database specialist responsible for retrieving user registration data.

            Your task:
            1. Connect to the MySQL database 'rahulshettyacademy'
            2. Query the 'RegistrationDetails' table to get a random record
            3. Query the 'Usernames' table to get additional user data
            4. Combine the data from both tables to create complete registration information
            5. Ensure the email is unique by adding a timestamp or random number if needed
            6. Prepare all the registration data in a structured format so that another agent can understand
            When ready, write: "DATABASE_DATA_READY - APIAgent should proceed next"
            """)

    api_agent = factory.create_api_agent(system_message="""
          You are an API testing specialist with access to both REST API tools and filesystem.

            Your task:
            1. FIRST: Extract the EXACT registration data from DatabaseAgent's REGISTRATION_DATA message
            2. Read the Postman collection to understand the API contract
            3. Before making a registration API call- construct its  body field with the  DatabaseAgent's  data inline with below format rules:
            Email should be unique. add timestamp/random data,
            password should be a format of SecurePass123
            Mobile number format - 1234567890

            once json body field is constructed as per above, then make registration API call with constructed body field as mandatory field
            4. If registration succeeds OR fails with "user already exists", proceed with login
            5. Make login API call with userEmail and userPassword from database data
            6. Report the actual API response status and success/failure

            CRITICAL: You MUST use the exact data from DatabaseAgent's REGISTRATION_DATA, not the sample data from Postman collection.
                and also complete login api call to validate the data you registered using registration api.

            Base URL: https://rahulshettyacademy.com
            Content-Type: application/json

            When login attempt is  complete with successful registration api call , write: "API_TESTING_COMPLETE - ExcelAgent should proceed next"
            Include the final login status (success/failure) in your response.
            """)

    excel_agent = factory.create_excel_agent(system_message="""
            You are an Excel data management specialist. ONLY proceed when APIAgent has completed testing.

            Your task:
            1. Wait for APIAgent to complete with "API_TESTING_COMPLETE" message that includes login call success
            2. Extract the registration data from DatabaseAgent's REGISTRATION_DATA message
            3. Check APIAgent's response for actual login success/failure status
            4. Only save data if login was actually successful
            5. Open /Users/dou3836/Documents/LLM-MCP (AI Agent)/newdata.xlsx
            6. Add the registration data with current timestamp
            7. Save and verify the data

            CRITICAL: Only save data if APIAgent reports successful login, not just attempted login.

            When complete, write: "REGISTRATION COMPLETE" and stop.
            """)

    team = RoundRobinGroupChat(participants=[database_agent, api_agent, excel_agent],
                                termination_condition=TextMentionTermination("REGISTRATION COMPLETE"))

    task_result = await Console(team.run_stream(task="Execute Sequential User Registration Process:\n\n"
                                                       
                                                       "STEP 1 - DatabaseAgent (FIRST):\n"
                                                       "Get random registration data from database tables and format it clearly.\n\n"

                                                       "STEP 2 - APIAgent:\n"
                                                       "Read Postman collection files, then make registration followed by login APIs using the database data.\n\n"

                                                       "STEP 3 - ExcelAgent:\n"
                                                       "Save successful registration login details to Excel file.\n\n"

                                                       "Each agent should complete their work fully before the next agent begins. "
                                                       "Pass data clearly between agents using the specified formats." ))

asyncio.run(main())
