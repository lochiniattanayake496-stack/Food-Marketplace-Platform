from typing import List
from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UserModel
from app.schemas import UserResponse, UserSyncRequest, UserUpdateRequest
from app.seed import init_db

app = FastAPI(
    title="User Microservice API",
    description="Manages user profiles and aligns with AWS Cognito for authentication and authorization.",  
    version="1.0.0",
)

@app.on_event("startup")
def on_startup():
    init_db()

#---GET ALL USERS (ADMIN/ DATA STEWARDS)---#

@app.get("/api/v1/users", response_model=List[UserResponse])
def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)

):
    offset = (page - 1) * limit
    return db.query(UserModel).offset(offset).limit(limit).all()

#--CREATE USER PROFILE--#
@app.post("/api/v1/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserSyncRequest, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_data.id).first()
    if user:
        user.email = user_data.email
        user.role = user_data.role
        user.name = user_data.name
    else:
        user = UserModel(
            id=user_data.id,
            email=user_data.email,
            role=user_data.role,
            name=user_data.name,
            status="ACTIVE"
        )
        db.add(user)

    db.commit()
    db.refresh(user)    
    return user

#--GET USER PROFILE BY ID--#

@app.get("/api/v1/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

#--UPDATE USER --#

@app.patch("/api/v1/users/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user_update: UserUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    

    update_data = user_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    
    db.commit()
    db.refresh(user)
    return user   


#--DELETE USER PROFILE--#

@app.delete("/api/v1/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}
  
    
          