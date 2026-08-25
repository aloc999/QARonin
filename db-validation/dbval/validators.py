"""Data validators proving UI/API claims against the database."""

from sqlalchemy import text


def order_integrity(session) -> list[str]:
    """Every order's stored total must equal SUM(quantity * unit_price)."""
    violations = []
    rows = session.execute(text("""
        SELECT o.id, o.total,
               COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS computed
        FROM orders o
        LEFT JOIN order_items oi ON oi.order_id = o.id
        GROUP BY o.id, o.total
    """)).fetchall()
    for order_id, stored, computed in rows:
        if abs(float(stored or 0.0) - float(computed)) > 0.005:
            violations.append(
                f"order {order_id}: stored total {stored} != line-item sum {computed}"
            )
    return violations


def referential_integrity(session) -> list[str]:
    """No orphan foreign keys anywhere."""
    violations = []
    checks = [
        ("order_items.order_id", """
            SELECT COUNT(*) FROM order_items oi
            LEFT JOIN orders o ON o.id = oi.order_id
            WHERE o.id IS NULL"""),
        ("order_items.product_id", """
            SELECT COUNT(*) FROM order_items oi
            LEFT JOIN products p ON p.id = oi.product_id
            WHERE p.id IS NULL"""),
    ]
    for label, sql in checks:
        count = session.execute(text(sql)).scalar()
        if count:
            violations.append(f"{label}: {count} orphaned rows")
    return violations


def seeded_data_quality(session, min_products: int = 8) -> list[str]:
    """Row counts, null checks and value-domain constraints on seed data."""
    violations = []
    product_count = session.execute(text("SELECT COUNT(*) FROM products")).scalar()
    if product_count < min_products:
        violations.append(
            f"products table has {product_count} rows, expected >= {min_products}"
        )
    user_count = session.execute(text("SELECT COUNT(*) FROM users")).scalar()
    if user_count < 2:
        violations.append(f"users table has {user_count} rows, expected >= 2")

    null_checks = [
        ("products.name", "SELECT COUNT(*) FROM products WHERE name IS NULL OR name = ''"),
        ("products.price", "SELECT COUNT(*) FROM products WHERE price IS NULL"),
        ("users.username", "SELECT COUNT(*) FROM users WHERE username IS NULL OR username = ''"),
        ("users.password_hash", "SELECT COUNT(*) FROM users WHERE password_hash IS NULL"),
    ]
    for column, sql in null_checks:
        count = session.execute(text(sql)).scalar()
        if count:
            violations.append(f"{column}: {count} null/empty values")

    domain_checks = [
        ("products.price", "SELECT COUNT(*) FROM products WHERE price <= 0"),
        ("products.stock", "SELECT COUNT(*) FROM products WHERE stock < 0"),
        ("order_items.quantity", "SELECT COUNT(*) FROM order_items WHERE quantity < 1"),
        (
            "users.role",
            "SELECT COUNT(*) FROM users WHERE role NOT IN ('user', 'admin')",
        ),
        (
            "orders.status",
            "SELECT COUNT(*) FROM orders WHERE status NOT IN ('confirmed')",
        ),
    ]
    for column, sql in domain_checks:
        count = session.execute(text(sql)).scalar()
        if count:
            violations.append(f"{column}: {count} out-of-domain values")
    return violations
