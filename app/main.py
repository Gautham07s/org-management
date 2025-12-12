from fastapi import FastAPI
from app.database.connection import db_manager
from app.routes.org_routes import router as org_router
from app.routes.auth_routes import router as auth_router # Import Auth Router

app = FastAPI(title="Org Management Service")

@app.on_event("startup")
def startup_db_client():
    db_manager.connect()

@app.on_event("shutdown")
def shutdown_db_client():
    db_manager.close()

# Include Routers
app.include_router(org_router, prefix="/org", tags=["Organization"])
app.include_router(auth_router, prefix="/admin", tags=["Authentication"]) # Add this line

@app.get("/")
def read_root():
    return {"message": "Server is running"}