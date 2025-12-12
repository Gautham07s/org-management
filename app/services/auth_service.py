from fastapi import HTTPException
from app.database.connection import db_manager
from app.models.auth import LoginInput, TokenResponse
from app.core.security import SecurityHandler

class AuthService:
    def __init__(self):
        self.db = db_manager.get_database()
        self.users_collection = self.db["users"]

    def login(self, login_data: LoginInput) -> TokenResponse:
        # 1. Find user by email
        user = self.users_collection.find_one({"email": login_data.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # 2. Verify Password
        if not SecurityHandler.verify_password(login_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # 3. Create Token Payload (What info is inside the badge?)
        # We put the User ID and Org Name inside the token
        token_data = {
            "sub": str(user["_id"]),
            "org_name": user["organization_name"],
            "role": user["role"]
        }
        
        # 4. Generate Token
        token = SecurityHandler.create_access_token(token_data)

        return TokenResponse(access_token=token, token_type="bearer")