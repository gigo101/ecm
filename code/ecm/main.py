from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import JSON
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi.middleware.cors import CORSMiddleware
import jwt
import time
from datetime import datetime
from passlib.context import CryptContext
import os
from fastapi import UploadFile, File, Form
from fastapi.responses import JSONResponse
from nlp_utils import extract_text_from_file, classify_document
from fastapi.responses import FileResponse
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from nlp_utils import get_relevant_sentences
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

embedder = SentenceTransformer("all-MiniLM-L6-v2")


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def require_role(required_roles: list):
    def role_checker(user):
        if user.role not in required_roles:
            raise HTTPException(status_code=403, detail="Access denied")
    return role_checker


# --- FASTAPI APP ---
app = FastAPI()

# --- CORS MUST BE BEFORE EVERYTHING ELSE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
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

    first_name = Column(String(255))
    middle_name = Column(String(255))
    last_name = Column(String(255))
    suffix = Column(String(50), nullable=True)
    position = Column(String(255))
    office = Column(String(255))

    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))

    role = Column(String(50), default="Viewer")
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# --- DOCUMENT MODEL ---
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    filepath = Column(String(500))
    description = Column(Text)
    category = Column(String(100), default="General")

    year_approved = Column(Integer, nullable=True)   # ✅ NEW FIELD

    document_type = Column(String(50), default="Public")
    uploaded_by = Column(String(255))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    embedding = Column(JSON)  # ⭐ ADD THIS


# --- TOKEN SCHEMA ---
class Token(BaseModel):
    access_token: str
    token_type: str

# Request body for registration

class UserCreate(BaseModel):
    first_name: str
    middle_name: str
    last_name: str
    suffix: str | None = None
    position: str
    office: str
    email: str
    password: str

class UserStatusUpdate(BaseModel):
    is_active: bool

class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)


class Office(Base):
    __tablename__ = "offices"

    id = Column(Integer, primary_key=True, index=True)
    office_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), unique=True, nullable=False)

class DocumentLog(Base):
    __tablename__ = "document_logs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, index=True)
    user_email = Column(String(255))
    action = Column(String(50))        # VIEW
    source = Column(String(50))        # LIST | SEMANTIC_SEARCH
    accessed_at = Column(DateTime, default=datetime.utcnow)


class DownloadRequest(Base):
    __tablename__ = "download_requests"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, index=True)
    document_name = Column(String(255))
    requester_email = Column(String(255))
    reason = Column(Text, nullable=True)
    status = Column(String(20), default="PENDING")  # PENDING | APPROVED | REJECTED
    requested_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)
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

    # Check duplicate email
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_pw = hash_password(user.password)

    # Create user
    new_user = User(
        first_name=user.first_name,
        middle_name=user.middle_name,
        last_name=user.last_name,
        suffix=user.suffix,
        position=user.position,
        office=user.office,
        email=user.email,
        password=hashed_pw,
        role="Viewer",  # Default role
    )

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

    # If user does not exist
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Block inactive users
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Your account has been deactivated. Please contact the administrator."
        )

    # Password check
    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Create token
    payload = {"sub": user.email, "exp": time.time() + 3600}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}


# Protected Route
@app.get("/users/me")
async def read_users_me(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Query the full User model
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "email": user.email,
        "first_name": user.first_name,
        "middle_name": user.middle_name,
        "last_name": user.last_name,
        "name": f"{user.first_name} {user.middle_name or ''} {user.last_name}".strip(),
        "role": user.role
    }



def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = data["sub"]
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user



#Document upload end point
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# @app.post("/documents/upload")
# async def upload_document(
#     file: UploadFile = File(...),
#     description: str = Form(""),
#     category: str = Form("General"),
#     document_type: str = Form("Public"),
#     current_user = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     require_role(["Admin", "Uploader"])(current_user)

