import logging
import traceback
from typing import List

from fastapi import FastAPI, File, Request, UploadFile, Form, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.exceptions import BaseCustomException
from src.logs import setup_logging
from src.main import DocIntelLayout


setup_logging()
ocr = DocIntelLayout()
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


class UploadRequest(BaseModel):
    extra_msg: str

    @classmethod
    def as_form(cls, extra_msg: str = Form(...)):
        return cls(extra_msg=extra_msg)


@app.post("/run_pdf_list")
def run_pdf_list(
        files: list[UploadFile] = File(...),
        meta: UploadRequest = Depends(UploadRequest.as_form)
    ) -> List:
    pdf_bytes_list = [f.file.read() for f in files]
    out = ocr.run_pdf_list(pdf_bytes_list)
    return out
