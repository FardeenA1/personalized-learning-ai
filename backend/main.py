from fastapi import FastAPI

from database import initialize_database
from router.user_profile import router as profile_router

from router.auth import router as user_router
from router.style_profile import router as style_router
from router.generation import router as generation_router
from router.admin import router as admin_router
...


app = FastAPI(title="StyleNotes AI", version="1.0")

initialize_database()

app.include_router(user_router)
app.include_router(style_router)
app.include_router(generation_router)
app.include_router(admin_router)

@app.get("/")
def home():
    return {"message": "Backend Running"}

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)