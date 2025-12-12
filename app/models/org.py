from pydantic import BaseModel, EmailStr

# Input Schema: What the user sends to us
class OrganizationCreate(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

# Output Schema: What we return to the user (No password!)
class OrganizationResponse(BaseModel):
    organization_name: str
    collection_name: str
    admin_email: str
    message: str
# Add this class to your existing imports
class OrganizationUpdate(BaseModel):
    new_organization_name: str
    email: str # To verify or update admin email
    password: str # To verify admin password