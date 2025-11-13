import grpc

import db_pb2
import db_pb2_grpc


def main():
    channel = grpc.insecure_channel("localhost:50051")
    stub = db_pb2_grpc.DbServiceStub(channel)

    # 1) 创建一个用户
    user = stub.CreateUser(
        db_pb2.CreateUserRequest(
            sid="12212345",
            username="haibin",
            email="laihb2022@mail.sustech.edu.cn",
            password_hash="dummy_hash",  # 测试随便写
        )
    )
    print("Created user:", user)

    # 2) 列出所有产品（你可以只用初始 SQL 插入的 3 个）
    products_resp = stub.ListProducts(
        db_pb2.ListProductsRequest(
            page=1,
            page_size=10,
        )
    )
    print("Products:")
    for p in products_resp.products:
        print("  -", p.id, p.name, p.price, p.stock)

    # 3) 给这个用户下一个订单（买第一件商品）
    if products_resp.products:
        first_product = products_resp.products[0]
        order = stub.CreateOrder(
            db_pb2.CreateOrderRequest(
                user_id=user.id,
                product_id=first_product.id,
                quantity=2,
            )
        )
        print("Created order:", order)

        # 再查一下这个用户的订单
        orders_resp = stub.ListOrdersByUser(
            db_pb2.ListOrdersByUserRequest(
                user_id=user.id,
                page=1,
                page_size=10,
            )
        )
        print("Orders of user", user.id)
        for o in orders_resp.orders:
            print("  - order_id:", o.id,
                  "product:", o.product_id,
                  "qty:", o.quantity,
                  "total:", o.total_price)


if __name__ == "__main__":
    main()