#     # Save file temporarily to extract its text
#     file_location = f"{UPLOAD_DIR}/{file.filename}"
#     with open(file_location, "wb+") as f:
#         f.write(await file.read())

#     # NLP Classification
#     if category == "Auto":
#         file_text = extract_text_from_file(file_location)
#         combined_text = f"{description}\n{file_text}"

#         category = classify_document(combined_text)
#         print("AUTO CATEGORY:", category)

#     # Save document record
#     document = Document(
#         filename=file.filename,
#         filepath=file_location,
#         description=description,
#         category=category,
#         document_type=document_type,
#         uploaded_by=current_user.email
#     )

#     db.add(document)
#     db.commit()
#     db.refresh(document)

#     return {
#         "message": "File uploaded successfully",
#         "auto_category": category
#     }

from pathlib import Path
import re

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    description: str = Form(""),
    category: str = Form("General"),
    year_approved: int = Form(None),
    document_type: str = Form("Public"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_role(["Admin", "Uploader"])(current_user)

    # ✅ 1. Get user's office
    user_office = current_user.office or "UNKNOWN"

    # ✅ 2. Sanitize office (safe for filenames)
    safe_office = re.sub(r"[^A-Za-z0-9]", "_", user_office).upper()

    # ✅ 3. Get original filename safely
    original_name = Path(file.filename).name

    # ✅ 4. Build new filename
    new_filename = f"{safe_office}_{original_name}"

    # ✅ 5. Save file using new filename
    file_location = os.path.join(UPLOAD_DIR, new_filename)

    with open(file_location, "wb+") as f:
        f.write(await file.read())

    # NLP auto classification
    if category == "Auto":
        file_text = extract_text_from_file(file_location)
        combined_text = f"{description}\n{file_text}"
        category = classify_document(combined_text)
    else:
        # Still extract text for embeddings even if category is manual
        file_text = extract_text_from_file(file_location)

    # =====================================================
    # ⭐ STEP 4 — GENERATE SEMANTIC EMBEDDING (PUT HERE)
    # =====================================================
    embedding = embedder.encode(
        file_text[:5000] if file_text else f"{description} {file.filename}"
    ).tolist()

    # ✅ 6. Save document record with updated filename
    document = Document(
        filename=new_filename,
        filepath=file_location,
        description=description,
        category=category,
        year_approved=year_approved,
        document_type=document_type,
        uploaded_by=current_user.email,
        embedding=embedding  # ⭐ SAVE EMBEDDING
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "message": "File uploaded successfully",
        "filename": new_filename,
        "auto_category": category,
        "year_approved": year_approved
    }




#Document list endpoint
@app.get("/documents/list")
async def list_documents(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Document)

    if current_user.role == "Viewer":
        query = query.filter(Document.document_type == "Public")

    elif current_user.role in ["Faculty", "Staff"]:
        query = query.filter(Document.document_type != "Confidential")

    # Admin, Uploader, Management → see all

    docs = query.order_by(Document.uploaded_at.desc()).all()

    return [
        {
            "id": d.id,
            "filename": d.filename,
            "description": d.description,
            "category": d.category,
            "year_approved": d.year_approved,
            "document_type": d.document_type,
            "uploaded_by": d.uploaded_by,
            "uploaded_at": d.uploaded_at.strftime("%Y-%m-%d %H:%M"),
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

@app.get("/admin/users")
def list_all_users(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_role(["Admin"])(current_user)
    return db.query(User).all()


@app.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(Document.id == doc_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # ✅ ADMIN can delete any document
    if current_user.role == "Admin":
        pass

    # ✅ UPLOADER can delete ONLY their own uploads
    elif current_user.role == "Uploader":
        if document.uploaded_by != current_user.email:
            raise HTTPException(status_code=403, detail="You can only delete your own uploads")

    # ❌ Everyone else cannot delete
    else:
        raise HTTPException(status_code=403, detail="Access denied")

    # Delete file from disk
    if os.path.exists(document.filepath):
        os.remove(document.filepath)

    db.delete(document)
    db.commit()

    return {"message": "Document deleted successfully"}


#Get all users - Admin only
@app.get("/users")
async def list_users(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_role(["Admin"])(current_user)

    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "first_name": u.first_name,
            "middle_name": u.middle_name,
            "last_name": u.last_name,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at,
        }
        for u in users
    ]



#Update User Role
@app.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_role(["Admin"])(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = role
    db.commit()
    return {"message": "User role updated"}


#Delete User
@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_role(["Admin"])(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted"}

#user update model
# class UserUpdate(BaseModel):
#     name: str
#     email: str
#     role: str

class UserUpdate(BaseModel):
    first_name: str
    middle_name: str | None = None
    last_name: str
    email: str
    role: str


#Update User
@app.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_role(["Admin"])(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.first_name = user_data.first_name
    user.middle_name = user_data.middle_name
    user.last_name = user_data.last_name
    user.email = user_data.email
    user.role = user_data.role

    db.commit()
    db.refresh(user)

    return {"message": "User updated successfully"}


#change password model
class PasswordChange(BaseModel):
    old_password: str | None = None
    new_password: str

#change password route
@app.put("/users/{user_id}/password")
async def change_password(
    user_id: int,
    data: PasswordChange,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Admin can reset passwords without old password
    if current_user.role != "Admin":
        if not verify_password(data.old_password, user.password):
            raise HTTPException(status_code=400, detail="Incorrect old password")

    # Hash new password
    user.password = hash_password(data.new_password)
    db.commit()

    return {"message": "Password updated successfully"}

#Update User Status
@app.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    status: UserStatusUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_role(["Admin"])(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    user.is_active = status.is_active
    db.commit()

    return {"message": "Status updated"}


# @app.get("/documents/preview/{doc_id}")
# async def preview_document(doc_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
#     document = db.query(Document).filter(Document.id == doc_id).first()
#     if not document:
#         raise HTTPException(status_code=404, detail="Document not found")

#     return FileResponse(
#         document.filepath,
#         media_type="application/pdf",
#         filename=document.filename
        
#         )

@app.get("/documents/preview/{doc_id}")
async def preview_document(
    doc_id: int,
    source: str = "LIST",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Viewer → Public only
    if current_user.role == "Viewer" and document.document_type != "Public":
        raise HTTPException(status_code=403, detail="Access denied")

    # Faculty & Staff → no Confidential
    if document.document_type == "Confidential" and current_user.role in ["Faculty", "Staff"]:
        raise HTTPException(status_code=403, detail="Access denied")

  # ✅ LOG VIEW
    log = DocumentLog(
        document_id=doc_id,
        user_email=current_user.email,
        action="VIEW",
        source=source.upper()
    )
    db.add(log)
    db.commit()

    return FileResponse(
        path=document.filepath,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline"},
    )


from fastapi import Query

@app.get("/documents/download/{doc_id}")
async def download_document(
    doc_id: int,
    token: str = Query(None),   # 👈 accept token from query
    db: Session = Depends(get_db)
):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # 🔐 RBAC
    if user.role == "Viewer" and document.document_type != "Public":
        raise HTTPException(status_code=403, detail="You are not allowed to download this file")

    if document.document_type == "Confidential" and user.role in ["Faculty", "Staff"]:
        raise HTTPException(status_code=403, detail="You are not allowed to download this file")

    # ✅ LOG DOWNLOAD
    log = DocumentLog(
        document_id=document.id,
        user_email=user.email,
        action="DOWNLOAD",
        source="PREVIEW"
    )
    db.add(log)
    db.commit()

    return FileResponse(
        path=document.filepath,
        filename=document.filename,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{document.filename}"'
        }
    )



@app.get("/documents/details/{doc_id}")
async def document_details(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Viewer → Public only
    if current_user.role == "Viewer" and doc.document_type != "Public":
        raise HTTPException(status_code=403, detail="Access denied")

    # Faculty & Staff → no Confidential
    if doc.document_type == "Confidential" and current_user.role in ["Faculty", "Staff"]:
        raise HTTPException(status_code=403, detail="Access denied")

      # ✅ LOG DETAILS VIEW
    log = DocumentLog(
        document_id=doc.id,
        user_email=current_user.email,
        action="VIEW",
        source="LIST"
    )
    db.add(log)
    db.commit()

    return {
        "filename": doc.filename,
        "description": doc.description,
        "category": doc.category,
        "document_type": doc.document_type,
        "uploaded_by": doc.uploaded_by,
        "uploaded_at": doc.uploaded_at,
    }


# @app.get("/documents/text/{doc_id}")
# async def get_document_text(doc_id: int, db: Session = Depends(get_db)):
#     doc = db.query(Document).filter(Document.id == doc_id).first()
#     if not doc:
#         raise HTTPException(status_code=404, detail="Document not found")

#     text = extract_text_from_file(doc.filepath)
#     return {"text": text}

@app.get("/positions")
async def get_positions(
    db: Session = Depends(get_db)
):
    return db.query(Position).order_by(Position.name).all()


@app.get("/offices")
async def get_offices(db: Session = Depends(get_db)):
    offices = db.query(Office).order_by(Office.name).all()

    return [
        {
            "id": o.id,
            "office_code": o.office_code,
            "name": o.name
        }
        for o in offices
    ]

@app.get("/admin/positions")
def list_positions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_role(["Admin"])(current_user)
    return db.query(Position).order_by(Position.name).all()


@app.post("/admin/positions")
def create_position(
    name: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_role(["Admin"])(current_user)

    if db.query(Position).filter(Position.name == name).first():
        raise HTTPException(400, "Position already exists")

    pos = Position(name=name)
    db.add(pos)
    db.commit()
    return {"message": "Position created"}


@app.delete("/admin/positions/{id}")
def delete_position(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_role(["Admin"])(current_user)

    pos = db.query(Position).get(id)
    if not pos:
        raise HTTPException(404, "Position not found")

    db.delete(pos)
    db.commit()
    return {"message": "Position deleted"}

@app.get("/admin/offices")
def list_offices(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_role(["Admin"])(current_user)
    return db.query(Office).order_by(Office.name).all()


@app.post("/admin/offices")
def create_office(
    office_code: str = Form(...),
    name: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_role(["Admin"])(current_user)

    if db.query(Office).filter(
        (Office.office_code == office_code) | (Office.name == name)
    ).first():
        raise HTTPException(400, "Office already exists")

    office = Office(office_code=office_code.upper(), name=name)
    db.add(office)
    db.commit()
    return {"message": "Office created"}


@app.delete("/admin/offices/{id}")
def delete_office(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_role(["Admin"])(current_user)

    office = db.query(Office).get(id)
    if not office:
        raise HTTPException(404, "Office not found")

    db.delete(office)
    db.commit()
    return {"message": "Office deleted"}

@app.get("/documents/my-uploads")
async def my_uploads(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Only Admin & Uploader can access
    if current_user.role not in ["Admin", "Uploader"]:
        raise HTTPException(status_code=403, detail="Access denied")

    docs = (
        db.query(Document)
        .filter(Document.uploaded_by == current_user.email)
        .order_by(Document.uploaded_at.desc())
        .all()
    )

    return [
        {
            "id": d.id,
            "filename": d.filename,
            "description": d.description,
            "category": d.category,
            "document_type": d.document_type,
            "uploaded_by": d.uploaded_by,
            "uploaded_at": d.uploaded_at.strftime("%Y-%m-%d %H:%M"),
        }
        for d in docs
    ]




# @app.get("/documents/semantic-search")
# async def semantic_search(
#     query: str,
#     year_from: int | None = None,   # ✅ NEW
#     year_to: int | None = None,     # ✅ NEW
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     if not query.strip():
#         return []

    # # Encode query
    # query_embedding = embedder.encode(query).reshape(1, -1)

    # # -----------------------------
    # # 🔎 BASE QUERY (WITH YEAR FILTER)
    # # -----------------------------
    # doc_query = db.query(Document).filter(Document.embedding != None)

    # # RBAC filtering
    # if current_user.role == "Viewer":
    #     doc_query = doc_query.filter(Document.document_type == "Public")
    # elif current_user.role in ["Faculty", "Staff"]:
    #     doc_query = doc_query.filter(Document.document_type != "Confidential")

    # # ✅ YEAR FILTER (APPLIED FIRST)
    # if year_from:
    #     doc_query = doc_query.filter(Document.year_approved >= year_from)

    # if year_to:
    #     doc_query = doc_query.filter(Document.year_approved <= year_to)

    # docs = doc_query.all()

    # if not docs:
    #     return []

    # -----------------------------
    # 🧠 SEMANTIC SCORING
    # # -----------------------------
    # results = []

    # for doc in docs:
    #     doc_embedding = np.array(doc.embedding).reshape(1, -1)
    #     score = cosine_similarity(query_embedding, doc_embedding)[0][0]

    #     if score > 0.35:  # similarity threshold
    #         results.append({
    #             "id": doc.id,
    #             "filename": doc.filename,
    #             "description": doc.description,
    #             "category": doc.category,
    #             "year_approved": doc.year_approved,   # ✅ INCLUDED
    #             "document_type": doc.document_type,
    #             "uploaded_by": doc.uploaded_by,
    #             "uploaded_at": doc.uploaded_at.strftime("%Y-%m-%d %H:%M"),
    #             "score": round(float(score), 3)
    #         })

    # # Sort by relevance
    # results.sort(key=lambda x: x["score"], reverse=True)

    # return results


@app.get("/documents/semantic-search")
async def semantic_search(
    query: str,
    year_from: int | None = None,
    year_to: int | None = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if not query.strip():
        return []

    query_embedding = embedder.encode(query).reshape(1, -1)

    # Base query
    doc_query = db.query(Document).filter(Document.embedding != None)

    # RBAC
    if current_user.role == "Viewer":
        doc_query = doc_query.filter(Document.document_type == "Public")
    elif current_user.role in ["Faculty", "Staff"]:
        doc_query = doc_query.filter(Document.document_type != "Confidential")

    # Year filter
    if year_from is not None:
        doc_query = doc_query.filter(Document.year_approved >= year_from)

    if year_to is not None:
        doc_query = doc_query.filter(Document.year_approved <= year_to)

    docs = doc_query.all()
    results = []

    for doc in docs:
        if not doc.embedding:
            continue  # ⛑ safety

        doc_embedding = np.array(doc.embedding).reshape(1, -1)
        score = cosine_similarity(query_embedding, doc_embedding)[0][0]

        if score >= 0.35:
            results.append({
                "id": doc.id,
                "filename": doc.filename,
                "description": doc.description,
                "category": doc.category,
                "year_approved": doc.year_approved,
                "document_type": doc.document_type,
                "uploaded_by": doc.uploaded_by,
                "uploaded_at": doc.uploaded_at.strftime("%Y-%m-%d %H:%M"),
                "score": round(float(score), 3)
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


from nlp_utils import get_relevant_sentences

@app.get("/documents/highlights/{doc_id}")
async def document_highlights(
    doc_id: int,
    query: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # RBAC check
    if current_user.role == "Viewer" and doc.document_type != "Public":
        raise HTTPException(status_code=403, detail="Access denied")

    text = extract_text_from_file(doc.filepath)

    highlights = get_relevant_sentences(
        text=text,
        query=query,
        embedder=embedder,
        top_k=5
    )

    return highlights




@app.put("/admin/offices/{id}")
def update_office(
    id: int,
    office_code: str = Form(...),
    name: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_role(["Admin"])(current_user)

    office = db.query(Office).filter(Office.id == id).first()
    if not office:
        raise HTTPException(status_code=404, detail="Office not found")

    # prevent duplicates
    if db.query(Office).filter(
        Office.id != id,
        ((Office.office_code == office_code) | (Office.name == name))
    ).first():
        raise HTTPException(status_code=400, detail="Office already exists")

    office.office_code = office_code.upper()
    office.name = name
    db.commit()

    return {"message": "Office updated successfully"}

@app.put("/admin/positions/{id}")
def update_position(
    id: int,
    name: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_role(["Admin"])(current_user)

    position = db.query(Position).filter(Position.id == id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")

    # Prevent duplicates
    if db.query(Position).filter(
        Position.id != id,
        Position.name == name
    ).first():
        raise HTTPException(status_code=400, detail="Position already exists")

    position.name = name
    db.commit()

    return {"message": "Position updated successfully"}


@app.get("/admin/document-logs")
async def get_document_logs(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_role(["Admin"])(current_user)

    logs = (
        db.query(DocumentLog, Document.filename)
        .join(Document, Document.id == DocumentLog.document_id)
        .order_by(DocumentLog.accessed_at.desc())
        .all()
    )

 # logs is a list of tuples: (DocumentLog, filename)
    result = []

    for log_entry, filename in logs:
        result.append({
            "id": log_entry.id,
            "document_id": log_entry.document_id,
            "document": filename,
            "user": log_entry.user_email,
            "action": log_entry.action,
            "source": log_entry.source,
            "accessed_at": log_entry.accessed_at.strftime("%Y-%m-%d %H:%M:%S"),
        })

    return result




class DownloadRequestCreate(BaseModel):
    reason: str | None = None


@app.post("/documents/{doc_id}/request-download")
async def request_download(
    doc_id: int,
    data: DownloadRequestCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only Viewer can request
    if current_user.role != "Viewer":
        raise HTTPException(403, "Only viewers can request downloads")

    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")

    req = DownloadRequest(
        document_id=doc.id,
        document_name=doc.filename,
        requester_email=current_user.email,
        reason=data.reason
    )

    db.add(req)
    db.commit()

    return {"message": "Download request submitted"}


@app.get("/admin/download-requests")
async def list_download_requests(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_role(["Admin"])(current_user)

    requests = db.query(DownloadRequest).order_by(
        DownloadRequest.requested_at.desc()
    ).all()

    return [
        {
            "id": r.id,
            "document_id": r.document_id,
            "document_name": r.document_name,
            "requester_email": r.requester_email,
            "reason": r.reason,
            "status": r.status,
            "requested_at": r.requested_at.strftime("%Y-%m-%d %H:%M")
        }
        for r in requests
    ]


@app.put("/admin/download-requests/{request_id}")
async def update_download_request(
    request_id: int,
    status: str = Query(..., regex="^(APPROVED|REJECTED)$"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_role(["Admin"])(current_user)

    req = db.query(DownloadRequest).filter(
        DownloadRequest.id == request_id
    ).first()

    if not req:
        raise HTTPException(404, "Request not found")

    req.status = status
    req.reviewed_at = datetime.utcnow()
    req.reviewed_by = current_user.email

    db.commit()

    return {"message": f"Request {status.lower()} successfully"}



@app.get("/documents/my-download-requests")
async def my_download_requests(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    requests = (
        db.query(DownloadRequest)
        .filter(DownloadRequest.requester_email == current_user.email)
        .order_by(DownloadRequest.requested_at.desc())
        .all()
    )

    return [
        {
            "id": r.id,
            "document_id": r.document_id,
            "document_name": r.document_name,
            "reason": r.reason,
            "status": r.status,
            "requested_at": r.requested_at.strftime("%Y-%m-%d %H:%M")
        }
        for r in requests
    ]
