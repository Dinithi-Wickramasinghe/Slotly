from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from . import models
from .routers import auth_routes, availability, public

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Slotly API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(availability.router)
app.include_router(public.router)


@app.get("/")
def health():
    return {"status": "ok"}