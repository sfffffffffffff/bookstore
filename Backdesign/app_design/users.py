# user.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import date
from db import get_db
from app_design.dependencies.deps import oauth2_scheme,get_current_user
from app_design.dependencies.deps import get_current_admin
from core.security import create_token,verify_token

routeruser = APIRouter()

# 密码加密配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserBase(BaseModel):
    name: str
    email: EmailStr
    address: str
    type: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    address: Optional[str] = None

class User(UserBase):
    id: int
    class Config:
        from_attributes = True
# API路由
@routeruser.get("/me", response_model=User)
async def get_current_user_info(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """获取当前用户信息的API endpoint"""
    user = await get_current_user(token, db)
    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "type": user.type,
        "address": user.address,
    }
    return user_data
@routeruser.put("/me", response_model=User)  
async def update_user(  
    user_update: UserUpdate,  
    db: Session = Depends(get_db),  
    token: str = Depends(oauth2_scheme)  
):  
    """更新当前用户信息"""  
    try:  
        # 获取当前用户信息  
        user = await get_current_user(token, db)  
        user_data = {  
            "id": user.id,  
            "name": user.name,  
            "email": user.email,  
            "type": user.type,  
            "address": user.address,  
        }  # 从 token 中验证并提取用户 ID  
        
        if user_data["id"] is None:  
            raise HTTPException(  
                status_code=status.HTTP_401_UNAUTHORIZED,  
                detail="Invalid token or expired",  
            )  
        
        # 将更新的数据转换为序列（元组、列表）  
        update_data = user_update.dict(exclude_unset=True)  
        if 'password' in update_data:  
            update_data['password'] = pwd_context.hash(update_data['password'])  
            
        if not update_data:  
            raise HTTPException(status_code=400, detail="No fields to update")  

        # 检查邮箱是否已存在  
        if 'email' in update_data :  
            check_sql = text("SELECT id FROM participants WHERE email = :email AND id != :id")  
            existing = db.execute(check_sql, {  
                "email": update_data['email'],  
                "id": user_data["id"]  # Use user_data["id"] instead of user_data.id  
            }).fetchone()  
            if existing and 'email'!=user_data["email"]:  
                raise HTTPException(status_code=400, detail="Email already registered")  

        # 如果要更新name，检查是否已存在  
        if 'name' in update_data:  
            check_sql = text("SELECT id FROM participants WHERE name = :name AND id != :id")  
            existing = db.execute(check_sql, {  
                "name": update_data['name'],  
                "id": user_data["id"]  # Use user_data["id"] instead of user_data.id  
            }).fetchone()  
            if existing:  
                raise HTTPException(status_code=400, detail="Username already taken")  

        # 构建UPDATE语句  
        set_clause = ", ".join(f"{k} = :{k}" for k in update_data.keys())  
        sql = text(f"""  
            UPDATE participants   
            SET {set_clause}  
            WHERE id = :id  
            RETURNING id, name, email, type, address  
        """)  
        
        # 添加user_id到参数中  
        update_data["id"] = user_data["id"]  
        result = db.execute(sql, update_data).fetchone()  
        
        if not result:  
            raise HTTPException(status_code=404, detail="User not found")  
        
        db.commit()  
        
        # 返回更新后的用户信息，保持格式一致  
        return {  
            "id": result[0],  # Access by index since result is likely a RowProxy  
            "name": result[1],  
            "email": result[2],  
            "type": result[3],  
            "address": result[4],  
        }  
    except Exception as e:  
        db.rollback()  
        raise HTTPException(status_code=500, detail=str(e))
