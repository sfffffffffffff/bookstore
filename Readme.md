# 在线书店系统设计文档
本项目为复旦大学2024年秋季数据库pj设计，请同学万万不要于该学期使用该pj，该项目置于此以便于向助教展示成果
本系统是一个在线书店电子商务平台，旨在为用户提供图书在线购买服务。系统支持多角色用户管理、商品管理、购物车、订单处理等功能，实现图书销售的完整业务流程。
![alt text](readmepicture/ER图.png)
## 属性表
### Participant (参与者表)
- **ID**: 唯一标识符
- **Name**: 字符串
- **Password**: 加密存储
- **Email**: 字符串
- **Address**: 字符串
- **Type**: 字符串 (buyer, Store, Administrator)

### Books (书籍表)
- **ISBN**: 唯一标识符
- **BookName**: 字符串
- **Authors**: 字符串
- **Category**: 字符串
- **Inventory**: 整数
- **Price**: 浮点数
- **StoreID**: 外键 (Participant)

### Orders (订单表)
- **OrderID**: 唯一标识符
- **UserID**: 外键 (Participant)
- **StoreID**: 外键 (Participant)
- **TotalPrice**: 浮点数
- **Status**: 字符串
- **OrderDate**: 日期

### OrderDetails (订单详情表)
- **OrderDetailID**: 唯一标识符
- **OrderID**: 外键 (Orders)
- **BookISBN**: 外键 (Books)
- **Quantity**: 整数
- **UnitPrice**: 浮点数

### CartItems (购物车项目表)
- **CartItemID**: 唯一标识符
- **UserID**: 外键 (Participant)
- **BookISBN**: 外键 (Books)
- **Quantity**: 整数

## 1.需求分析

### 1.1用户管理需求

#### 1.1.1用户注册和登录
- 用户可以注册新账户，填写姓名、邮箱、密码等信息
- 系统需验证邮箱的唯一性，并可能通过邮件验证用户邮箱
- 用户登录时需输入邮箱和密码
- 忘记密码功能，通过邮箱重置

#### 1.1.2用户角色和权限

**买家权限：**
- 浏览书籍
- 搜索书籍
- 添加书籍到购物车
- 创建和查看订单
- 查看和编辑个人信息

**商店权限：**
- 管理自己的书籍库存（添加、更新、删除书籍）
- 查看自己的订单
- 设置书籍价格和库存
- 查看和编辑个人信息
- 修改订单状态

**管理员权限：**
- 管理所有账户
- 查看必要时修改订单
- 修改系统设置（如增加新的书籍类别）
- 管理网站内容

### 1.2书籍管理需求

#### 1.2.1书籍信息维护
- 商店用户可以添加新书籍，需要填写ISBN、书名、作者、分类、价格和库存等信息
- 商店用户可以更新或删除自己商店的书籍信息
- 买家可以浏览所有可购买的书籍，并通过分类、作者、价格等条件进行筛选和搜索

### 1.3订单管理需求

#### 1.3.1订单创建和管理
- 买家在购物车中选择书籍后可以创建订单
- 订单包含多个书籍，每本书籍的数量和价格需在创建订单时确认
- 订单创建后，系统自动减少相应书籍的库存数量
- 买家可以查看自己的历史订单和当前订单状态（待发货、已发货、已完成）
- 商店可以查看由其提供书籍的订单详细信息

#### 1.3.2购物车管理
- 买家可以将书籍添加到购物车，包括选择数量
- 买家可以更改购物车中书籍的数量或将书籍移除
- 购物车中显示所有书籍的总价格

### 1.4安全性和数据保护需求

#### 1.4.1数据加密和安全
- 所有用户密码在数据库中加密存储
- 使用HTTPS协议加密所有数据传输
- 实现CSRF和XSS防护策略保护网站免受攻击
- 数据库采用SQL注入防护措施

#### 1.4.2隐私保护
- 确保所有用户数据按照隐私政策处理
- 用户有权查看和请求删除自己的个人信息

### 2.2 技术栈

#### 后端
- FastAPI：Python Web 框架
- PostgreSQL：关系型数据库
- SQLAlchemy：ORM
- JWT：用户认证
- Python 3.8+

#### 前端
- Vue 3：前端框架
- Vue Router：路由管理
- Vuex：状态管理
- Axios：HTTP 客户端
- Element Plus：UI 组件库

## 二、功能概要
### 主要功能

- 未登录时，只显示页面书籍，登录选项，此时页面书籍加入购物车无权限。登录之后加入购物车有权限。
   ![alt text](readmepicture/image.png)
- 未注册可以选择注册，但是注册只能注册用户与商家，管理员只能管理员登录之后添加。
![alt text](readmepicture/image.png)

