import asyncio
import json
from textwrap import dedent
from uuid import UUID

from loguru import logger as log
from pydantic import BaseModel

from informed.config import WeatherSourcesConfig
from informed.db_models.query import Query, QuerySource, QueryState
from informed.db_models.users import User
from informed.helper.util import (
    build_system_prompt,
    build_weather_query_context,
    extract_user_info,
)
from informed.llm.client import LLMClient
from informed.llm.llm import ChatState
from informed.llm.schema import build_function_schema
from informed.query.manager import QueryManager
from informed.services.weather_alert_service import WeatherAlertService
from informed.users.manager import UserManager


class QueryResponse(BaseModel):
    answer: str = ""


class QueryAgent:
    def __init__(
        self,
        query_id: UUID,
        query_manager: QueryManager,
        user_manager: UserManager,
        llm_client: LLMClient,
        weather_sources_config: WeatherSourcesConfig,
        weather_alert_service: WeatherAlertService,
        previous_messages: list[str],
        instructions: str | None = None,
    ):
        self.query_id = query_id
        self.query_manager = query_manager
        self.user_manager = user_manager
        self.llm_client = llm_client
        self.weather_sources_config = weather_sources_config
        self.weather_alert_service = weather_alert_service
        self.instructions = instructions
        self.previous_messages = previous_messages

    async def run(self) -> None:
        query = await self.query_manager.get_query(self.query_id)
        if query is None:
            raise ValueError(f"Query {self.query_id} not found")
        query.state = QueryState.PENDING
        await self.query_manager.persist_query(query)
        await self._run(query)

    async def _run(self, query: Query) -> None:
        user = await self.user_manager.get_user(query.user_id)
        if not user:
            raise ValueError("User not found")
        await self._process_query(query, user)

    async def _process_query(self, query: Query, user: User) -> None:
        try:
            system_prompt = build_system_prompt()
            user_info = extract_user_info(user)
            context = await build_weather_query_context(
                user,
                weather_sources_config=self.weather_sources_config,
                weather_alert_service=self.weather_alert_service,
            )
            user_prompt = dedent(
                f"""
                <weather_context>
                {context}
                </weather_context>
                <user>
                {user_info}
                </user>
                <previous_messages>
                    {"\n".join(self.previous_messages)}
                </previous_messages>
                <new_user_message>
                {query.query}
                </new_user_message>
                """
            )
            if self.instructions:
                user_prompt += f"\n<instructions>{self.instructions}</instructions>"
            chat_state = ChatState(system_prompt=system_prompt, user_prompt=user_prompt)
            output_schema = build_function_schema(
                QueryResponse,
                description="""
                Function to provide the response to the user's question.
                All assistant responses must be passed through this tool.

                Args:
                    answer (str): The assistant's response to the user's question
                """,
            )
            try:

                function = await self.llm_client.chat_completion(
                    chat_state, tools=[output_schema]
                )
                data = json.loads(function.arguments)
                weather_response = QueryResponse.model_validate(data)

                if isinstance(weather_response, QueryResponse):
                    log.info(f"GPT Response: {weather_response.model_dump_json()}")
                    query.state = QueryState.COMPLETED
                    query.answer = weather_response.answer
                    # TODO: Need to change after adding multiple sources
                    # Also remove this hardcoded source
                    query.sources = [QuerySource(source="https://api.weather.gov")]
                else:
                    log.error(
                        f"Unexpected response type for GPT response: {type(weather_response)}"
                    )
                    query.state = QueryState.FAILED
                    query.answer = "Sorry, I'm having some trouble answering your question. Please contact support"

            except Exception as e:
                log.error(e)
                query.state = QueryState.FAILED
                query.answer = "Sorry, I'm having some trouble answering your question. Please contact support"

            await self.query_manager.persist_query(query)

        except asyncio.CancelledError:
            log.info("Document processing was cancelled.")
            query.state = QueryState.CANCELLED
            await self.query_manager.persist_query(query)
            raise
        except Exception as e:
            query.state = QueryState.FAILED
            await self.query_manager.persist_query(query)
            log.error(f"Error processing documents: {e!s}")
            raise
