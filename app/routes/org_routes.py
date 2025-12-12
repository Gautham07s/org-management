from fastapi import APIRouter, Depends
from app.models.org import OrganizationCreate, OrganizationResponse
from app.services.org_service import OrganizationService
from app.core.deps import get_current_user # Import the security dependency

router = APIRouter()

def get_org_service():
    return OrganizationService()

# 1. Create (Public)
@router.post("/create", response_model=OrganizationResponse)
def create_organization(
    org_data: OrganizationCreate, 
    service: OrganizationService = Depends(get_org_service)
):
    return service.create_organization(org_data)

# 2. Get (Public or Protected - let's make it Public for now as per requirement 2)
@router.get("/get")
def get_organization(
    organization_name: str,
    service: OrganizationService = Depends(get_org_service)
):
    return service.get_organization(organization_name)

# 3. Delete (Protected! Needs Token)
@router.delete("/delete")
def delete_organization(
    organization_name: str,
    service: OrganizationService = Depends(get_org_service),
    current_user: dict = Depends(get_current_user) # This forces the user to be logged in
):
    return service.delete_organization(organization_name, current_user)
# 4. Update (Protected)
from app.models.org import OrganizationUpdate # Import the new model

@router.put("/update")
def update_organization(
    update_data: OrganizationUpdate,
    service: OrganizationService = Depends(get_org_service),
    current_user: dict = Depends(get_current_user)
):
    # We use the org_name from the token (current_user) to ensure they only edit their own org
    current_org_name = current_user["organization_name"]
    return service.update_organization(current_org_name, update_data)