- 不同角色有不同的界面显示，用户有我的订单与购物车界面，默认界面为书籍商城，如果购物车为空，点击去逛逛来到商城，点击不同分类，可以分类显示，搜索栏用@可以实现精确搜索。点击加入购物车，如果库存大于0，会将商品加入到购物车中，点击购物车，结算，会生成订单，点击我的订单可以查询订单，可以取消未发货的订单。

![image](https://github.com/user-attachments/assets/b43f1ccf-7633-4743-bde2-efb911929d11)
![image](https://github.com/user-attachments/assets/2d7eef1e-0e4e-46f9-b052-c3bedc4197e9)
![image](https://github.com/user-attachments/assets/e2f06409-e264-416c-b2ce-c9dbf128cc91)
![image](https://github.com/user-attachments/assets/7ce2b647-57d4-4fe7-94e1-79317b6413d6)
![image](https://github.com/user-attachments/assets/301fb684-96b9-4fa8-9247-396efa91c664)


- 店家有店家面板，此时默认登录后界面依旧为商城，但是此时，用户无权限加入购物车。店家面板中有订单管理与商品管理，订单管理可以修改订单状态，书籍管理可以新增书籍信息，可以更新书籍信息，可以查看目前库存预警。
![image](https://github.com/user-attachments/assets/6932fd3b-42d6-4d3c-88b0-ba288d9385de)
![image](https://github.com/user-attachments/assets/a18ad736-b29c-4f6e-b2b1-b5f780c50c79)
![image](https://github.com/user-attachments/assets/53cb97b8-ce7d-4bb5-bfa1-4edf4f79a01a)
![image](https://github.com/user-attachments/assets/f6b05d7b-2b9d-4764-ab38-6e0b10d63d12)
![image](https://github.com/user-attachments/assets/e957be68-c2be-4a3e-849e-cbaacacb9c7a)
![image](https://github.com/user-attachments/assets/f9eb108d-726a-4bcf-9e6d-2844456734be)

- 管理员有管理员面板，此时默认登录后界面依旧为商城，但是此时，用户无权限加入购物车。管理员面板有用户管理，订单管理，商品管理，管理员可以新增用户，修改用户昵称，地址，密码，权限。订单管理管理员可以查看订单详情，删除订单，商品管理，管理员可以修改书籍信息。
  ![image](https://github.com/user-attachments/assets/210970ca-79ff-4ae8-88a5-3977e5bce2f9)
![image](https://github.com/user-attachments/assets/fcf45827-d7c7-4e4b-b528-653ed0fe6b36)
![image](https://github.com/user-attachments/assets/7fdb0458-daf6-404d-ae6b-53b5883cc173)




## 三、详细设计

### 3.1 数据库设计
#### 数据库设计

##### PostgreSQL 表结构

```sql
-- 用户表
CREATE TABLE participants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    address TEXT,
    type VARCHAR(50) NOT NULL
);

-- 图书表
CREATE TABLE books (
    isbn VARCHAR(20) PRIMARY KEY,
    book_name VARCHAR(255) NOT NULL,
    authors VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    inventory INTEGER NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    store_id INTEGER REFERENCES participants(id) ON DELETE CASCADE,
    image_url VARCHAR(255)
);

-- 购物车表
CREATE TABLE cart_items (
    cart_item_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES participants(id) ON DELETE CASCADE,
    book_isbn VARCHAR(20) REFERENCES books(isbn) ON DELETE CASCADE,
    quantity INTEGER NOT NULL
);

-- 订单表
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES participants(id) ON DELETE CASCADE,
    store_id INTEGER REFERENCES participants(id) ON DELETE CASCADE,
    total_price NUMERIC(10,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    order_date DATE NOT NULL
);

-- 订单详情表
CREATE TABLE order_details (
    order_detail_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
    book_isbn VARCHAR(20) REFERENCES books(isbn) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL
);
```

### 3.2 API 路由设计

#### 用户相关
- POST `/participants/`: 创建新用户
- POST `/login/`: 用户登录
- GET `/user/me`: 获取当前用户信息
- PUT `/user/me`: 更新用户信息
- DELETE `/user/me`: 删除账号

#### 管理员路由
- GET `/user/`: 获取所有用户
- POST `/user/admin/create`: 创建管理员
- PUT `/user/{user_id}`: 更新用户
- DELETE `/user/{user_id}`: 删除用户

#### 图书相关
- POST `/book/`: 创建新书籍
- GET `/book/search`: 搜索书籍
- GET `/book/{isbn}`: 获取书籍详情
- PUT `/book/{isbn}`: 更新书籍
- DELETE `/book/{isbn}`: 删除书籍
- GET `/book/category/{category}`: 按分类获取书籍
- GET `/book/store/{store_id}`: 获取店铺书籍
- POST `/upload/{isbn}`: 上传书籍图片

#### 购物车相关
- GET `/cart/`: 获取购物车
- POST `/cart/`: 添加到购物车
- PUT `/cart/{cart_item_id}`: 更新购物车商品
- DELETE `/cart/{cart_item_id}`: 删除购物车商品
- POST `/cart/checkout`: 结算购物车

#### 订单相关
- GET `/bookorders/`: 获取所有订单
- POST `/bookorders/`: 创建订单
- GET `/bookorders/{order_id}`: 获取订单详情
- PUT `/bookorders/{order_id}`: 更新订单状态
- DELETE `/bookorders/{order_id}`: 删除订单
- GET `/bookorders/my-orders`: 获取我的订单
- GET `/bookorders/store-orders`: 获取店铺订单

#### 前端页面结构

- `/`: 首页，展示商品列表
- `/login`: 登录/注册页面
- `/admin`: 管理员后台
- `/store`: 商家管理面板
- `/orders`: 订单管理
- `/cart`: 购物车
- `/profile`: 个人资料
- `/forgot-password`: 忘记密码

#### 组件结构
```
src/
├── components/
│   ├── AdminPanel.vue    # 管理员面板
│   ├── StorePanel.vue    # 商家面板
│   ├── Login.vue         # 登录页面
│   ├── Profile.vue       # 个人信息
│   ├── Cart.vue          # 购物车
│   ├── Orders.vue        # 订单列表
│   └── Home.vue          # 首页
├── stores/
│   └── store.js          # Vuex 存储
├── router/
│   └── index.ts          # 路由配置
├── assets/               # 静态资源
└── App.vue              # 根组件
```

#### 项目结构

```
BOOKSRORE/
├── Backdesign/
│   ├── app_design/
│   │   ├── dependencies/
|   |   |     |————deps.py
|   |   |———books.py
│   │   ├── cart_item.py
│   │   ├── orders.py
│   │   └── users.py
|   |—— db.py
│   ├── main.py
│   └── core/
|       |————config.py
|       |————security.py
├── Frontdesign/
│   ├── src/
│   ├── public/
│   └── package.json
└── README.md
```

### 3.3 核心功能实现

#### 3.2.1 用户认证流程
1. 用户登录
```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant DB as Database
    C->>S: POST /login/ {username, password}
    S->>DB: 验证用户凭证
    DB-->>S: 返回用户信息
    S->>S: 生成JWT Token
    S-->>C: 返回Token和用户信息
```

2. 权限验证
```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user_id
```

#### 3.2.2 购物流程
1. 添加到购物车
```sequence
User->Frontend: 点击"加入购物车"
Frontend->Backend: POST /cart/ {book_isbn, quantity}
Backend->Database: 检查库存
Database-->Backend: 返回库存信息
Backend->Database: 创建购物车项
Backend-->Frontend: 返回结果
Frontend-->User: 显示成功提示
```

2. 订单创建
```python
async def create_order(cart_items, user_id):
    with transaction.atomic():
        # 创建订单
        order = Order.create(user_id=user_id)
        
        # 添加订单项
        for item in cart_items:
            OrderItem.create(
                order_id=order.id,
                book_isbn=item.book_isbn,
                quantity=item.quantity
            )
            
        # 更新库存
        Book.update_inventory(item.book_isbn, item.quantity)
            
        # 清空购物车
        Cart.clear(user_id)
    
    return order
```

### 3.3 API接口设计

#### 3.3.1 用户接口
```yaml
POST /login/:
  description: 用户登录
  request:
    body:
      username: string
      password: string
  response:
    token: string
    user_type: string
```

#### 3.3.2 商品接口
```yaml
GET /book/search:
  description: 搜索图书
  parameters:
    q: string
    category: string
  response:
    books: array<Book>
```

## 四、部署方法

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 配置数据库
```bash
# 创建数据库
psql -U postgres
CREATE DATABASE bookstore;
```

3. 安装前端依赖
```bash
cd Frontdesign\vue_bookstore
npm install
```

4. 运行服务
```bash
# 后端
cd Backdesign\main_sqlmodel.py
python main_sqlmodel.py

# 前端
cd Frontdesign\vue_bookstore
npm run dev
```



## 注意事项
1. 首次运行会初始化生成管理员账号
```
password("admin123")
name="Admin",
email="admin@bookstore.com",
address="Admin Office",
type="administrator"
            
```
2. 请确保正确配置数据库连接信息
目前为
```
DATABASE_URL = "postgresql://postgres:15466515aA@localhost/bookstore"
```
需要修改
3. 图片上传需要配置存储路径
因书籍图片不是很重要，数据库中只存储了书籍图片url,书籍存储在uploads\books中
4. 建议在生产环境中修改密钥





## 许可证
MIT License
