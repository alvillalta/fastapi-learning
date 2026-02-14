from fastapi import FastAPI, WebSocket, Path
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from src.routes.auth_routes import app as auth_router
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    yield
    print("Shutting down...")  

@app.middleware("http")
async def log_request(request, call_next):
    print(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    response.headers["X-Custom-Header"] = "CustomValue"
    print(f"Response status code: {response.status_code}")
    return response 

connected_clients = []

@app.websocket("/ws/data")
async def websocket_endpoint(websocket: WebSocket): 
    await websocket.accept() 
    connected_clients.append(websocket)
    try:
        while True: 
            await websocket.receive_text()
    except:
        connected_clients.remove(websocket)

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

class Item(BaseModel):
    id: int
    name: str
    age: int

items = [{"id": 1, "name": "Juan", "age": 10}, {"id": 2, "name": "Javier", "age": 20}]

@app.post("/items")
async def create_item(item: Item):
    new_item = {"id": len(items) + 1, "name": item.name, "age": item.age}
    items.append(new_item)
    return items

@app.get("/items/{item_id}")
async def get_item(item_id: int = Path(..., description="The ID of the item to retrieve", gt=0)):
    return items[item_id]
 
@app.get("/get-by-name/{item_id}")
def get_item(item_id: int, name: str):
    for item in items:
        if item["id"] == item_id and item["name"] == name:
            return item
    return {"message": "Item not found"}

class Student(BaseModel):
    name: str
    age: int

students = {
    1: {"name": "Alice", "age": 20}, 
    2: {"name": "Bob", "age": 22}
}

@app.post("/students/{student_id}")
async def create_student(student_id: int, student: Student):
    if student_id in students:
        return {"message": "Student ID already exists"}
    students[student_id] = student
    return students[student_id]

class UpdateStudent(BaseModel):
    name: Optional[str] = None
    age: int = None

@app.put("/students/{student_id}")
async def update_student(student_id: int, student: UpdateStudent):
    if student_id not in students:
        return {"message": "Student not found"}
    if student.name is not None:
        students[student_id]["name"] = student.name 
    if student.age is not None:
        students[student_id]["age"] = student.age
    return students[student_id]

@app.delete("/students/{student_id}")
async def delete_student(student_id: int):
    if student_id not in students:
        return {"message": "Student not found"}
    del students[student_id]
    return {"message": "Student deleted"}