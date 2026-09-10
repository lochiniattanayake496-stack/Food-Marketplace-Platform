from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.controller.product_controller import router as product_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Product Microservice API",
    description="Handles product catalog management, supplier submissions and Data Steward approvals.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product_router)

