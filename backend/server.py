from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
import google.generativeai as genai
import uuid
import json

load_dotenv()

app = FastAPI(title="Nutracía API", version="1.0.0")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# MongoDB setup
MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL)
db = client.nutracia_db

# Gemini AI setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# JWT setup
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

# Pydantic models
class User(BaseModel):
    email: str
    password: str
    name: Optional[str] = None
    age: Optional[int] = None
    health_goals: Optional[List[str]] = []

class UserLogin(BaseModel):
    email: str
    password: str

class UserProfile(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    health_goals: Optional[List[str]] = []
    dietary_preferences: Optional[List[str]] = []
    fitness_level: Optional[str] = None

class ChatMessage(BaseModel):
    message: str
    user_id: str

class CartItem(BaseModel):
    product_name: str
    category: str
    price: float
    quantity: int

class CartSync(BaseModel):
    user_id: str
    items: List[CartItem]

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# API Routes
@app.get("/")
async def root():
    return {"message": "Nutracía API - Your Intelligent Wellness Companion"}

@app.post("/api/signup")
async def signup(user: User):
    try:
        # Check if user already exists
        existing_user = db.users.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(user.password)
        
        user_doc = {
            "id": user_id,
            "email": user.email,
            "password": hashed_password,
            "name": user.name,
            "age": user.age,
            "health_goals": user.health_goals,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        db.users.insert_one(user_doc)
        
        # Create access token
        access_token = create_access_token(data={"sub": user_id})
        
        return {
            "message": "User created successfully",
            "user_id": user_id,
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@app.post("/api/login")
async def login(user_login: UserLogin):
    try:
        # Find user
        user = db.users.find_one({"email": user_login.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not verify_password(user_login.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create access token
        access_token = create_access_token(data={"sub": user["id"]})
        
        return {
            "message": "Login successful",
            "user_id": user["id"],
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.get("/api/profile/{user_id}")
async def get_profile(user_id: str, current_user: str = Depends(get_current_user)):
    try:
        if current_user != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        user = db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Remove password from response
        user.pop("password", None)
        user.pop("_id", None)
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")

@app.put("/api/profile/{user_id}")
async def update_profile(user_id: str, profile: UserProfile, current_user: str = Depends(get_current_user)):
    try:
        if current_user != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        update_data = profile.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        result = db.users.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "Profile updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@app.get("/api/dashboard/{user_id}")
async def get_dashboard(user_id: str, current_user: str = Depends(get_current_user)):
    try:
        if current_user != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get user info
        user = db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get recent chat history
        chat_history = list(db.chat_history.find({"user_id": user_id}).sort("timestamp", -1).limit(5))
        
        # Get cart items
        cart = db.carts.find_one({"user_id": user_id})
        cart_items = cart.get("items", []) if cart else []
        
        # Create dashboard data
        dashboard = {
            "user_id": user_id,
            "name": user.get("name", "User"),
            "health_goals": user.get("health_goals", []),
            "recent_chats": len(chat_history),
            "cart_items_count": len(cart_items),
            "daily_tip": "Stay hydrated! Aim for 8 glasses of water daily for optimal wellness.",
            "last_updated": datetime.utcnow()
        }
        
        return dashboard
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")

@app.post("/api/cart/sync")
async def sync_cart(cart_data: CartSync, current_user: str = Depends(get_current_user)):
    try:
        if current_user != cart_data.user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        cart_doc = {
            "user_id": cart_data.user_id,
            "items": [item.dict() for item in cart_data.items],
            "updated_at": datetime.utcnow()
        }
        
        db.carts.replace_one(
            {"user_id": cart_data.user_id},
            cart_doc,
            upsert=True
        )
        
        return {"message": "Cart synced successfully", "items_count": len(cart_data.items)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync cart: {str(e)}")

@app.post("/api/chat/ai")
async def chat_with_ai(chat_message: ChatMessage, current_user: str = Depends(get_current_user)):
    try:
        if current_user != chat_message.user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get user context
        user = db.users.find_one({"id": chat_message.user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create context-aware prompt
        context = f"""
        You are Nutracía, an intelligent medical-grade AI wellness companion. 
        You provide evidence-based guidance on nutrition, skincare, and fitness.
        
        User Context:
        - Name: {user.get('name', 'User')}
        - Age: {user.get('age', 'Not specified')}
        - Health Goals: {', '.join(user.get('health_goals', []))}
        - Dietary Preferences: {', '.join(user.get('dietary_preferences', []))}
        - Fitness Level: {user.get('fitness_level', 'Not specified')}
        
        Always provide professional, evidence-based advice. If the question is outside your scope or requires medical diagnosis, recommend consulting a healthcare professional.
        
        User Question: {chat_message.message}
        """
        
        # Generate AI response
        response = model.generate_content(context)
        ai_response = response.text
        
        # Save chat history
        chat_record = {
            "user_id": chat_message.user_id,
            "user_message": chat_message.message,
            "ai_response": ai_response,
            "timestamp": datetime.utcnow()
        }
        db.chat_history.insert_one(chat_record)
        
        return {
            "message": "AI response generated",
            "response": ai_response,
            "timestamp": datetime.utcnow()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI chat failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)