@routeruser.delete("/me")
async def delete_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """删除当前用户账号"""
    try:
        user = await get_current_user(token, db)
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "type": user.type,
            "address": user.address,
        } 
        if user_data["id"] is None:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired",
         )
        sql = text("DELETE FROM participants WHERE id = :id RETURNING id")
        result = db.execute(sql, {"id":user_data["id"]}).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        
        db.commit()
        return {"message": "User account deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@routeruser.get("/stores")
async def get_all_stores(db: Session = Depends(get_db)):
    """获取所有商家用户"""
    sql = text("SELECT * FROM participants WHERE type = 'store'")
    result = db.execute(sql)
    stores = []
    for user in result:
            store_list = {
                "id": user.id,
                "name": user.name,
               "email": user.email,
               "type": user.type,
               "address": user.address,
            }
            stores.append(UserUpdate(**store_list))
    return stores
    

@routeruser.get("/{user_id}", response_model=User)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取指定用户信息（管理员用）"""
    try:
        sql = text("SELECT * FROM participants WHERE id = :id")
        result = db.execute(sql, {"id": user_id}).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@routeruser.get("/")
async def get_all_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取所有用户（管理员用）"""
    try:
        # 使用参数化查询
        sql = text("""
            SELECT id, name, email, type, address 
            FROM participants 
            ORDER BY id  -- 添加排序确保结果一致
            OFFSET :skip LIMIT :limit
        """)
        
        result = db.execute(sql, {"skip": skip, "limit": limit})
        users_data = []
        
        for row in result:
            user_dict = {
                "id": row.id,  # 确保返回id字段
                "name": row.name,
                "email": row.email,
                "type": row.type,
                "address": row.address
            }
            users_data.append(user_dict)
        
        return users_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
# 管理员routes
@routeruser.post("/admin/create", response_model=User)
async def create_admin(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """创建新管理员（仅限管理员）"""
    try:
        # 检查email是否已存在
        check_sql = text("SELECT id FROM participants WHERE email = :email")
        if db.execute(check_sql, {"email": user.email}).fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")

        # 检查昵称是否已存在
        check_sql = text("SELECT id FROM participants WHERE name = :name")
        if db.execute(check_sql, {"name": user.name}).fetchone():
            raise HTTPException(status_code=400, detail="Username already taken")

        # 创建新管理员
        sql = text("""
            INSERT INTO participants (name, email, password, address, type)
            VALUES (:name, :email, :password, :address, 'administrator')
            RETURNING *
        """)
        
        hashed_password = pwd_context.hash(user.password)
        result = db.execute(sql, {
            "name": user.name,
            "email": user.email,
            "password": hashed_password,
            "address": user.address
        }).fetchone()
        
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
# 管理员更新用户
@routeruser.delete("/{user_id}")
async def delete_user_by_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """管理员删除用户"""
    try:
        # 首先检查用户是否存在
        check_sql = text("SELECT id FROM participants WHERE id = :id")
        existing_user = db.execute(check_sql, {"id": user_id}).first()
        
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 执行删除操作
        sql = text("DELETE FROM participants WHERE id = :id")
        result = db.execute(sql, {"id": user_id})
        
        if result.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=404, detail="User not found or already deleted")
        
        db.commit()
        return {"message": "User deleted successfully", "user_id": user_id}
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")
class UserUpdate2(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    type: Optional[str] = None
    password: Optional[str] = None
@routeruser.put("/{user_id}", response_model=User)
async def update_user_by_admin(
    user_id: int,
    user_update: UserUpdate2,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """管理员更新用户信息"""
    try:
        # 首先检查用户是否存在
        check_sql = text("SELECT * FROM participants WHERE id = :id")
        existing_user = db.execute(check_sql, {"id": user_id}).first()
        
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        # 获取更新数据
        update_data = {}
        
        # 检查并添加要更新的字段
        if user_update.name is not None:
            # 检查用户名是否重复
            check_sql = text("""
                SELECT id FROM participants 
                WHERE name = :name AND id != :id
            """)
            if db.execute(check_sql, {
                "name": user_update.name, 
                "id": user_id
            }).first():
                raise HTTPException(status_code=400, detail="Username already taken")
            update_data['name'] = user_update.name

        if user_update.address is not None:
            update_data['address'] = user_update.address

        if user_update.type is not None:
            # 验证用户类型
            valid_types = ['buyer', 'store', 'administrator']
            if user_update.type not in valid_types:
                raise HTTPException(status_code=400, detail="Invalid user type")
            update_data['type'] = user_update.type

        if user_update.password is not None and user_update.password.strip():
            # 对密码进行哈希处理
            update_data['password'] = pwd_context.hash(user_update.password)

        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields to update")

        # 构建更新语句
        set_clause = ", ".join(f"{k} = :{k}" for k in update_data.keys())
        sql = text(f"""
            UPDATE participants 
            SET {set_clause}
            WHERE id = :id
            RETURNING id, name, email, type, address
        """)
        
        # 添加user_id到更新数据中
        update_data['id'] = user_id
        result = db.execute(sql, update_data).first()
        
        if not result:
            db.rollback()
            raise HTTPException(status_code=404, detail="Update failed")
            
        db.commit()
        
        # 返回更新后的用户数据
        return {
            "id": result.id,
            "name": result.name,
            "email": result.email,
            "type": result.type,
            "address": result.address
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

# 管理员搜索用户
@routeruser.get("/search/")
async def search_users(
    query: str = "",
    type: str = "",
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """搜索用户"""
    try:
        sql = """
            SELECT * FROM participants
            WHERE 1=1
        """
        params = {}
        
        if query:
            sql += " AND (name ILIKE :query OR email ILIKE :query)"
            params['query'] = f"%{query}%"
            
        if type:
            sql += " AND type = :type"
            params['type'] = type
            
        sql += " LIMIT :limit OFFSET :skip"
        params.update({'limit': limit, 'skip': skip})
        
        result = db.execute(text(sql), params).fetchall()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@routeruser.post("/", response_model=User)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)  # 确保是管理员权限
):
    """创建新用户（仅限管理员）"""
    try:
        # 检查email是否已存在
        check_sql = text("SELECT id FROM participants WHERE email = :email")
        if db.execute(check_sql, {"email": user.email}).fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")

        # 检查昵称是否已存在
        check_sql = text("SELECT id FROM participants WHERE name = :name")
        if db.execute(check_sql, {"name": user.name}).fetchone():
            raise HTTPException(status_code=400, detail="Username already taken")

        # 创建新用户
        sql = text("""
            INSERT INTO participants (name, email, password, address, type)
            VALUES (:name, :email, :password, :address, :type)
            RETURNING id, name, email, type, address
        """)
        
        hashed_password = pwd_context.hash(user.password)
        result = db.execute(sql, {
            "name": user.name,
            "email": user.email,
            "password": hashed_password,
            "address": user.address,
            "type": user.type
        }).fetchone()
        
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))