from fastapi import (
    FastAPI,
    Query,
    Path,
    Body,
    Form,
    Header,
    BackgroundTasks,
    File,
    status,
)
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse, PlainTextResponse
from enum import Enum
from typing import Annotated, List, Union, Optional
from pydantic import BaseModel, Field, EmailStr
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


class Hello(str, Enum):
    Ritvik = "ritvik"
    Ramesh = "ramesh"


class ISBN(BaseModel):
    publisher: str = Field(default="", max_length=100)
    address: str = Field(default="", max_length=100)


class Item(BaseModel):
    name: str = Field(default="", min_length=5, max_length=100)
    price: float = Field(
        default=0.0, description="This is price", gt=100.00, lt=20000.00
    )
    phone: str = Field(default="", regex="^[0-9]{10}$", max_length=10)
    is_offer: Optional[bool] = None
    students: List[str] = Field(default_factory=lambda: ["ramesh", "rakesh"])
    isbn: Optional[ISBN] = None
    email: Optional[EmailStr] = None


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.post("/body", response_description="This is a response", summary="Summary")
def read_item(
    item: ISBN = Body(...),
):
    """
    Hello I am Doc
    """
    return {"item": item}


@app.post("/hello/{name}", response_description="This is a response", summary="Summary")
async def read_item(
    name: Annotated[str, Path(..., max_length=20)],
):
    """
    Hello I am Doc
    """
    return {"path": name}


@app.get("/redirect")
async def redirect():
    """
    Redirects to YouTube.
    """
    return RedirectResponse(url="https://www.youtube.com")


@app.get("/json")
async def json():
    """
    Returns a JSON response.
    """
    return JSONResponse(content={"message": "Hello"})


@app.post("/form")
async def form_handle(
    username: Annotated[str, Form(default=""), Query(..., min_length=3, max_length=20)],
    password: Annotated[str, Form(default=""), Query(..., min_length=8, max_length=20)],
):
    """
    Handles form data.
    """
    return {"username": username, "password": password}


@app.post("/files/")
async def create_file(
    file: Annotated[
        bytes,
        File(None),
    ]
):
    """
    Creates a file.
    """
    return {"file_size": len(file)}


def task(data: str):
    with open("./file.txt", "a+") as f:
        f.write(data + "\n")


@app.get("/header")
async def header(x_token: Annotated[str, Header(None)], background: BackgroundTasks):
    """
    Handles headers with background task.
    """
    background.add_task(task, data=x_token)
    return {"header": x_token}


@app.get("/query")
def handle_query(skip: int = 0, limit: int = 10):
    """
    Handles query parameters.
    """
    db = [{"name": "Ramesh"}, {"name": "Rajesh"}, {"name": "Rakesh"}, {"name": "Rahul"}]
    return db[skip : skip + limit]


@app.get("/query2")
def handle_query(q: Union[str, None]):
    """
    Handles query parameters.
    """
    return {"query": q}
