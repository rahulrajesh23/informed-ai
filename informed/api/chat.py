from typing import cast

from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address


from informed.helper.utils import UserDep
from informed.api.schema import ChatRequest, AddUserMessageRequest, ChatResponse

from informed.informed import InformedManager
from uuid import UUID

router = APIRouter()


# Create a Limiter instance
limiter = Limiter(key_func=get_remote_address)


@router.post("", response_model=ChatResponse)
async def create_chat(
    chat_request: ChatRequest, request: Request, user: UserDep
) -> ChatResponse:
    app_manager = cast(InformedManager, request.app.state.app_manager)
    try:
        chat_thread = await app_manager.start_new_chat_thread(
            chat_request, user.user_id
        )
        chat_thread = await app_manager.get_chat(chat_thread.chat_thread_id)
        chat_response = ChatResponse.from_chat_thread(chat_thread)
        return chat_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e!s}") from e


@router.post("/{chat_thread_id}", response_model=ChatResponse)
async def add_user_message(
    add_user_message_request: AddUserMessageRequest,
    user: UserDep,
    request: Request,
) -> ChatResponse:
    app_manager = cast(InformedManager, request.app.state.app_manager)
    try:
        await app_manager.add_user_message(add_user_message_request, user.user_id)
        chat_thread_id = add_user_message_request.chat_thread_id
        chat_thread = await app_manager.get_chat(chat_thread_id)
        if chat_thread is None:
            raise HTTPException(
                status_code=404, detail=f"chat thread {chat_thread_id} not found"
            )
        chat_response = ChatResponse.from_chat_thread(chat_thread)
        return chat_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"unexpected error: {e}") from e


@router.get("/{chat_thread_id}", response_model=ChatResponse)
async def get_chat(
    chat_thread_id: UUID,
    _: UserDep,
    request: Request,
) -> ChatResponse:
    app_manager = cast(InformedManager, request.app.state.app_manager)
    try:
        chat_thread = await app_manager.get_chat(chat_thread_id)
        chat_response = ChatResponse.from_chat_thread(chat_thread)
        return chat_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"unexpected error: {e!s}") from e
