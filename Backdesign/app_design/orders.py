from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from db import get_db
from app_design.dependencies.deps import get_current_user

routerbookorders = APIRouter()

# Pydantic 模型
class OrderDetailBase(BaseModel):
    book_isbn: str
    quantity: int
    unit_price: float

class OrderDetail(BaseModel):
    order_detail_id: int
    order_id: int
    book_isbn: str
    quantity: int
    unit_price: float
    book_name: str | None = None
    authors: str | None = None
    image_url: str | None = None

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    user_id: int
    store_id: int
    total_price: float
    status: str
    order_date: date

class OrderCreate(BaseModel):
    store_id: int
    items: List[OrderDetailBase]

class OrderUpdate(BaseModel):
    status: Optional[str] = None

class Order(BaseModel):
    order_id: int
    user_id: int
    store_id: int
    store_name: str | None = None
    total_price: float
    status: str
    order_date: date
    details: List[OrderDetail] = []

    class Config:
        from_attributes = True
@routerbookorders.get("/my-orders", response_model=List[Order])
async def get_my_orders(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        orders_result = db.execute(text("""
            SELECT * FROM orders 
            WHERE user_id = :user_id 
            ORDER BY order_date DESC
            OFFSET :skip LIMIT :limit
        """), {
            "user_id": current_user.id,
            "skip": skip,
            "limit": limit
        }).fetchall()

        orders = []
        for row in orders_result:
            # 直接使用属性访问
            order_data = {
    "order_id": row[0],  # Access by index
    "user_id": row[1],
    "store_id": row[2],
    "total_price": float(row[3]),
    "status": row[4],
    "order_date": row[5],
    "details": []
}


            details_result = db.execute(text("""
                SELECT od.*, b.book_name, b.authors 
                FROM order_details od
                LEFT JOIN books b ON od.book_isbn = b.isbn
                WHERE od.order_id = :order_id
            """), {"order_id": order_data["order_id"]}).fetchall()

            for detail in details_result:
               detail_data = {
    "order_detail_id": detail[0],  # Access by index
    "order_id": detail[1],
    "book_isbn": detail[2],
    "quantity": detail[3],
    "unit_price": float(detail[4]),
    "book_name": detail[5],
    "authors": detail[6]
    }

            order_data["details"].append(OrderDetail(**detail_data))

            orders.append(Order(**order_data))

        return orders

    except Exception as e:
        print(f"Error in get_my_orders: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@routerbookorders.post("/", response_model=Order)
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        total_price = Decimal('0.0')
        for item in order.items:
            book = db.execute(text("""
                SELECT price, inventory FROM books 
                WHERE isbn = :isbn AND store_id = :store_id
            """), {
                "isbn": item.book_isbn,
                "store_id": order.store_id
            }).fetchone()
            
            if not book:
                raise HTTPException(status_code=404, detail=f"Book {item.book_isbn} not found")
            
            if book.inventory < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient inventory for book {item.book_isbn}")
            
            total_price += Decimal(str(book.price)) * item.quantity

            # 更新库存
            db.execute(text("""
                UPDATE books 
                SET inventory = inventory - :quantity 
                WHERE isbn = :isbn
            """), {
                "quantity": item.quantity,
                "isbn": item.book_isbn
            })

        order_result = db.execute(text("""
            INSERT INTO orders (user_id, store_id, total_price, status, order_date)
            VALUES (:user_id, :store_id, :total_price, 'pending', CURRENT_DATE)
            RETURNING *
        """), {
            "user_id": current_user.id,
            "store_id": order.store_id,
            "total_price": total_price
        }).fetchone()

        order_data = Order(
            order_id=order_result.order_id,
            user_id=order_result.user_id,
            store_id=order_result.store_id,
            total_price=float(order_result.total_price),
            status=order_result.status,
            order_date=order_result.order_date,
            details=[]
        )

        for item in order.items:
            detail_result = db.execute(text("""
                INSERT INTO order_details (order_id, book_isbn, quantity, unit_price)
                VALUES (:order_id, :book_isbn, :quantity, :unit_price)
                RETURNING *
            """), {
                "order_id": order_data.order_id,
                "book_isbn": item.book_isbn,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price)
            }).fetchone()
            
            detail_data = OrderDetail(
                order_detail_id=detail_result.order_detail_id,
                order_id=detail_result.order_id,
                book_isbn=detail_result.book_isbn,
                quantity=detail_result.quantity,
                unit_price=float(detail_result.unit_price)
            )
            order_data.details.append(detail_data)

        db.commit()
        return order_data

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
@routerbookorders.get("/store-orders", response_model=List[Order])
async def get_store_orders(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        orders_result = db.execute(text("""
            SELECT o.*, p.name as buyer_name
            FROM orders o
            JOIN participants p ON o.user_id = p.id
            WHERE o.store_id = :user_id 
            ORDER BY order_date DESC
            OFFSET :skip LIMIT :limit
        """), {
            "user_id": current_user.id,
            "skip": skip,
            "limit": limit
        }).fetchall()

        orders = []
        for row in orders_result:
            order_data = Order(
                order_id=row.order_id,
                user_id=row.user_id,
                store_id=row.store_id,
                total_price=float(row.total_price),
                status=row.status,
                order_date=row.order_date,
                store_name=row.buyer_name,
                details=[]
            )

            details_result = db.execute(text("""
                SELECT od.*, b.book_name, b.authors 
                FROM order_details od
                LEFT JOIN books b ON od.book_isbn = b.isbn
                WHERE od.order_id = :order_id
            """), {"order_id": order_data.order_id}).fetchall()

            for detail in details_result:
                detail_data = OrderDetail(
                    order_detail_id=detail.order_detail_id,
                    order_id=detail.order_id,
                    book_isbn=detail.book_isbn,
                    quantity=detail.quantity,
                    unit_price=float(detail.unit_price),
                    book_name=detail.book_name,
                    authors=detail.authors
                )
                order_data.details.append(detail_data)

            orders.append(order_data)

        return orders

    except Exception as e:
        print(f"Error in get_store_orders: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@routerbookorders.put("/{order_id}", response_model=Order)
async def update_order_status(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        if current_user.type != "store":
            raise HTTPException(status_code=403, detail="Only stores can update order status")

        updated  = db.execute(text("""
            SELECT o.*, b.address as shipping_address, s.address as store_address
            FROM orders o
            JOIN participants b ON o.user_id = b.id
            JOIN participants s ON o.store_id = s.id
            WHERE o.order_id = :order_id
        """), {"order_id": order_id}).fetchone()

        if not updated:
            raise HTTPException(status_code=404, detail="Order not found")

        order_data = Order(
            order_id=updated.order_id,
            user_id=updated.user_id,
            store_id=updated.store_id,
            total_price=float(updated.total_price),
            status=updated.status,
            order_date=updated.order_date,
            details=[]
        )

        details_result = db.execute(text("""
            SELECT od.*, b.book_name, b.authors
            FROM order_details od
            JOIN books b ON od.book_isbn = b.isbn
            WHERE od.order_id = :order_id
        """), {"order_id": order_id}).fetchall()

        for detail in details_result:
            detail_data = OrderDetail(
                order_detail_id=detail.order_detail_id,
                order_id=detail.order_id,
                book_isbn=detail.book_isbn,
                quantity=detail.quantity,
                unit_price=float(detail.unit_price),
                book_name=detail.book_name,
                authors=detail.authors
            )
            order_data.details.append(detail_data)

        db.commit()
        return order_data

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@routerbookorders.delete("/{order_id}")
async def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        order = db.execute(text("""
            SELECT * FROM orders 
            WHERE order_id = :order_id 
            AND user_id = :user_id 
            AND status = 'pending'
        """), {
            "order_id": order_id,
            "user_id": current_user.id
        }).fetchone()

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found or cannot be cancelled"
            )

        details = db.execute(text("""
            SELECT * FROM order_details 
            WHERE order_id = :order_id
        """), {
            "order_id": order_id
        }).fetchall()

        for detail in details:
            db.execute(text("""
                UPDATE books 
                SET inventory = inventory + :quantity 
                WHERE isbn = :isbn
            """), {
                "quantity": detail.quantity,
                "isbn": detail.book_isbn
            })

        db.execute(text("""
            DELETE FROM orders 
            WHERE order_id = :order_id
        """), {
            "order_id": order_id
        })

        db.commit()
        return {"message": "Order cancelled successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
from app_design.dependencies.deps  import get_current_admin
# 修改获取单个订单详情的查询
@routerbookorders.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取订单详情"""
    try:
        # 先查询订单基本信息
        order_result = db.execute(text("""
            SELECT o.*,
                   b.name as buyer_name,
                   b.address as shipping_address,
                   s.name as store_name,
                   s.address as store_address
            FROM orders o
            JOIN participants b ON o.user_id = b.id
            JOIN participants s ON o.store_id = s.id
            WHERE o.order_id = :order_id
        """), {
            "order_id": order_id
        }).fetchone()

        if not order_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        # 检查访问权限
        if (current_user.id != order_result.user_id and 
            current_user.id != order_result.store_id and 
            current_user.type != 'administrator'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this order"
            )

        # 查询订单详情
        details_result = db.execute(text("""
            SELECT od.*, 
                   b.book_name,
                   b.authors,
                   b.image_url
            FROM order_details od
            JOIN books b ON od.book_isbn = b.isbn
            WHERE od.order_id = :order_id
        """), {
            "order_id": order_id
        }).fetchall()

        # 构建返回数据
        order_data = {
            "order_id": order_result.order_id,
            "user_id": order_result.user_id,
            "store_id": order_result.store_id,
            "buyer_name": order_result.buyer_name,
            "shipping_address": order_result.shipping_address,
            "store_name": order_result.store_name,
            "store_address": order_result.store_address,
            "total_price": float(order_result.total_price),
            "status": order_result.status,
            "order_date": order_result.order_date,
            "details": []
        }

        for detail in details_result:
            detail_data = {
                "order_detail_id": detail.order_detail_id,
                "order_id": detail.order_id,
                "book_isbn": detail.book_isbn,
                "quantity": detail.quantity,
                "unit_price": float(detail.unit_price),
                "book_name": detail.book_name,
                "authors": detail.authors,
                "image_url": detail.image_url
            }
            order_data["details"].append(detail_data)

        # 打印调试信息
        print(f"Order data: {order_data}")
        return order_data

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error getting order details: {str(e)}")  # 添加日志
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
# 在 orders.py 中修改获取订单列表的查询
class Order(BaseModel):
    order_id: int
    user_id: int
    store_id: int
    buyer_name: str | None = None
    shipping_address: str | None = None
    store_name: str | None = None
    store_address: str | None = None
    total_price: float
    status: str
    order_date: date
    details: List[OrderDetail] = []

    class Config:
        from_attributes = True
@routerbookorders.get("/", response_model=List[Order])
async def get_all_orders(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)  # 确保只有管理员可以访问
):
    """获取所有订单"""
    try:
        orders_result = db.execute(text("""
            SELECT o.*,
                   b.name as buyer_name,
                   b.address as shipping_address,
                   s.name as store_name, 
                   s.address as store_address
            FROM orders o
            JOIN participants b ON o.user_id = b.id
            JOIN participants s ON o.store_id = s.id
            ORDER BY o.order_date DESC
            OFFSET :skip LIMIT :limit
        """), {
            "skip": skip,
            "limit": limit
        }).fetchall()

        orders = []
        for order in orders_result:
            # 获取订单详情
            details = db.execute(text("""
                SELECT od.*, b.book_name, b.authors, b.image_url
                FROM order_details od
                JOIN books b ON od.book_isbn = b.isbn
                WHERE od.order_id = :order_id
            """), {"order_id": order.order_id}).fetchall()

            order_details = []
            for detail in details:
                detail_data = {
                    "order_detail_id": detail.order_detail_id,
                    "order_id": detail.order_id,
                    "book_isbn": detail.book_isbn,
                    "quantity": detail.quantity,
                    "unit_price": float(detail.unit_price),
                    "book_name": detail.book_name,
                    "authors": detail.authors,
                    "image_url": detail.image_url
                }
                order_details.append(detail_data)

            order_data = {
                "order_id": order.order_id,
                "user_id": order.user_id,
                "store_id": order.store_id,
                "buyer_name": order.buyer_name,
                "shipping_address": order.shipping_address,
                "store_name": order.store_name,
                "store_address": order.store_address,
                "total_price": float(order.total_price),
                "status": order.status,
                "order_date": order.order_date,
                "details": order_details
            }
            orders.append(order_data)

        return orders
    except Exception as e:
        print(f"Error in get_all_orders: {str(e)}")  # 添加日志
        raise HTTPException(status_code=500, detail=str(e))
