from fastapi import HTTPException
from app.database.connection import db_manager
from app.models.org import OrganizationCreate, OrganizationResponse, OrganizationUpdate
from app.core.security import SecurityHandler

class OrganizationService:
    def __init__(self):
        # We access the Master DB
        self.db = db_manager.get_database()
        self.org_collection = self.db["organizations"]
        self.users_collection = self.db["users"]

    def create_organization(self, data: OrganizationCreate) -> OrganizationResponse:
        # 1. Validate: Check if organization name already exists
        if self.org_collection.find_one({"organization_name": data.organization_name}):
            raise HTTPException(status_code=400, detail="Organization already exists")

        # 2. Check if admin email is already used (Optional but good practice)
        if self.users_collection.find_one({"email": data.email}):
            raise HTTPException(status_code=400, detail="Email already registered")

        # 3. Dynamic Collection Naming
        # Example: if name is "Tesla", collection is "org_Tesla"
        # We replace spaces with underscores to be safe
        safe_name = data.organization_name.replace(" ", "_")
        dynamic_collection_name = f"org_{safe_name}"

        # 4. Hash the password
        hashed_password = SecurityHandler.get_password_hash(data.password)

        # 5. Create the Admin User Document (Stored in Master DB as per requirements)
        admin_user = {
            "email": data.email,
            "password": hashed_password,
            "role": "admin",
            "organization_name": data.organization_name
        }
        user_result = self.users_collection.insert_one(admin_user)

        # 6. Create the Organization Metadata Document
        new_org = {
            "organization_name": data.organization_name,
            "collection_name": dynamic_collection_name,
            "admin_id": str(user_result.inserted_id), # Reference to the admin user
            "created_at": None # You can add a timestamp here if you like
        }
        self.org_collection.insert_one(new_org)

        # 7. Dynamically Create the Tenant Collection
        # In MongoDB, a collection is created automatically when you insert data.
        # We will insert a dummy config document to initialize it.
        tenant_db = self.db # In this simple design, we use the same DB, just different collections
        tenant_collection = tenant_db[dynamic_collection_name]
        tenant_collection.insert_one({"type": "config", "initialized": True})

        return OrganizationResponse(
            organization_name=data.organization_name,
            collection_name=dynamic_collection_name,
            admin_email=data.email,
            message="Organization created successfully"
        )
    def get_organization(self, org_name: str):
        org = self.org_collection.find_one({"organization_name": org_name})
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Convert ObjectId to string for JSON compatibility
        org["_id"] = str(org["_id"])
        return org

    def delete_organization(self, org_name: str, current_user: dict):
        # 1. Check if Organization exists
        org = self.org_collection.find_one({"organization_name": org_name})
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # 2. Security Check: ensure the logged-in admin owns this org
        # (Assuming the token user belongs to the org they are trying to delete)
        if current_user["organization_name"] != org_name:
            raise HTTPException(status_code=403, detail="Not authorized to delete this organization")

        # 3. Delete the Metadata
        self.org_collection.delete_one({"organization_name": org_name})

        # 4. Delete the Admin User associated with it
        self.users_collection.delete_one({"organization_name": org_name})

        # 5. Drop the Dynamic Collection (The Tenant Data)
        collection_name = org["collection_name"]
        self.db.drop_collection(collection_name)

        return {"message": f"Organization {org_name} and its data have been deleted"}
    
    def update_organization(self, current_org_name: str, data: OrganizationUpdate):
        # 1. Check if the NEW name is already taken
        if data.new_organization_name != current_org_name:
            if self.org_collection.find_one({"organization_name": data.new_organization_name}):
                raise HTTPException(status_code=400, detail="Organization name already exists")

        # 2. Verify Admin Credentials (Security Check)
        # We need to find the admin for the CURRENT org
        admin = self.users_collection.find_one({"organization_name": current_org_name, "email": data.email})
        if not admin or not SecurityHandler.verify_password(data.password, admin["password"]):
             raise HTTPException(status_code=401, detail="Invalid admin credentials")

        # 3. Rename the Collection (Sync Data)
        old_org_metadata = self.org_collection.find_one({"organization_name": current_org_name})
        old_collection_name = old_org_metadata["collection_name"]
        
        new_safe_name = data.new_organization_name.replace(" ", "_")
        new_collection_name = f"org_{new_safe_name}"

        # MongoDB Rename Command (Atomic and Fast)
        if old_collection_name != new_collection_name:
            self.db[old_collection_name].rename(new_collection_name)

        # 4. Update Metadata in Master DB
        self.org_collection.update_one(
            {"organization_name": current_org_name},
            {"$set": {
                "organization_name": data.new_organization_name,
                "collection_name": new_collection_name
            }}
        )

        # 5. Update Admin User Reference
        self.users_collection.update_one(
            {"organization_name": current_org_name},
            {"$set": {"organization_name": data.new_organization_name}}
        )

        return {"message": "Organization updated and data synced successfully", "new_name": data.new_organization_name}