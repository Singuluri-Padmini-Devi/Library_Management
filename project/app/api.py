from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, books, users, librarian

def create_app() -> FastAPI:
    # Create database tables
    Base.metadata.create_all(bind=engine)

    app = FastAPI(title="Library Management System")

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth.router)
    app.include_router(books.router)
    app.include_router(users.router)
    app.include_router(librarian.router)

    return app