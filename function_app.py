import os
import azure.functions as func
import logging
from azurefunctions.extensions.http.fastapi import Request, JSONResponse

from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from azure.identity import (
    DefaultAzureCredential,
    ManagedIdentityCredential,
    get_bearer_token_provider,
)
from semantic_kernel.contents import AuthorRole, ChatHistory, ChatMessageContent


app = func.FunctionApp()


def get_azure_credential() -> ManagedIdentityCredential | DefaultAzureCredential:
    # don't set this in local.settings.json
    # we'll use AzureCliCredential to authenticate locally
    client_id: str | None = os.getenv("AZURE_CLIENT_ID")

    if client_id:
        return ManagedIdentityCredential(client_id=client_id)

    return DefaultAzureCredential()


chat_history = ChatHistory(system_message="You are a helpful AI Agent")


@app.route(route="sample", auth_level=func.AuthLevel.FUNCTION)
async def sample(req: Request) -> JSONResponse:
    logging.info("Python HTTP trigger function processed a request.")

    name = req.query_params.get("name")
    if not name:
        try:
            req_body = await req.json()
        except ValueError:
            pass
        else:
            name = req_body.get("name")

    if name:
        return JSONResponse(
            f"Hello, {name}. This HTTP triggered function executed successfully."
        )
    else:
        return JSONResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200,
        )


@app.route(
    route="chat", methods=[func.HttpMethod.POST], auth_level=func.AuthLevel.FUNCTION
)
async def chat(req: Request) -> JSONResponse:

    try:
        payload = await req.json()
        prompt = payload["prompt"]
        if not prompt:
            return JSONResponse({"message": "prompt is required."})

        chat_history.add_message(
            message=ChatMessageContent(role=AuthorRole.USER, content=prompt)
        )
        gpt_4o_mini_service = AzureChatCompletion(
            service_id="gpt4omini",
            deployment_name="gpt-4o-mini",
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            ad_token_provider=get_bearer_token_provider(
                get_azure_credential(), "https://cognitiveservices.azure.com/.default"
            ),
            api_version=os.getenv("OPENAI_API_VERSION", ""),
        )
        completion = await gpt_4o_mini_service.get_chat_message_content(
            chat_history=chat_history,
            settings=AzureChatPromptExecutionSettings(),
        )
        if completion:
            return JSONResponse({"message": completion.content})

        return JSONResponse({"error": "Content can't be found"})
    except Exception as e:
        return JSONResponse(str(e), status_code=500)
