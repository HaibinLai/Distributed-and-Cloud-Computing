import os
import logging
from concurrent import futures
from datetime import timezone

import grpc
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from google.protobuf.timestamp_pb2 import Timestamp

import db_pb2
import db_pb2_grpc

# import psycopg2

# ---------- 数据库工具 ----------

# def get_connection():
#     """
#     简单起见：每个 RPC 新建一个连接。
#     真要上生产可改成连接池，比如 psycopg2.pool.SimpleConnectionPool。
#     """
#     dsn = os.environ.get(
#         "PG_DSN",
#         "dbname=goodsstore user=dncc password=dncc host=localhost port=5432",
#     )
#     return psycopg2.connect(dsn)

# ---------- 全局连接池 ----------

POOL: SimpleConnectionPool | None = None


def init_pool():
    """
    初始化全局连接池。
    在 Docker Compose 里，host 一般写 postgres（service 名），
    你也可以通过 PG_DSN 环境变量覆盖。
    """
    global POOL
    if POOL is not None:
        return

    dsn = os.environ.get("POSTGRES_DSN")
    if not dsn:
        # 没传 env，就用默认的 *postgres*，千万不要 localhost
        dsn = "dbname=goodsstore user=dncc password=dncc host=postgres port=5432"

    logging.info(f"Initializing DB connection pool with DSN: {dsn}")
    POOL = SimpleConnectionPool(minconn=1, maxconn=10, dsn=dsn)


def get_connection():
    """
    从连接池拿一个连接。
    """
    if POOL is None:
        init_pool()
    return POOL.getconn()


def release_connection(conn):
    """
    归还连接到连接池。
    """
    if POOL is not None:
        POOL.putconn(conn)
    else:
        conn.close()




def row_to_product(row):
    # row 顺序必须和 SQL SELECT 的字段顺序一致
    p = db_pb2.Product()
    p.id = row[0]
    p.name = row[1]
    p.description = row[2] or ""
    p.category = row[3] or ""
    p.price = float(row[4])
    p.slogan = row[5] or ""
    p.stock = row[6]
    if row[7] is not None:
        ts = Timestamp()
        # 这里简单认为是 UTC（如果你的 DB 是本地时间，可以根据需要调整）
        ts.FromDatetime(row[7].replace(tzinfo=timezone.utc))
        p.created_at.CopyFrom(ts)
    return p


def row_to_user(row):
    u = db_pb2.User()
    u.id = row[0]
    u.sid = row[1]
    u.username = row[2]
    u.email = row[3] or ""
    u.password_hash = row[4]
    if row[5] is not None:
        ts = Timestamp()
        ts.FromDatetime(row[5].replace(tzinfo=timezone.utc))
        u.created_at.CopyFrom(ts)
    return u


# // id, sid, username, password_hash, created_at
def row_to_user2(row):
    u = db_pb2.User()
    u.id = row[0]
    u.sid = row[1]
    u.username = row[2]
    u.email = row[3] or ""
    u.password_hash = row[4]
    if row[5] is not None:
        ts = Timestamp()
        ts.FromDatetime(row[5].replace(tzinfo=timezone.utc))
        u.created_at.CopyFrom(ts)
    return u



def row_to_order(row):
    o = db_pb2.Order()
    o.id = row[0]
    o.user_id = row[1]
    o.product_id = row[2]
    o.quantity = row[3]
    o.total_price = float(row[4])
    if row[5] is not None:
        ts = Timestamp()
        ts.FromDatetime(row[5].replace(tzinfo=timezone.utc))
        o.created_at.CopyFrom(ts)
    return o


# ---------- gRPC Service 实现 ----------

