# book.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from db import get_db

routerbook = APIRouter()

# Pydantic模型
class BookBase(BaseModel):
    isbn: str
    book_name: str
    authors: str
    category: str
    inventory: int
    price: float
    store_id: int
    image_url: Optional[str] = None 

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    book_name: Optional[str] = None
    authors: Optional[str] = None
    category: Optional[str] = None
    inventory: Optional[int] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
class Book(BookBase):
    class Config:
        from_attributes = True

# API路由
@routerbook.post("/", response_model=Book)
async def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """创建新书籍"""
    try:
        # 插入新书籍的 SQL 语句
        sql = text("""
            INSERT INTO books (isbn, book_name, authors, category, inventory, price, store_id,image_url)
            VALUES (:isbn, :book_name, :authors, :category, :inventory, :price, :store_id,:image_url)
            RETURNING *
        """)
        
        # 将 BookCreate 数据转换为字典并执行 SQL
        result = db.execute(sql, book.dict())
        db.commit()
        # 返回插入的书籍数据
        return result.fetchone()
    
    except Exception as e:
        # 发生异常时回滚事务
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



@routerbook.get("/search", response_model=List[Book])
async def search_books(q: Optional[str] = None, category: Optional[str] = None, db: Session = Depends(get_db)):
    """搜索书籍"""
    try:
        if q and q.startswith('@'): # 精确搜索
            search_term = q[1:]
            if category:
                result = db.execute(
                    text("""
                        SELECT * FROM books 
                        WHERE (isbn = :term 
                        OR book_name = :term 
                        OR authors = :term)
                        AND category = :category
                    """),
                    {"term": search_term, "category": category}
                ).fetchall()
            else:
                result = db.execute(
                    text("""
                        SELECT * FROM books 
                        WHERE isbn = :term 
                        OR book_name = :term 
                        OR authors = :term
                    """),
                    {"term": search_term}
                ).fetchall()
        
        elif q: # 模糊搜索
            if category:
                result = db.execute(
                    text("""
                        SELECT * FROM books 
                        WHERE (book_name ILIKE :pattern 
                        OR authors ILIKE :pattern)
                        AND category = :category
                    """),
                    {"pattern": f"%{q}%", "category": category}
                ).fetchall()
            else:
                result = db.execute(
                    text("""
                        SELECT * FROM books 
                        WHERE book_name ILIKE :pattern 
                        OR authors ILIKE :pattern
                    """),
                    {"pattern": f"%{q}%"}
                ).fetchall()
        
        elif category: # 只按分类筛选
            result = db.execute(
                text("SELECT * FROM books WHERE category = :category"),
                {"category": category}
            ).fetchall()
        
        else: # 获取所有书籍
            result = db.execute(text("SELECT * FROM books")).fetchall()

        # 处理返回结果
        books = []
        for row in result:
            book_dict = {
                "isbn": row.isbn,
                "book_name": row.book_name,
                "authors": row.authors,
                "category": row.category,
                "inventory": row.inventory,
                "price": float(row.price),  # 将Decimal转换为float
                "store_id": row.store_id,
                "image_url": row.image_url  # 新增的图片URL字段
            }
            books.append(Book(**book_dict))
        return books

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@routerbook.get("/{isbn}", response_model=Book)
async def get_book(isbn: str, db: Session = Depends(get_db)):
    """获取单本书籍详情"""
    sql = text("SELECT * FROM books WHERE isbn = :isbn")
    result = db.execute(sql, {"isbn": isbn}).fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Book not found")
    return result

@routerbook.put("/{isbn}", response_model=Book)
async def update_book(isbn: str, book_update: BookUpdate, db: Session = Depends(get_db)):
    """更新书籍信息"""
    try:
        update_data = book_update.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # 构建UPDATE语句
        set_clause = ", ".join(f"{k} = :{k}" for k in update_data.keys())
        sql = text(f"""
            UPDATE books 
            SET {set_clause}
            WHERE isbn = :isbn
            RETURNING *
        """)
        
        # 添加isbn到参数中
        update_data["isbn"] = isbn
        result = db.execute(sql, update_data).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Book not found")
        
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@routerbook.delete("/{isbn}")
async def delete_book(isbn: str, db: Session = Depends(get_db)):
    """删除书籍"""
    try:
        sql = text("DELETE FROM books WHERE isbn = :isbn RETURNING isbn")
        result = db.execute(sql, {"isbn": isbn}).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Book not found")
        db.commit()
        return {"message": "Book deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@routerbook.get("/category/{category}")
async def get_books_by_category(category: str, db: Session = Depends(get_db)):
    """按分类获取书籍"""
    sql = text("SELECT * FROM books WHERE category = :category")
    result = db.execute(sql, {"category": category})
    # 处理返回结果
    books = []
    for row in result:
            book_dict = {
                "isbn": row.isbn,
                "book_name": row.book_name,
                "authors": row.authors,
                "category": row.category,
                "inventory": row.inventory,
                "price": float(row.price),  # 将Decimal转换为float
                "store_id": row.store_id,
                "image_url": row.image_url  # 新增的图片URL字段
            }
            books.append(Book(**book_dict))
    return books
@routerbook.get("/store/{store_id}")
async def get_books_by_store(store_id: int, db: Session = Depends(get_db)):
    """获取店铺的所有书籍"""
    sql = text("SELECT * FROM books WHERE store_id = :store_id")
    result = db.execute(sql, {"store_id": store_id})
    # 处理返回结果
    books = []
    for row in result:
            book_dict = {
                "isbn": row.isbn,
                "book_name": row.book_name,
                "authors": row.authors,
                "category": row.category,
                "inventory": row.inventory,
                "price": float(row.price),  # 将Decimal转换为float
                "store_id": row.store_id,
                "image_url": row.image_url  # 新增的图片URL字段
            }
            books.append(Book(**book_dict))
    return books

@routerbook.get("/inventory/low")
async def get_low_inventory_books(threshold: int = 0, db: Session = Depends(get_db)):
    """获取库存低的书籍"""
    sql = text("SELECT * FROM books WHERE inventory <= :threshold")
    result = db.execute(sql, {"threshold": threshold})
    # 处理返回结果
    books = []
    for row in result:
            book_dict = {
                "isbn": row.isbn,
                "book_name": row.book_name,
                "authors": row.authors,
                "category": row.category,
                "inventory": row.inventory,
                "price": float(row.price),  # 将Decimal转换为float
                "store_id": row.store_id,
                "image_url": row.image_url  # 新增的图片URL字段
            }
            books.append(Book(**book_dict))
    return books
# 在 books.py 中添加新接口
# books.py
# 确保有对应的路由处理函数
@routerbook.get("/")  # 或 "/search"
async def get_all_books(db: Session = Depends(get_db)):
    """获取所有图书"""
    try:
        result = db.execute(text("SELECT * FROM books")).fetchall()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@routerbook.get("/late/")
async def get_all_books(db: Session = Depends(get_db)):
    """获取所有图书"""
    try:
        result = db.execute(text("SELECT * FROM books")).fetchall()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))