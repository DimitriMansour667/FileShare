from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
from typing import Optional
import os

from sqlmodel import Field, SQLModel, create_engine, Session, select


class File(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    size: int
    file_path: str


engine = create_engine("sqlite:///database.db")


common_path = "F:\Project A\FileShare\server\/files\/"


app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:5173/files"
]



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

valid_passcode = "1234"

@app.get("/connect/{id}")
def read_root(id: str):
    if valid_passcode == id:
        return {"status": "connected"}
    else:
        return {"status": "error"}

@app.get("/{id}/files")
def read_files(id: str):
    if read_root(id)["status"] == "error":
        return {"status": "error"}
    else:
        with Session(engine) as session:
            files = session.exec(select(File)).all()
            return files

@app.get("/{id}/storage")
def read_storage(id: str):
    if read_root(id)["status"] == "error":
        return {"status": "error"}
    else:
        total, used, free = shutil.disk_usage("/")
        return {"total": total, "used": used, "free": free}

@app.get("/{id}/file/{file_id}/download")
def read_file(id: str, file_id: str):
    if read_root(id)["status"] == "error":
        return {"status": "error"}
    else:
        with Session(engine) as session:
            file = session.exec(select(File).where(File.id == file_id)).first()
            file_path = file.file_path
            #return whole file as blob
            try:
                return FileResponse(file_path)
            except:
                return {"status": "error", "message": "file not found in server"}

@app.post("/{id}/file/upload")
async def create_upload_file(id: str, file: UploadFile):
    if read_root(id)["status"] == "error":
        return {"status": "error"}
    else:
        # save file to server
        with open(common_path + file.filename, "wb") as buffer:
            buffer.write(file.file.read())
        with Session(engine) as session:
            new_file = File(name=file.filename, size=os.path.getsize(common_path + file.filename), file_path=common_path + file.filename)
            session.add(new_file)
            session.commit()
        return {"status": "success"}
    
@app.delete("/{id}/file/{file_id}/delete")
def delete_file(id: str, file_id: int):
    if read_root(id)["status"] == "error":
        return {"status": "error"}
    else:
        with Session(engine) as session:
            file = session.exec(select(File).where(File.id == file_id)).first()
            session.delete(file)
            session.commit()
            try:
                os.remove(file.file_path)
            except FileNotFoundError:
                return {"status": "success", "message": "file deleted but not found in server"}
        return {"status": "success"}