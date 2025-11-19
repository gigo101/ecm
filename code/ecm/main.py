from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi.middleware.cors import CORSMiddleware
import jwt
import time
from datetime import datetime
from passlib.context import CryptContext
import os
from fastapi import UploadFile, File, Form
from fastapi.responses import JSONResponse


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# --- FASTAPI APP ---
app = FastAPI()

# --- CORS MUST BE BEFORE EVERYTHING ELSE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 AFTER CORS
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- CONFIG ---
DATABASE_URL = "mysql+pymysql://root:Dnsc2025**@localhost/ecmdb"
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

Base = declarative_base()   # MUST COME BEFORE MODELS

# --- DATABASE SETUP ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- USER MODEL ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    filepath = Column(String(500))
    description = Column(Text)
    uploaded_by = Column(String(255))
    uploaded_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

# --- TOKEN SCHEMA ---
class Token(BaseModel):
    access_token: str
    token_type: str

# Request body for registration
class UserCreate(BaseModel):
    email: str
    password: str

# --- DB DEPENDENCY ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Register API
@app.post("/auth/register")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check for duplicates
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_pw = hash_password(user.password)

    # Insert new user
    new_user = User(email=user.email, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


# --- LOGIN ---
@app.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Find user
    user = db.query(User).filter(User.email == form_data.username).first()

    # Compare plain text password (for now)
    #if not user or user.password != form_data.password:
    if not user or not verify_password(form_data.password, user.password):

        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Create token
    payload = {"sub": user.email, "exp": time.time() + 3600}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}

# --- PROTECTED ROUTE ---
@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"email": data["sub"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

#Document upload end point
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    description: str = Form(""),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    # Decode token
    try:
        user_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = user_data["sub"]
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Save file to disk
    file_location = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_location, "wb+") as f:
        f.write(await file.read())

    # Save to database
    document = Document(
        filename=file.filename,
        filepath=file_location,
        description=description,
        uploaded_by=user_email,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return {"message": "File uploaded successfully", "document_id": document.id}

#Document list endpoint
@app.get("/documents/list")
async def list_documents(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    # Verify user token
    try:
        user_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    docs = db.query(Document).order_by(Document.uploaded_at.desc()).all()

    return [
        {
            "id": d.id,
            "filename": d.filename,
            "description": d.description,
            "uploaded_by": d.uploaded_by,
            "uploaded_at": d.uploaded_at.strftime("%Y-%m-%d %H:%M")
        }
        for d in docs
    ]


from fastapi.staticfiles import StaticFiles

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")



#change password
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

@app.post("/auth/change-password")
async def change_password(
    req: ChangePasswordRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    # Decode token
    try:
        user_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = user_data["sub"]
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Get user
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check old password
    if not verify_password(req.old_password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    # Update new password
    user.password = hash_password(req.new_password)
    db.commit()

    return {"message": "Password updated successfully"}
