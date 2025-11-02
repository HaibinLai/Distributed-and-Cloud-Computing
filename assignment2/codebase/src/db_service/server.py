import grpc, time
from concurrent.futures import ThreadPoolExecutor
import psycopg2
from pool import conn, put
import db_pb2, db_pb2_grpc
from grpc import StatusCode

class DbImpl(db_pb2_grpc.DbServiceServicer):
    def ListProducts(self, request, context):
        c = conn(); cur = c.cursor()
        try:
            cur.execute("SELECT id,name,category,price,stock FROM products ORDER BY id")
            rows = cur.fetchall()
            return db_pb2.ListProductsResp(products=[db_pb2.Product(id=r[0],name=r[1],category=r[2],price=float(r[3]),stock=r[4]) for r in rows])
        finally:
            c.rollback(); put(c)

    def PlaceOrder(self, req, context):
        c = conn(); cur = c.cursor()
        try:
            if req.quantity < 1 or req.quantity > 3:
                context.set_code(StatusCode.INVALID_ARGUMENT)
                context.set_details("quantity must be 1..3")
                return db_pb2.Order()
            cur.execute("SELECT price, stock FROM products WHERE id=%s FOR UPDATE", (req.product_id,))
            row = cur.fetchone()
            if not row:
                context.set_code(StatusCode.NOT_FOUND); context.set_details("product not found"); return db_pb2.Order()
            price, stock = float(row[0]), int(row[1])
            if stock < req.quantity:
                context.set_code(StatusCode.FAILED_PRECONDITION); context.set_details("insufficient stock"); return db_pb2.Order()
            total = price * req.quantity
            cur.execute("UPDATE products SET stock=stock-%s WHERE id=%s", (req.quantity, req.product_id))
            cur.execute(
              "INSERT INTO orders(user_id,product_id,quantity,total_price,status) VALUES(%s,%s,%s,%s,'PLACED') RETURNING id",
              (req.user_id, req.product_id, req.quantity, total)
            )
            oid = cur.fetchone()[0]
            c.commit()
            return db_pb2.Order(id=oid, user_id=req.user_id, product_id=req.product_id, quantity=req.quantity, total_price=total, status=db_pb2.PLACED)
        except Exception as e:
            c.rollback()
            context.set_code(StatusCode.INTERNAL); context.set_details(str(e)); return db_pb2.Order()
        finally:
            put(c)

# 其余 CRUD（GetProduct/CreateUser/GetUser...）按类似模式实现

def serve():
    s = grpc.server(ThreadPoolExecutor(max_workers=16))
    db_pb2_grpc.add_DbServiceServicer_to_server(DbImpl(), s)
    s.add_insecure_port("[::]:50051")
    s.start(); s.wait_for_termination()

if __name__ == "__main__":
    serve()
