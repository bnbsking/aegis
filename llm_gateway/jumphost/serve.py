import logging
import os
import traceback
from typing import Dict, List, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from llm_client.async_funcs import async_executor
from llm_client.llm_calls import init_model
from pydantic import BaseModel
import yaml

from jumphost import response_format_preprocess
from jumphost.binary_base64_converter import recursive_convert_b64dict_to_binary
from jumphost.exceptions import BaseCustomException
from jumphost.logs import setup_logging


setup_logging()
logger = logging.getLogger(__name__)


cfg = yaml.safe_load(open(os.environ["BASE_CFG_PATH"], "r"))
llm_chat_cfg = cfg["llm_chat_cfg"]
response_format_preprocess_cfg = cfg.get("response_format_preprocess", {})


llms = {}
for key, args in llm_chat_cfg.items():
    try:
        if key in response_format_preprocess_cfg:
            response_format_preprocess_func = getattr(
                response_format_preprocess,
                response_format_preprocess_cfg[key]
            )
        else:
            response_format_preprocess_func = None

        llms[key] = {
            "model": init_model(args),
            "response_format_preprocess_func": response_format_preprocess_func
        }
    except Exception as e:
        logger.error(f"key: {key}, args: {args}, error: {e}, full traceback: {traceback.format_exc()}")
logger.info(f"valid llm keys: {list(llms.keys())}")
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


class APIRequest(BaseModel):
    key: str
    prompt: str | List[Dict]
    response_format: Optional[Dict] = None
    extra_args: Optional[Dict] = None
    

@app.post("/cloud_api")
def cloud_api(r: APIRequest) -> str | Dict:
    if r.key not in llms:
        raise BaseCustomException(f"Invalid key: {r.key}")
    if not r.prompt:
        raise BaseCustomException("Prompt must not be empty")
    llm = llms.get(r.key, None)

    if isinstance(r.prompt, List):
        prompt_ = recursive_convert_b64dict_to_binary(r.prompt)
    else:
        prompt_ = r.prompt
    args = {"prompt": prompt_} | (r.extra_args or {})

    if r.response_format is not None:
        if llm["response_format_preprocess_func"] is not None:
            args["response_format"] = llm["response_format_preprocess_func"](
                "custom",
                r.response_format
            )
        else:
            args["response_format"] = r.response_format

    out = llm["model"].run(**args)
    return out


@app.post("/async_cloud_api")
def async_cloud_api(r: List[APIRequest]) -> List[str | Dict]:
    if not r:
        raise BaseCustomException("Request list must not be empty")
    if r[0].key not in llms:
        raise BaseCustomException(f"Invalid key: {r[0].key}")
    if not all(ri.key == r[0].key for ri in r):
        raise BaseCustomException("All keys must be the same")
    if any(not ri.prompt for ri in r):
        raise BaseCustomException("All prompts must not be empty")
    llm = llms[r[0].key]

    arg_list = []
    for ri in r:
        if isinstance(ri.prompt, List):
            prompt_ = recursive_convert_b64dict_to_binary(ri.prompt)
        else:
            prompt_ = ri.prompt
        args = {"prompt": prompt_} | (ri.extra_args or {})

        if ri.response_format is not None:
            if llm["response_format_preprocess_func"] is not None:
                args["response_format"] = llm["response_format_preprocess_func"](
                    "custom",
                    ri.response_format
                )
            else:
                args["response_format"] = ri.response_format
        arg_list.append(args)
    
    out_list = async_executor(llm["model"].arun, arg_list)
    return out_list
