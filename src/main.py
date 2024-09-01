from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from src import database
from src.routes import form_router, user_router, data_entry_router
import logging

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.on_event("startup")
def startup():
    database.Base.metadata.create_all(bind=database.engine)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log message format
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file
        logging.StreamHandler()  # Log to console
    ]
)

logger = logging.getLogger(__name__)

# Store the original app.openapi method
original_openapi = app.openapi

# Add security definitions to the OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        logger.info("Schema already exists")
        return app.openapi_schema
    openapi_schema = original_openapi()
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


# Include routers
app.include_router(form_router, prefix="/api", tags=["Forms"])
app.include_router(user_router, prefix="/api", tags=["Users"])
app.include_router(data_entry_router, prefix="/api", tags=["Data Entry"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "OK"}

# Example endpoint that requires authentication
@app.get("/secure-endpoint", tags=["Secure"], dependencies=[Depends(oauth2_scheme)])
def secure_endpoint():
    return {"message": "This is a secure endpoint"}