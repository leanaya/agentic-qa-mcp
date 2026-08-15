from autogen_ext.tools.mcp import StdioServerParams, McpWorkbench


class McpConfig:


    @staticmethod
    def get_mysql_workbench():
        mysql_server_params = StdioServerParams(
            command="/Users/name/PycharmProjects/autogenai/.venv/bin/uv",
            args=[
                "--directory",
                "/Users/name/PycharmProjects/autogenai/.venv/lib/python3.14/site-packages",
                "run",
                "mysql_mcp_server",
            ],
            env={
                "MYSQL_HOST": "localhost",
                "MYSQL_PORT": "3306",
                "MYSQL_USER": "root",
                "MYSQL_PASSWORD": "<MYSQL_PASSWORD>",
                "MYSQL_DATABASE": "rahulshettyacademy",
            },
            read_timeout_seconds=60,
        )

        return McpWorkbench(mysql_server_params)

    @staticmethod
    def get_rest_api_workbench():
        rest_api_server_params = StdioServerParams(
            command="npx",
            args=[
                "-y",
                "dkmaker-mcp-rest-api",
            ],
            env={
                "REST_BASE_URL": "https://rahulshettyacademy.com",
                "HEADER_Accept": "application/json",
            },
            read_timeout_seconds=60,
        )

        return McpWorkbench(rest_api_server_params)

    @staticmethod
    def get_excel_workbench():
        excel_server_params = StdioServerParams(
            command="npx",
            args=[
                "--yes",
                "@negokaz/excel-mcp-server",
            ],
            env={
                "EXCEL_MCP_PAGING_CELLS_LIMIT": "4000",
            },
            read_timeout_seconds=60,
        )

        return McpWorkbench(excel_workbench)

    @staticmethod
    def get_file_system_workbench():
        file_system_server_params = StdioServerParams(
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                "/Users/name/Documents/LLM-MCP (AI Agent)"
            ],
            read_timeout_seconds=60,
        )

        return McpWorkbench(server_params=file_system_server_params)
