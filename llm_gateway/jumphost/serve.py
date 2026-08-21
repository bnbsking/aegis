import logging
import traceback
from typing import Dict, List

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from llm_client.async_funcs import async_executor
from llm_client.llm_calls import init_model
from pydantic import BaseModel

from jumphost.exceptions import BaseCustomException
from jumphost.logs import setup_logging


setup_logging()
logger = logging.getLogger(__name__)
logger.info("Start serving ...")
app = FastAPI()


@app.exception_handler(BaseCustomException)
async def custom_exception_handler(request: Request, exc: BaseCustomException) -> str:
    logger.error(f"[Client error] {exc.message}")
    return JSONResponse(
        status_code=exc.code,
        content=f"[Client error] {exc.message}"
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> str:
    tb = traceback.format_exc()
    logger.error(f"[Internal server error] {tb}, {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=f"[Internal server error] {str(exc)}"
    )


class APIRequestRunArgs(BaseModel):
    prompt: str | List[Dict]
    response_format: Dict | None = None
    extra_args: Dict | None = None


class APIRequest(BaseModel):
    mod_name: str
    cls_name: str
    init_args: Dict | None = None
    run_args: APIRequestRunArgs | None = None


@app.post("/cloud_api")
def cloud_api(r: APIRequest) -> str | Dict:
    try:
        llm = init_model(
            {
                "mod_name": r.mod_name,
                "cls_name": r.cls_name,
                "args": r.init_args or {}
            }
        )
    except Exception as e:
        raise BaseCustomException(f"Failed to initialize model: {e}")
    if not r.run_args or not r.run_args.prompt:
        raise BaseCustomException("Prompt must not be empty")

    run_args = {"prompt": r.run_args.prompt} | (r.run_args.extra_args or {})
    if r.run_args.response_format is not None:
        run_args["response_format"] = r.run_args.response_format

    out = llm.run(**run_args)
    return out


@app.post("/async_cloud_api")
def async_cloud_api(r: List[APIRequest]) -> List[str | Dict]:
    if not r:
        raise BaseCustomException("Request list must not be empty")
    if not all(ri.mod_name == r[0].mod_name for ri in r):
        raise BaseCustomException("All mode_name must be the same")
    if not all(ri.cls_name == r[0].cls_name for ri in r):
        raise BaseCustomException("All cls_name must be the same")
    if not all(ri.init_args == r[0].init_args for ri in r):
        raise BaseCustomException("All init_args must be the same")
    try:
        llm = init_model(
            {
                "mod_name": r[0].mod_name,
                "cls_name": r[0].cls_name,
                "args": r[0].init_args or {}
            }
        )
    except Exception as e:
        raise BaseCustomException(f"Failed to initialize model: {e}")
    if any(not ri.run_args or not ri.run_args.prompt for ri in r):
        raise BaseCustomException("All prompts must not be empty")

    run_args_list = []
    for ri in r:
        args = {"prompt": ri.run_args.prompt} | (ri.run_args.extra_args or {})
        if ri.run_args.response_format is not None:
            args["response_format"] = ri.run_args.response_format
        run_args_list.append(args)
    
    out_list = async_executor(llm.arun, run_args_list)
    return out_list