class DbService(db_pb2_grpc.DbServiceServicer):

    def _row_to_user(row):
        u = db_pb2.User()
        u.id = row[0]
        u.sid = row[1]
        u.username = row[2]
        u.email = row[3] or ""
        u.password_hash = row[4]
        if row[5] is not None:
            ts = Timestamp()
            ts.FromDatetime(row[5].replace(tzinfo=timezone.utc))
            u.created_at.CopyFrom(ts)
        return u

    # ---- Products ----
    def CreateProduct(self, request, context):
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO products
                          (name, description, category, price, slogan, stock)
                        VALUES (%s, %s, %s, %s, %s, COALESCE(%s, 500))
                        RETURNING id, name, description, category, price, slogan, stock, created_at
                        """,
                        (
                            request.name,
                            request.description,
                            request.category,
                            request.price,
                            request.slogan,
                            request.stock if request.stock != 0 else None,
                        ),
                    )
                    row = cur.fetchone()
                    return row_to_product(row)
        finally:
            release_connection(conn)

    def ListProducts(self, request, context):
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    params = []
                    where = ""
                    if request.category:
                        where = "WHERE category = %s"
                        params.append(request.category)

                    page = request.page if request.page > 0 else 1
                    page_size = request.page_size if request.page_size > 0 else 20
                    offset = (page - 1) * page_size

                    # total count
                    cur.execute(f"SELECT COUNT(*) FROM products {where}", params)
                    total_count = cur.fetchone()[0]

                    # data
                    cur.execute(
                        f"""
                        SELECT id, name, description, category, price, slogan, stock, created_at
                        FROM products
                        {where}
                        ORDER BY id
                        LIMIT %s OFFSET %s
                        """,
                        params + [page_size, offset],
                    )
                    rows = cur.fetchall()
                    products = [row_to_product(r) for r in rows]

            return db_pb2.ListProductsResponse(
                products=products,
                page=page,
                page_size=page_size,
                total_count=total_count,
            )
        finally:
            release_connection(conn)

    def GetProduct(self, request, context):
        """
        根据 id 返回单个商品
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, name, description, category, price, slogan, stock, created_at
                        FROM products
                        WHERE id = %s
                        """,
                        (request.id,),
                    )
                    row = cur.fetchone()
                    if row is None:
                        # gRPC 层返回 NOT_FOUND，API 那边可以翻译成 404
                        context.abort(grpc.StatusCode.NOT_FOUND, "product not found")
                    return row_to_product(row)
        finally:
            release_connection(conn)

    # ---- Users ----
    def CreateUser(self, request, context):
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    # 如果这里已经有现成的user了，会抛 UniqueViolation 异常
                    try:
                        cur.execute(
                            """
                            INSERT INTO users (sid, username, email, password_hash)
                            VALUES (%s, %s, %s, %s)
                            RETURNING id, sid, username, email, password_hash, created_at
                            """,
                            (
                                request.sid,
                                request.username,
                                request.email,
                                request.password_hash,
                            ),
                        )
                        row = cur.fetchone()
                    except psycopg2.IntegrityError as e:
                        context.abort(grpc.StatusCode.ALREADY_EXISTS, "user with this SID already exists")
                    

                    return row_to_user(row)
        finally:
            release_connection(conn)

    def GetUserBySid(self, request, context):
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, sid, username, email, password_hash, created_at
                        FROM users
                        WHERE sid = %s
                        """,
                        (request.sid,),
                    )
                    row = cur.fetchone()

                    if row is None:
                        context.set_code(grpc.StatusCode.NOT_FOUND)
                        context.set_details(f"user with sid={request.sid} not found")
                        # 返回一个空的响应即可，不要去 row_to_user(None)
                        # 好像不能这样！ gRPC 规范要求必须返回一个 User
                        return db_pb2.User()

                    # 把 row 转成 User proto
                    user_msg = row_to_user2(row)
                    # 再包装进 Response 里返回
                    return user_msg
        finally:
            release_connection(conn)


    def UpdateUser(self, request, context):
        """
        根据 user id 更新用户信息，并返回更新后的 User。
        这里假设 UpdateUserRequest 里至少有：
          - id
          - username
          - email
          - password_hash
        如果你的 proto 字段名不一样，把 request.xxx 换成对应的名字即可。
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    # 用 id 作为主键进行更新
                    # 如果找不到user，返回 NOT_FOUND
                    cur.execute(
                        """
                        UPDATE users
                        SET username = %s,
                            email = %s,
                            password_hash = %s
                        WHERE id = %s
                        RETURNING id, sid, username, email, password_hash, created_at
                        """,
                        (
                            request.username,
                            request.email,
                            request.password_hash,
                            request.id,
                        ),
                    )

                    row = cur.fetchone()

                    # 如果没有更新到任何行，说明这个 id 不存在
                    if row is None:
                        context.set_code(grpc.StatusCode.NOT_FOUND)
                        context.set_details(f"user with id={request.id} not found")
                        # gRPC 要求必须返回一个同类型消息，这里返回空的 User
                        return db_pb2.User()

                    # 把 row 转成 User proto 返回
                    user_msg = row_to_user2(row)
                    return user_msg
        finally:
            release_connection(conn)

    def DeleteUser(self, request, context):
        """
        根据用户 id 删除该用户。
        DeleteUserRequest:
            int32 id = 1;
        DeleteUserResponse:
            bool success = 1;

            def row_to_user(row):
    u = db_pb2.User()
    u.id = row[0]
    u.sid = row[1]
    u.username = row[2]
    u.email = row[3] or ""
    u.password_hash = row[4]
    if row[5] is not None:
        ts = Timestamp()
        ts.FromDatetime(row[5].replace(tzinfo=timezone.utc))
        u.created_at.CopyFrom(ts)
    return u
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:

                    # 先尝试查询
                    cur.execute(
                        """
                        SELECT id, sid, username, email, password_hash, created_at
                        FROM users
                        WHERE id = %s
                        """,
                        (request.id,)
                    )
                    row = cur.fetchone()

                    # row 为 None 表示没有匹配的 id
                    if row is None:
                        context.set_code(grpc.StatusCode.NOT_FOUND)
                        context.set_details(f"user with id={request.id} not found")
                        # 返回空的响应对象（保持 gRPC 类型一致）
                        return db_pb2.User()

                    # 再尝试删除
                    cur.execute(
                        """
                        DELETE FROM users
                        WHERE id = %s
                        RETURNING id
                        """,
                        (request.id,)
                    )

                    row2 = cur.fetchone()

                    # row2 为 None 表示没有匹配的 id
                    if row2 is None:
                        context.set_code(grpc.StatusCode.NOT_FOUND)
                        context.set_details(f"user with id={request.id} not found")
                        # 返回空的响应对象（保持 gRPC 类型一致）
                        return db_pb2.User()

                    # 删除成功
                    return row_to_user(row)

        finally:
            release_connection(conn)



    # ---- Orders ----
    def CreateOrder(self, request, context):
        """
        CreateOrder 逻辑说明（在一个事务里完成）：
        1. 使用 SELECT ... FOR UPDATE 锁定商品行，读取 price 与 stock
        2. 校验 quantity 范围（1~3）以及库存是否足够
        3. 基于数据库中的 price 计算 total_price（使用 Decimal 处理金额）
        4. 向 orders 表插入新订单记录，并返回生成的订单信息
        5. 扣减 products 表中的库存

        所有 SQL 操作都使用参数化查询（%s + 参数元组），防止 SQL 注入。
        价格只信任数据库中的 price，不信任客户端传入的任何金额字段。
        """
        conn = get_connection()
        try:
            with conn:  # 开启一个事务，退出时自动 commit / rollback
                with conn.cursor() as cur:
                    # 1. 锁定商品行，读取价格和库存
                    cur.execute(
                        """
                        SELECT price, stock
                        FROM products
                        WHERE id = %s
                        FOR UPDATE
                        """,
                        (request.product_id,),
                    )
                    prod_row = cur.fetchone()
                    if prod_row is None:
                        context.abort(grpc.StatusCode.NOT_FOUND, "product not found")

                    price, stock = prod_row  # price: NUMERIC -> Decimal, stock: int

                    # 2. 校验数量和库存
                    qty = int(request.quantity)
                    if qty <= 0 or qty > 3:
                        context.abort(
                            grpc.StatusCode.INVALID_ARGUMENT,
                            "quantity must be between 1 and 3",
                        )

                    if stock < qty:
                        context.abort(
                            grpc.StatusCode.FAILED_PRECONDITION,
                            "not enough stock",
                        )

                    # 3. 计算总价（基于 DB 中的 price，使用 Decimal 防止 float 精度问题）
                    # psycopg2 读取 NUMERIC 默认就是 Decimal，可以直接 * qty

                    # ---- Orders ----
                    from decimal import Decimal
                    import grpc
                    import db_pb2
                    if not isinstance(price, Decimal):
                        price = Decimal(str(price))
                    total_price = price * Decimal(qty)

                    total_price = float(total_price)

                    # 4. 插入订单记录（参数化查询，防 SQL 注入）
                    cur.execute(
                        """
                        INSERT INTO orders (user_id, product_id, quantity, total_price)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id, user_id, product_id, quantity, total_price, created_at
                        """,
                        (
                            request.user_id,
                            request.product_id,
                            qty,
                            total_price,
                        ),
                    )
                    order_row = cur.fetchone()
                    # order_row
                    if order_row is None:
                        context.abort(
                            grpc.StatusCode.INTERNAL,
                            "failed to create order",
                        )

                    # 5. 扣减库存（同一个事务内，且商品行已被 FOR UPDATE 锁定）
                    cur.execute(
                        """
                        UPDATE products
                        SET stock = stock - %s
                        WHERE id = %s
                        """,
                        (qty, request.product_id),
                    )

                    # row_to_order: 将 DB 行转换成 db_pb2.Order
                    return row_to_order(order_row)
        except Exception as e:
            # 出现异常时，事务会自动回滚
            conn.rollback()
        finally:
            release_connection(conn)

    def ListOrdersByUser(self, request, context):
            conn = get_connection()
            try:
                with conn:
                    with conn.cursor() as cur:
                        page = request.page if request.page > 0 else 1
                        page_size = request.page_size if request.page_size > 0 else 20
                        offset = (page - 1) * page_size

                        cur.execute(
                            """
                            SELECT COUNT(*)
                            FROM orders
                            WHERE user_id = %s
                            """,
                            (request.user_id,),
                        )
                        total_count = cur.fetchone()[0]

                        cur.execute(
                            """
                            SELECT id, user_id, product_id, quantity, total_price, created_at
                            FROM orders
                            WHERE user_id = %s
                            ORDER BY created_at DESC
                            LIMIT %s OFFSET %s
                            """,
                            (request.user_id, page_size, offset),
                        )
                        rows = cur.fetchall()
                        orders = [row_to_order(r) for r in rows]

                return db_pb2.ListOrdersResponse(
                    orders=orders,
                    page=page,
                    page_size=page_size,
                    total_count=total_count,
                )
            finally:
                release_connection(conn)


    def GetOrder(self, request, context):
            conn = get_connection()
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            SELECT id, user_id, product_id, quantity, total_price, created_at
                            FROM orders
                            WHERE id = %s
                            """,
                            (request.id,),
                        )
                        row = cur.fetchone()
                        if row is None:
                            context.abort(grpc.StatusCode.NOT_FOUND, "order not found")

                        return row_to_order(row)

            finally:
                release_connection(conn)


    def DeleteOrder(self, request, context):
        """
        取消订单：
        1. 查出订单的 product_id 和 quantity，并锁住这条订单记录；
        2. 删除订单；
        3. 把数量加回对应商品的库存。
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    # 1. 查订单，并加行锁，防止并发修改
                    cur.execute(
                        """
                        SELECT product_id, quantity
                        FROM orders
                        WHERE id = %s
                        FOR UPDATE
                        """,
                        (request.id,),
                    )
                    row = cur.fetchone()
                    if row is None:
                        # 订单不存在
                        context.abort(grpc.StatusCode.NOT_FOUND, "order not found")

                    product_id, qty = row

                    # 2. 删除订单
                    cur.execute(
                        """
                        DELETE FROM orders
                        WHERE id = %s
                        """,
                        (request.id,),
                    )

                    # 3. 库存加回去
                    cur.execute(
                        """
                        UPDATE products
                        SET stock = stock + %s
                        WHERE id = %s
                        """,
                        (qty, product_id),
                    )

            from google.protobuf import empty_pb2
            return empty_pb2.Empty()

        finally:
            release_connection(conn)

    



# ---------- 启动 gRPC Server ----------


def serve(port: int = 50051):
    logging.basicConfig(level=logging.INFO)

    # 先初始化连接池
    init_pool()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    db_pb2_grpc.add_DbServiceServicer_to_server(DbService(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logging.info("DB gRPC server started on port %d", port)

    try:
        server.wait_for_termination()
    finally:
        # 进程退出前关掉连接池
        global POOL
        if POOL is not None:
            POOL.closeall()
            POOL = None
            logging.info("DB connection pool closed.")


if __name__ == "__main__":
    serve()