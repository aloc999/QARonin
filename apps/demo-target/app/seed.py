import random
from datetime import datetime, timedelta, timezone

from . import database as dbmod
from .database import Base, init_engine
from .models import Product, User, Order, OrderItem
from .auth import hash_password

PRODUCTS = [
    {"name": "Katana Letter Opener", "description": "Hand-forged steel letter opener with hamon line.", "price": 49.99, "stock": 25},
    {"name": "Zen Garden Starter Kit", "description": "Miniature raked sand garden with stone set.", "price": 29.50, "stock": 40},
    {"name": "Ronin Tea Set", "description": "Cast iron teapot with two cups, matte black finish.", "price": 74.00, "stock": 12},
    {"name": "Bamboo Bento Box", "description": "Two-tier lacquered bento with cloth wrap.", "price": 38.25, "stock": 33},
    {"name": "Calligraphy Brush Set", "description": "Five brushes of varying weight with ink stone.", "price": 42.00, "stock": 18},
    {"name": "Origami Paper Pack", "description": "200 sheets of washi paper in twelve colors.", "price": 15.75, "stock": 60},
    {"name": "Incense Sampler", "description": "Twelve sticks of cedar, sandalwood and hinoki.", "price": 22.00, "stock": 45},
    {"name": "Lucky Cat Figurine", "description": "Ceramic maneki-neko, left paw raised.", "price": 19.99, "stock": 28},
]

USERS = [
    {"username": "demo", "password": "demo1234", "role": "user"},
    {"username": "admin", "password": "admin1234", "role": "admin"},
]


def seed(db_url: str = "sqlite:///./roninshop.db"):
    engine = init_engine(db_url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    db = dbmod._SessionLocal()
    try:
        for p in PRODUCTS:
            db.add(Product(**p))
        for u in USERS:
            db.add(User(username=u["username"], password_hash=hash_password(u["password"]), role=u["role"]))

        now = datetime.now(timezone.utc)
        order = Order(
            username="demo",
            created_at=now - timedelta(hours=3),
            status="confirmed",
            total=79.24,
        )
        db.add(order)
        db.flush()
        db.add(OrderItem(order_id=order.id, product_id=1, quantity=1, unit_price=49.99))
        db.add(OrderItem(order_id=order.id, product_id=6, quantity=1, unit_price=15.75))
        db.add(OrderItem(order_id=order.id, product_id=8, quantity=1, unit_price=19.99))
        random.seed(20260826)
        db.commit()
    finally:
        db.close()
