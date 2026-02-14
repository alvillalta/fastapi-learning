from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from src.routes.auth_routes import app as auth_router

class Item(BaseModel):
    name: str
    age: int

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

@app.post("/items")
async def create_item(item: Item):
    return {"item": item, "name": item.name, "age": item.age}
