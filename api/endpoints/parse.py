import asyncio

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db, truncate_db_data
from errors import ParseError
from logger import log
from search import delete_all_documents
from services import parse_pdf

router = APIRouter()


@router.post("/upload", status_code=201)
async def upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    log.info("PDF received, starting file parsing")

    loop = asyncio.get_event_loop()
    file_bytes = await file.read()

    try:
        await loop.run_in_executor(None, parse_pdf, db, file_bytes)
    except ParseError as ex:
        # Truncate all stored data in the database
        truncate_db_data()
        # Delete all documents from elasticsearch
        delete_all_documents()

        message = f"There was an error in parsing the PDF file: {ex.detail}"
        log.error(message)
        return JSONResponse(content={"message": message}, status_code=ex.status_code)

    message = "PDF parsed and uploaded successfully"
    log.info(message)

    return {"message": message}
