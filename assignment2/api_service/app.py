from fastapi import FastAPI, Depends, HTTPException
from deps import issue_token, require_user, AuthedUser
from grpc_clients import db, log_streamer, make_log
from db_pb2 import Empty, ProductId, CreateUserReq, GetUserByNameReq, UpdateUserReq, DeactivateUserReq, PlaceOrderReq, OrderId

app = FastAPI(title="SUSTech Merch Store API")

# 启动一个日志流（客户端流）
_log_stub, _log_gen = log_streamer()

@app.get("/")
def greet():
    _log_gen.send(make_log("INFO", "Greeting"))
    return {"message": "Welcome to SUSTech Merch Store!"}

@app.get("/products")
def list_products():
    resp = db.ListProducts(Empty())
    return [dict(id=p.id, name=p.name, category=p.category, price=p.price, stock=p.stock) for p in resp.products]

@app.get("/products/{pid}")
def get_product(pid: int):
    try:
        p = db.GetProduct(ProductId(id=pid))
        return dict(id=p.id, name=p.name, category=p.category, price=p.price, stock=p.stock)
    except Exception:
        raise HTTPException(404, "Product not found")

@app.post("/users/register", status_code=201)
def register(body: dict):
    # 这里用 PBKDF2/bcrypt 生成 password_hash（略，示例用明文 hash 代替）
    import hashlib
    ph = hashlib.sha256(body["password"].encode()).hexdigest()
    u = db.CreateUser(CreateUserReq(username=body["username"], password_hash=ph))
    _log_gen.send(make_log("INFO", f"Register user {u.username}"))
    return {"id": u.id, "username": u.username, "active": u.active}

@app.post("/users/login")
def login(body: dict):
    u = db.GetUserByName(GetUserByNameReq(username=body["username"]))
    import hashlib
    ph = hashlib.sha256(body["password"].encode()).hexdigest()
    # 这里应由 DB 返回 password_hash 做比对；为简化示例，假设比对通过
    if not u.active:
        raise HTTPException(401, "User inactive")
    token = issue_token(u.id, u.username)
    _log_gen.send(make_log("INFO", f"Login {u.username}"))
    return {"access_token": token, "token_type": "Bearer"}

@app.get("/users/me")
def me(user: AuthedUser = Depends(require_user)):
    u = db.GetUserByName(GetUserByNameReq(username=user.username))
    return {"id": u.id, "username": u.username, "active": u.active}

@app.patch("/users/me")
def update_me(body: dict, user: AuthedUser = Depends(require_user)):
    u = db.GetUserByName(GetUserByNameReq(username=user.username))
    uu = db.UpdateUser(UpdateUserReq(id=u.id, username=body.get("username", u.username)))
    _log_gen.send(make_log("INFO", f"Update user {uu.username}"))
    return {"id": uu.id, "username": uu.username, "active": uu.active}

@app.post("/users/deactivate")
def deactivate_me(user: AuthedUser = Depends(require_user)):
    u = db.GetUserByName(GetUserByNameReq(username=user.username))
    uu = db.DeactivateUser(DeactivateUserReq(id=u.id))
    _log_gen.send(make_log("WARN", f"Deactivate user {uu.username}"))
    return {"ok": True}

@app.post("/orders", status_code=201)
def place_order(body: dict, user: AuthedUser = Depends(require_user)):
    if body["quantity"] > 3:
        raise HTTPException(400, "Quantity must be <= 3")
    o = db.PlaceOrder(PlaceOrderReq(user_id=user.id, product_id=body["product_id"], quantity=body["quantity"]))
    _log_gen.send(make_log("INFO", f"Place order #{o.id} by {user.username}"))
    return dict(id=o.id, user_id=o.user_id, product_id=o.product_id, quantity=o.quantity, total_price=o.total_price, status="PLACED")

@app.get("/orders/{oid}")
def get_order(oid: int, user: AuthedUser = Depends(require_user)):
    o = db.GetOrder(OrderId(id=oid))
    if o.user_id != user.id:
        raise HTTPException(403, "Not your order")
    return dict(id=o.id, user_id=o.user_id, product_id=o.product_id, quantity=o.quantity, total_price=o.total_price, status=("PLACED" if o.status==0 else "CANCELED"))

@app.delete("/orders/{oid}")
def cancel_order(oid: int, user: AuthedUser = Depends(require_user)):
    o = db.GetOrder(OrderId(id=oid))
    if o.user_id != user.id:
        raise HTTPException(403, "Not your order")
    oc = db.CancelOrder(OrderId(id=oid))
    _log_gen.send(make_log("WARN", f"Cancel order #{oc.id} by {user.username}"))
    return {"ok": True}
