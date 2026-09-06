# AutomationExercise parity (https://automationexercise.com/test_cases)

Two layers:

1. **Live** (`AE_LIVE=1`, default on): fetches the reference `test_cases` page
   and asserts cases 1-26 are published (AE-7), plus home/products/login return
   200. Skips gracefully offline — never a merge gate, nightly only.
2. **Parity** (offline, always): mirrors every AE case that has a RoninShop
   analogue via TestClient. Gaps are recorded, not hidden.

```bash
pip install -r frameworks/automationexercise/requirements.txt
python -m pytest frameworks/automationexercise/tests -q   # or: make ae-test
AE_LIVE=0 python -m pytest frameworks/automationexercise/tests -q  # offline only
```

## Full 26-case mapping

| AE | Title | RoninShop analogue | Status |
|----|-------|--------------------|--------|
| 1 | Register User | seed demo/admin (registration UI out of scope) | live check |
| 2 | Login correct | POST /api/auth/login demo/demo1234 | parity test |
| 3 | Login incorrect | POST login wrong pw -> 401 / UI error box | parity test |
| 4 | Logout User | logout clears localStorage token; bad token -> 401 | parity test |
| 5 | Register existing email | seed conflict note | live check |
| 6 | Contact Us Form | out of scope | live check |
| 7 | Verify Test Cases Page | this suite (page lists 1-26) | live test |
| 8 | All Products + detail | GET /api/products + /{id} name/price/stock | parity test |
| 9 | Search Product | search out of scope | live check |
| 10 | Subscription home | out of scope | live check |
| 11 | Subscription cart | out of scope | live check |
| 12 | Add Products in Cart | order 2 products, totals verified | parity test |
| 13 | Verify quantity in cart | order qty=4, total = price*4 | parity test |
| 14 | Place Order: register while checkout | e2e-purchase spec | TS spec |
| 15 | Place Order: register before checkout | seed + order flow | parity note |
| 16 | Place Order: login before checkout | login -> order -> fetch order | parity test |
| 17 | Remove Products From Cart | order unknown product -> 404 | parity test |
| 18 | View Category Products | categories out of scope | live check |
| 19 | View & Cart Brand Products | brands out of scope | live check |
| 20 | Search + cart after login | search gap; cart-after-login via storageState | TS setup |
| 21 | Add review on product | reviews out of scope | live check |
| 22 | Add to cart from Recommended | add-to-cart badge flow | TS smoke |
| 23 | Address details in checkout | order username/address analogue | parity note |
| 24 | Download Invoice after order | order created_at/total analogue | parity note |
| 25 | Scroll Up (arrow) / Down | out of scope | live check |
| 26 | Scroll Up (no arrow) / Down | out of scope | live check |

Traceability: docs/QMS/TRACEABILITY-MATRIX.md.
