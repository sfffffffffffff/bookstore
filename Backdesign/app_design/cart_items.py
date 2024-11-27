# cart_items.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from decimal import Decimal
from db import get_db
from app_design.dependencies.deps import get_current_user

routercart = APIRouter()

# Pydantic 模型
class CartItemBase(BaseModel):
    book_isbn: str
    quantity: int

    class Config:
        from_attributes = True

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class BookInfo(BaseModel):
    isbn: str
    book_name: str
    authors: str
    price: float
    inventory: int
    store_id: int
    store_name: str

    class Config:
        from_attributes = True

class CartItemResponse(BaseModel):
    cart_item_id: int
    user_id: int
    book_isbn: str
    quantity: int
    book_info: BookInfo

    class Config:
        from_attributes = True

class CheckoutResponse(BaseModel):
    message: str
    order_ids: List[int]

class MessageResponse(BaseModel):
    message: str

# API路由
@routercart.post("/", response_model=CartItemResponse)
async def add_to_cart(
    item: CartItemCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加商品到购物车"""
    try:
        # 检查书籍是否存在且有足够库存
        book = db.execute(text("""
            SELECT b.*, p.name as store_name 
            FROM books b
            JOIN participants p ON b.store_id = p.id
            WHERE b.isbn = :isbn AND b.inventory >= :quantity
        """), {
            "isbn": item.book_isbn,
            "quantity": item.quantity
        }).fetchone()
        
        if not book:
            raise HTTPException(status_code=404, detail="Book not found or insufficient inventory")

        # 检查是否已在购物车中
        existing = db.execute(text("""
            SELECT * FROM cart_items 
            WHERE user_id = :user_id AND book_isbn = :book_isbn
        """), {
            "user_id": current_user[0],
            "book_isbn": item.book_isbn
        }).fetchone()

        if existing:
            cart_item = db.execute(text("""
                UPDATE cart_items 
                SET quantity = quantity + :quantity 
                WHERE cart_item_id = :cart_item_id
                RETURNING *
            """), {
                "quantity": item.quantity,
                "cart_item_id": existing.cart_item_id
            }).fetchone()
        else:
            cart_item = db.execute(text("""
                INSERT INTO cart_items (user_id, book_isbn, quantity)
                VALUES (:user_id, :book_isbn, :quantity)
                RETURNING *
            """), {
                "user_id": current_user[0],
                "book_isbn": item.book_isbn,
                "quantity": item.quantity
            }).fetchone()

        db.commit()

        return CartItemResponse(
            cart_item_id=cart_item.cart_item_id,
            user_id=cart_item.user_id,
            book_isbn=cart_item.book_isbn,
            quantity=cart_item.quantity,
            book_info=BookInfo(
                isbn=book.isbn,
                book_name=book.book_name,
                authors=book.authors,
                price=float(book.price),
                inventory=book.inventory,
                store_id=book.store_id,
                store_name=book.store_name
            )
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@routercart.get("/", response_model=List[CartItemResponse])
async def get_cart_items(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取购物车所有商品"""
    try:
        results = db.execute(text("""
            SELECT 
                ci.*,
                b.book_name,
                b.authors,
                b.price,
                b.inventory,
                b.store_id,
                p.name as store_name
            FROM cart_items ci
            JOIN books b ON ci.book_isbn = b.isbn
            JOIN participants p ON b.store_id = p.id
            WHERE ci.user_id = :user_id
        """), {
            "user_id": current_user[0]
        }).fetchall()

        return [
            CartItemResponse(
                cart_item_id=row.cart_item_id,
                user_id=row.user_id,
                book_isbn=row.book_isbn,
                quantity=row.quantity,
                book_info=BookInfo(
                    isbn=row.book_isbn,
                    book_name=row.book_name,
                    authors=row.authors,
                    price=float(row.price),
                    inventory=row.inventory,
                    store_id=row.store_id,
                    store_name=row.store_name
                )
            )
            for row in results
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@routercart.put("/{cart_item_id}", response_model=CartItemResponse)
async def update_cart_item(
    cart_item_id: int,
    item_update: CartItemUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新购物车商品数量"""
    try:
        # 验证并更新
        item = db.execute(text("""
            SELECT ci.*, b.inventory, b.book_name, b.authors, b.price, b.store_id, p.name as store_name
            FROM cart_items ci
            JOIN books b ON ci.book_isbn = b.isbn
            JOIN participants p ON b.store_id = p.id
            WHERE ci.cart_item_id = :cart_item_id AND ci.user_id = :user_id
        """), {
            "cart_item_id": cart_item_id,
            "user_id": current_user[0]
        }).fetchone()
        
        if not item:
            raise HTTPException(status_code=404, detail="Cart item not found")
            
        if item_update.quantity > item.inventory:
            raise HTTPException(status_code=400, detail="Insufficient inventory")
            
        updated_item = db.execute(text("""
            UPDATE cart_items 
            SET quantity = :quantity 
            WHERE cart_item_id = :cart_item_id
            RETURNING *
        """), {
            "quantity": item_update.quantity,
            "cart_item_id": cart_item_id
        }).fetchone()
        
        db.commit()
        
        return CartItemResponse(
            cart_item_id=updated_item.cart_item_id,
            user_id=updated_item.user_id,
            book_isbn=updated_item.book_isbn,
            quantity=updated_item.quantity,
            book_info=BookInfo(
                isbn=item.book_isbn,
                book_name=item.book_name,
                authors=item.authors,
                price=float(item.price),
                inventory=item.inventory,
                store_id=item.store_id,
                store_name=item.store_name
            )
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@routercart.delete("/{cart_item_id}", response_model=MessageResponse)
async def remove_from_cart(
    cart_item_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """从购物车移除商品"""
    try:
        result = db.execute(text("""
            DELETE FROM cart_items 
            WHERE cart_item_id = :cart_item_id AND user_id = :user_id
            RETURNING cart_item_id
        """), {
            "cart_item_id": cart_item_id,
            "user_id": current_user[0]
        }).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Cart item not found")
            
        db.commit()
        return MessageResponse(message="Item removed from cart successfully")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@routercart.delete("/", response_model=MessageResponse)
async def clear_cart(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """清空购物车"""
    try:
        db.execute(text("""
            DELETE FROM cart_items 
            WHERE user_id = :user_id
        """), {
            "user_id": current_user[0]
        })
        db.commit()
        return MessageResponse(message="Cart cleared successfully")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@routercart.post("/checkout", response_model=CheckoutResponse)
async def checkout_cart(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """购物车结算，创建订单"""
    try:
        # 获取购物车商品
        cart_items = db.execute(text("""
            SELECT ci.*, b.store_id, b.price
            FROM cart_items ci
            JOIN books b ON ci.book_isbn = b.isbn
            WHERE ci.user_id = :user_id
        """), {
            "user_id": current_user.id
        }).fetchall()
        
        if not cart_items:
            raise HTTPException(status_code=400, detail="购物车是空的")

        # 按店铺分组
        store_items = {}
        for item in cart_items:
            if item.store_id not in store_items:
                store_items[item.store_id] = []
            store_items[item.store_id].append(item)

        # 创建订单
        order_ids = []
        for store_id, items in store_items.items():
            total_price = sum(float(item.price) * item.quantity for item in items)
            
            # 创建订单，状态为待付款
            order = db.execute(text("""
                INSERT INTO orders (user_id, store_id, total_price, status, order_date)
                VALUES (:user_id, :store_id, :total_price, 'pending', CURRENT_DATE)
                RETURNING order_id
            """), {
                "user_id": current_user.id,
                "store_id": store_id,
                "total_price": total_price
            }).fetchone()

            for item in items:
                # 创建订单详情
                db.execute(text("""
                    INSERT INTO order_details 
                    (order_id, book_isbn, quantity, unit_price)
                    VALUES (:order_id, :book_isbn, :quantity, :unit_price)
                """), {
                    "order_id": order.order_id,
                    "book_isbn": item.book_isbn,
                    "quantity": item.quantity,
                    "unit_price": float(item.price)
                })

            order_ids.append(order.order_id)

        # 清空购物车
        db.execute(text("DELETE FROM cart_items WHERE user_id = :user_id"), {
            "user_id": current_user.id
        })
        
        db.commit()
        return CheckoutResponse(
            message="结算成功",
            order_ids=order_ids
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))