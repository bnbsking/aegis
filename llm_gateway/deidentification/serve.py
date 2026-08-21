import logging
import os
import traceback
from typing import Dict, List, Optional

from fastapi import FastAPI
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from llm_client.async_funcs import async_executor
from llm_client.llm_calls import init_model
from pydantic import BaseModel
import yaml

from deid.exceptions import BaseCustomException
from deid.logs import setup_logging
from deid.main import DeidPipeline


cfg = yaml.safe_load(open(os.environ["BASE_CFG_PATH"], "r"))
llm_cloud = init_model(cfg['cloud_llm_cfg'])
deid_registry = {}  # str -> DeidPipeline
for key, path in cfg['main_cfg_list'].items():
    pipeline_args = yaml.safe_load(open(path, "r"))['pipeline_args']
    pipeline = DeidPipeline(**pipeline_args)
    deid_registry[key] = pipeline
setup_logging()
logger = logging.getLogger(__name__)
logger.info("Start serving API...")
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
    base_text: str | List
    raw_text: str
    response_format_dict: Optional[Dict] = None
    

@app.post("/cloud_api")
def cloud_api(r: APIRequest) -> Dict:
    pipeline = deid_registry.get(r.key, None)
    if pipeline is None:
        raise BaseCustomException(f"Invalid key: {r.key}")

    deid_text = pipeline.run(r.raw_text)
    if deid_text.startswith("[Deid_failed]"):
        return {"succeed": False, "deid_text": deid_text, "output": ""}

    if isinstance(r.base_text, list):
        prompt = [
            {**msg, "content": msg["content"].replace("{{ deid_text }}", deid_text)}
            if isinstance(msg.get("content"), str) else msg
            for msg in r.base_text
        ]
    else:
        prompt = r.base_text.replace("{{ deid_text }}", deid_text)
    out = llm_cloud.run(prompt=prompt, response_format=r.response_format_dict)
    return {"succeed": True, "deid_text": deid_text, "output": out}


@app.post("/async_cloud_api")
def async_cloud_api(r: List[APIRequest]) -> List[Dict]:
    if not r:
        raise BaseCustomException("Request list must not be empty")
    if not all(ri.key == r[0].key for ri in r):
        raise BaseCustomException("All keys must be the same")
    pipeline = deid_registry.get(r[0].key, None)
    if pipeline is None:
        raise BaseCustomException(f"Invalid key: {r[0].key}")

    arg_list = []
    deid_text_list = []  # (deid_passed, deid_text)
    for ri in r:
        deid_text = pipeline.run(ri.raw_text)
        if deid_text.startswith("[Deid_failed]"):
            deid_text_list.append((False, deid_text))
        else:
            deid_text_list.append((True, deid_text))
            if isinstance(ri.base_text, list):
                prompt = [
                    {**msg, "content": msg["content"].replace("{{ deid_text }}", deid_text)}
                    if isinstance(msg.get("content"), str) else msg
                    for msg in ri.base_text
                ]
            else:
                prompt = ri.base_text.replace("{{ deid_text }}", deid_text)
            arg_list.append(
                {
                    "prompt": prompt,
                    "response_format": ri.response_format_dict
                }
            )
    out_list = async_executor(llm_cloud.arun, arg_list) if arg_list else []
    out_list.reverse()

    return_list = []
    for i in range(len(r)):
        if deid_text_list[i][0]:
            return_list.append({"succeed": True, "deid_text": deid_text_list[i][1], "output": out_list.pop()})
        else:
            return_list.append({"succeed": False, "deid_text": deid_text_list[i][1], "output": ""})
    return return_list
