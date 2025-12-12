from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm # <--- New Import
from app.models.auth import TokenResponse, LoginInput # Keep LoginInput if you want json support too, but we switch to form here
from app.services.auth_service import AuthService

router = APIRouter()

def get_auth_service():
    return AuthService()

@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), # <--- Changed input to Form
    service: AuthService = Depends(get_auth_service)
):
    # Map the form data to our service's expected input
    # Note: OAuth2 forms always use "username" and "password" fields.
    # So we put the email inside the "username" field.
    login_data = LoginInput(email=form_data.username, password=form_data.password)
    
    return service.login(login_data)