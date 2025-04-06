import azure.functions as func
import logging
from azurefunctions.extensions.http.fastapi import Request, JSONResponse

app = func.FunctionApp()


@app.route(route="sample", auth_level=func.AuthLevel.FUNCTION)
async def http_trigger(req: Request) -> JSONResponse:
    logging.info("Python HTTP trigger function processed a request.")

    # name = req.params.get("name")
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
