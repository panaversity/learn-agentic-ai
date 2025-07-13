from core.agent_service import AgentService
from mcp_client import MCPClient

class Chat:
    def __init__(self, agent_serve: AgentService, clients: dict[str, MCPClient]):
        self.agent_serve: AgentService = agent_serve
        self.clients: dict[str, MCPClient] = clients


    async def run(
        self,
        query: str,
    ) -> str:

        response = await self.agent_serve.chat(
            query=query,
            mcp_clients=self.clients,
        )
        
        return response.final_output
