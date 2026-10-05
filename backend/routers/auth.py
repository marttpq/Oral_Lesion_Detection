import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta
from google.oauth2 import id_token
from google.auth.transport import requests

import models, schemas, auth_utils
from database import get_db

router = APIRouter(prefix="/api/auth", tags=["Auth"])
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "dummy-client-id")

@router.post("/register", response_model=schemas.UserOut)
async def register(user_data: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(models.User).where(models.User.email == user_data.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_pwd = auth_utils.get_password_hash(user_data.password)
    new_user = models.User(
        email=user_data.email, 
        hashed_password=hashed_pwd,
        is_google_auth=False
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
async def login(user_data: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.email == user_data.email))
    user = result.scalars().first()
    
    if not user or user.is_google_auth:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    if not auth_utils.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    access_token_expires = timedelta(minutes=auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_utils.create_access_token(
        data={"sub": user.email, "id": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/google", response_model=schemas.Token)
async def google_auth(request_data: schemas.GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo", 
                headers={"Authorization": f"Bearer {request_data.credential}"}
            )
            if response.status_code != 200:
                raise ValueError("Invalid credentials")
            user_info = response.json()
            
        email = user_info.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Google token missing email")

        picture = user_info.get("picture")

        result = await db.execute(select(models.User).where(models.User.email == email))
        user = result.scalars().first()
        
        if not user:
            # Create user
            user = models.User(email=email, hashed_password=None, is_google_auth=True)
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            if not user.is_google_auth:
                # Update if needed
                user.is_google_auth = True
                await db.commit()

        access_token_expires = timedelta(minutes=auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
        # Embed the picture string directly into the JWT without mutating DB schema!
        access_token = auth_utils.create_access_token(
            data={"sub": user.email, "id": user.id, "picture": picture}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Google token")
