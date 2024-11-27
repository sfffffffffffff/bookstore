# main_sqlmodel.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, Text, Enum, ForeignKey, Numeric, Date, text, inspect
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic import BaseModel, EmailStr, ConfigDict
from passlib.context import CryptContext
import bcrypt
import enum
from typing import AsyncGenerator, Optional
import logging
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
from typing import Union
from app_design.books import routerbook
from app_design.cart_items import routercart
from app_design.orders import routerbookorders
from app_design.users import routeruser 

from db import get_db
# 在 main_sqlmodel.py 中
from db import engine
from db import SessionLocal
from app_design.dependencies.deps import ACCESS_TOKEN_EXPIRE_MINUTES
from app_design.dependencies.deps import timedelta
from app_design.dependencies.deps import create_access_token
# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


Base = declarative_base()

# 加密配置
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)



# 用户类型枚举
class UserType(str, enum.Enum):
    buyer = "buyer"
    store = "store"
    administrator = "administrator"

# 订单状态枚举
class OrderStatus(str, enum.Enum):
    pending = "pending"
    shipped = "shipped"
    completed = "completed"

# 数据库模型
class CartItemModel(Base):
    __tablename__ = "cart_items"
    
    cart_item_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('participants.id', ondelete='CASCADE'))
    book_isbn = Column(String(20), ForeignKey('books.isbn', ondelete='CASCADE'))
    quantity = Column(Integer, nullable=False)

class OrderDetailModel(Base):
    __tablename__ = "order_details"

    order_detail_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.order_id', ondelete='CASCADE'))
    book_isbn = Column(String(20), ForeignKey('books.isbn', ondelete='CASCADE'))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)

class OrderModel(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('participants.id', ondelete='CASCADE'))
    store_id = Column(Integer, ForeignKey('participants.id', ondelete='CASCADE'))
    total_price = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), nullable=False)
    order_date = Column(Date, nullable=False)

class BookModel(Base):
    __tablename__ = "books"

    isbn = Column(String(20), primary_key=True)
    book_name = Column(String(255), nullable=False)
    authors = Column(String(255), nullable=False)
    category = Column(String(100))
    inventory = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    store_id = Column(Integer, ForeignKey('participants.id', ondelete='CASCADE'))
    image_url = Column(String(255)) 
    

class ParticipantModel(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)  # 添加unique=True确保昵称唯一
    password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    address = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)

# Pydantic 模型
class ParticipantBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class ParticipantCreate(ParticipantBase):
    name: str
    password: str
    email: EmailStr
    address: str
    type: UserType

class ParticipantUpdate(ParticipantBase):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    password: Optional[str] = None

class ParticipantResponse(ParticipantBase):
    id: int
    name: str
    email: EmailStr
    address: str
    type: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str

