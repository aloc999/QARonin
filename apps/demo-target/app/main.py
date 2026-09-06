import random
import time
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import get_session
from .models import Product, Order, OrderItem
from .auth import create_token, verify_token, TokenError, authenticate_user
from .seed import seed

app = FastAPI(title="RoninShop", version="1.0.0")
_BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=_BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(_BASE_DIR / "templates"))


@app.on_event("startup")
def on_startup():
    seed()


class LoginRequest(BaseModel):
    username: str
    password: str


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = 1


class OrderCreate(BaseModel):
    items: list[OrderItemIn]


def get_current_user(request: Request) -> dict:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    try:
        return verify_token(auth.removeprefix("Bearer ").strip())
    except TokenError as e:
        raise HTTPException(status_code=401, detail=str(e))


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user


# ---------- UI ----------


@app.get("/", response_class=HTMLResponse)
def index():
    return RedirectResponse(url="/products")


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/products", response_class=HTMLResponse)
def products_page(request: Request):
    db = next(get_session())
    products = db.query(Product).all()
    return templates.TemplateResponse("products.html", {"request": request, "products": products})


@app.get("/cart", response_class=HTMLResponse)
def cart_page(request: Request):
    return templates.TemplateResponse("cart.html", {"request": request})


# ---------- API ----------


@app.post("/api/auth/login")
def api_login(body: LoginRequest, db: Session = Depends(get_session)):
    user = authenticate_user(db, body.username, body.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "access_token": create_token(user.username, user.role),
        "token_type": "bearer",
        "username": user.username,
        "role": user.role,
    }


@app.get("/api/products")
def list_products(db: Session = Depends(get_session)):
    return [
        {"id": p.id, "name": p.name, "description": p.description, "price": p.price, "stock": p.stock}
        for p in db.query(Product).all()
    ]


@app.get("/api/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_session)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if p is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"id": p.id, "name": p.name, "description": p.description, "price": p.price, "stock": p.stock}


@app.post("/api/orders", status_code=201)
def create_order(
    body: OrderCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    if not body.items:
        raise HTTPException(status_code=422, detail="Order must contain at least one item")

    order = Order(username=user["sub"], total=0.0)
    total = 0.0
    for item in body.items:
        p = db.query(Product).filter(Product.id == item.product_id).first()
        if p is None:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if p.stock < item.quantity or item.quantity < 1:
            raise HTTPException(
                status_code=409,
                detail=f"Insufficient stock for product {p.id} (requested {item.quantity}, available {p.stock})",
            )
        line_total = p.price * item.quantity
        total += line_total
        p.stock -= item.quantity
        order.items.append(OrderItem(product_id=p.id, quantity=item.quantity, unit_price=p.price))
    order.total = round(total, 2)
    order.items_json = "[]"
    db.add(order)
    db.commit()
    db.refresh(order)
    return {
        "id": order.id,
        "username": order.username,
        "status": order.status,
        "total": order.total,
        "created_at": order.created_at.isoformat(),
        "items": [
            {"product_id": i.product_id, "quantity": i.quantity, "unit_price": i.unit_price}
            for i in order.items
        ],
    }


@app.get("/api/orders/{order_id}")
def get_order(
    order_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.username != user["sub"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not your order")
    return {
        "id": order.id,
        "username": order.username,
        "status": order.status,
        "total": order.total,
        "created_at": order.created_at.isoformat(),
        "items": [
            {"product_id": i.product_id, "quantity": i.quantity, "unit_price": i.unit_price}
            for i in db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        ],
    }


@app.get("/api/admin/orders")
def admin_orders(user: dict = Depends(require_admin), db: Session = Depends(get_session)):
    orders = db.query(Order).all()
    return {
        "count": len(orders),
        "orders": [
            {"id": o.id, "username": o.username, "status": o.status, "total": o.total}
            for o in orders
        ],
    }


@app.get("/api/flaky")
def flaky_endpoint():
    if random.random() < 0.30:
        raise HTTPException(status_code=503, detail="Transient failure (simulated)")
    return {"status": "ok", "ts": time.time()}


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "roninshop", "version": app.version}


@app.get("/metrics")
def metrics():
    # Minimal Prometheus exposition (no extra deps): process + app counters.
    lines = [
        "# HELP roninshop_up 1 when the app serves traffic",
        "# TYPE roninshop_up gauge",
        "roninshop_up 1",
        "# HELP roninshop_build_info Build metadata",
        "# TYPE roninshop_build_info gauge",
        f'roninshop_build_info{{version="{app.version}"}} 1',
    ]
    from fastapi.responses import PlainTextResponse

    return PlainTextResponse("\n".join(lines) + "\n", media_type="text/plain; version=0.0.4")
