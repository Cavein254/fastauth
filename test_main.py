from fastapi.testclient import TestClient
from typing import Annotated
from pydantic import BaseModel
from fastapi import FastAPI


fake_secret = 'superduppersecret'

fake_db = {
    "foo": {"id": "foo", "title": "foo", "description": "This is foo"},
    "bar": {"id": "bar", "title": "bar", "description": "This is bar"}
}


app = FastAPI()

@app.get('/')
async def read_main():
    return {"msg":"Hello, world"}


client = TestClient(app)

class Item(BaseModel):
    id: str
    title: str
    description: str

def test_index_page():
    response = client.get('/')
    assert response.status_code == 200