def hash_password(password: str) -> str:
    """安全的密码哈希函数"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

# 初始化管理员函数
def create_initial_admin():
    db = SessionLocal()
    try:
        # 检查是否已存在管理员
        admin = db.query(ParticipantModel).filter_by(type="administrator").first()
        if not admin:
            hashed_password = hash_password("admin123")
            admin = ParticipantModel(
                name="Admin",
                password=hashed_password,
                email="admin@bookstore.com",
                address="Admin Office",
                type="administrator"
            )
            db.add(admin)
            db.commit()
            logger.info("Initial admin created successfully")
        else:
            logger.info("Admin already exists")
    except Exception as e:
        logger.error(f"Error creating initial admin: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# 使用 lifespan
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    logger.info("Starting up...")
    try:
        # 检查表是否存在
        inspector = inspect(engine)
        if 'participants' not in inspector.get_table_names():
            # 只有在表不存在时才创建表和初始管理员
            Base.metadata.create_all(bind=engine)
            create_initial_admin()
            logger.info("Tables created and initialized")
        logger.info("Database ready")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    yield
    logger.info("Shutting down...")

# 创建 FastAPI 应用
app = FastAPI(
    title="Bookstore API",
    description="Backend API for the bookstore application",
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(routerbook, prefix="/book")
app.include_router(routeruser, prefix="/user")

app.include_router(routerbookorders, prefix="/bookorders")
app.include_router(routercart, prefix="/cart")


# API路由
@app.post("/participants/", response_model=ParticipantResponse)
async def create_participant(participant: ParticipantCreate, db: Session = Depends(get_db)):
    """
    创建新用户
    - 检查昵称和邮箱是否已被使用
    - 普通注册不允许创建管理员账号
    """
    try:
        # 检查昵称是否已被使用
        existing_name = db.query(ParticipantModel).filter_by(name=participant.name).first()
        if existing_name:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # 检查 email 是否已注册
        existing_email = db.query(ParticipantModel).filter_by(email=participant.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # 检查用户类型权限
        if participant.type == UserType.administrator:
            raise HTTPException(
                status_code=403, 
                detail="Cannot directly register as administrator"
            )
        
        # 创建新用户
        new_participant = ParticipantModel(
            name=participant.name,
            password=hash_password(participant.password),
            email=participant.email,
            address=participant.address,
            type=participant.type.value
        )
        
        db.add(new_participant)
        db.commit()
        db.refresh(new_participant)
        
        logger.info(f"New participant created: {new_participant.name}")
        return new_participant
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error creating participant: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred while creating the participant"
        )


@app.post("/login/", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """用户登录"""
    try:
        print(f"Login attempt for user: {form_data.username}")  # 日志

        # 通过昵称查找用户
        user = db.query(ParticipantModel).filter(
            ParticipantModel.name == form_data.username
        ).first()
        
        if not user:
            print(f"User not found: {form_data.username}")  # 日志
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 验证密码
        if not verify_password(form_data.password, user.password):
            print("Password verification failed")  # 日志
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查用户类型
        if form_data.scopes and user.type not in form_data.scopes:
            print(f"User type mismatch. Expected: {form_data.scopes}, Got: {user.type}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User type does not match",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 创建访问令牌
        access_token = create_access_token(data={"sub": str(user.id)})
        
        print(f"Login successful for user: {user.name}")  # 日志
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_type": user.type
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Login error: {str(e)}")  # 日志
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
# 配置 CORS 中间件
from fastapi.middleware.cors import CORSMiddleware

from fastapi.middleware.cors import CORSMiddleware

# main_sqlmodel.py
from fastapi.middleware.cors import CORSMiddleware

# main_sqlmodel.py

# 定义允许的源
origins = [
    "http://localhost:5173",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Methods",
        "Access-Control-Allow-Headers"
    ],
    expose_headers=["*"],
    max_age=3600,
)
#————————————————————————————————————————————————————————————————————
from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
import os
import shutil
import aiofiles
# 创建上传目录
UPLOAD_DIR = "uploads/books"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True) 
# 挂载静态文件目录
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 添加图片上传路由
@app.post("/upload/{isbn}")
async def upload_book_image(
    isbn: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="只能上传图片文件")

        # 验证文件大小
        MAX_SIZE = 2 * 1024 * 1024  # 2MB
        file_size = 0
        file_contents = bytearray()
        
        while chunk := await file.read(8192):
            file_size += len(chunk)
            if file_size > MAX_SIZE:
                raise HTTPException(status_code=400, detail="文件大小超过限制")
            file_contents.extend(chunk)

        # 验证文件扩展名
        file_ext = os.path.splitext(file.filename)[1].lower()
        allowed_ext = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        if file_ext not in allowed_ext:
            raise HTTPException(status_code=400, detail="不支持的文件格式")

        # 生成文件名和路径
        file_name = f"{isbn}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, file_name)

        # 保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_contents)

        # 更新数据库
        image_url = f"/uploads/books/{file_name}"
        db.execute(
            text("UPDATE books SET image_url = :url WHERE isbn = :isbn"),
            {"url": image_url, "isbn": isbn}
        )
        db.commit()

        return {"url": image_url}

    except HTTPException as he:
        raise he
    except Exception as e:
        if 'db' in locals():
            db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
#————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_sqlmodel:app", host="127.0.0.1", port=8000, reload=True)