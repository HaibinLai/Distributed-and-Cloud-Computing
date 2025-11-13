import os
import logging
from concurrent import futures
from datetime import timezone

import grpc
import psycopg2
from google.protobuf.timestamp_pb2 import Timestamp

import db_pb2
import db_pb2_grpc

# ---------- 数据库工具 ----------

def get_connection():
    """
    简单起见：每个 RPC 新建一个连接。
    真要上生产可改成连接池，比如 psycopg2.pool.SimpleConnectionPool。
    """
    dsn = os.environ.get(
        "PG_DSN",
        "dbname=goodsstore user=dncc password=dncc host=localhost port=5432",
    )
    return psycopg2.connect(dsn)


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
            conn.close()

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
            conn.close()

    # ---- Users ----
    def CreateUser(self, request, context):
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
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
                    return row_to_user(row)
        finally:
            conn.close()

    # ---- Orders ----
    def CreateOrder(self, request, context):
        """
        简化版逻辑：
        1. 读取 product 价格 & 库存
        2. 检查库存和数量约束
        3. 新建订单表记录
        4. 扣减库存
        全部在一个事务里完成
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    # 1. 获取商品
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

                    price, stock = prod_row
                    qty = request.quantity
                    if qty <= 0 or qty > 3:
                        context.abort(grpc.StatusCode.INVALID_ARGUMENT, "quantity must be 1~3")
                    if stock < qty:
                        context.abort(grpc.StatusCode.FAILED_PRECONDITION, "not enough stock")

                    total_price = float(price) * qty

                    # 2. 插入订单
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

                    # 3. 扣减库存
                    cur.execute(
                        """
                        UPDATE products
                        SET stock = stock - %s
                        WHERE id = %s
                        """,
                        (qty, request.product_id),
                    )

                    return row_to_order(order_row)
        finally:
            conn.close()

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
            conn.close()


# ---------- 启动 gRPC Server ----------

def serve(port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    db_pb2_grpc.add_DbServiceServicer_to_server(DbService(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logging.info("DB gRPC server started on port %d", port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    serve()
