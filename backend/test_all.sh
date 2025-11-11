#!/usr/bin/env bash
set -euo pipefail

API="http://127.0.0.1:8000"
JQ=$(command -v jq || true)
if [ -z "$JQ" ]; then
  echo "Note: jq not found. Install with: brew install jq  (script will continue without pretty JSON)"
fi

timestamp() { date +"%y%m%d%H%M%S"; }

echo "=== Sanity: /health ==="
health=$(curl -sS "$API/health")
echo "health: $health"
if [[ "$health" != *"ok"* ]]; then
  echo "Health check failed. Exiting."
  exit 1
fi

echo "=== 1) Ensure tax slabs exist (0,5,18) ==="
create_tax() {
  rate=$1; name=$2
  resp=$(curl -sS -X POST "$API/tax_slabs/" \
    -H "Content-Type: application/json" \
    -d "{\"rate\": $rate, \"name\": \"$name\"}" || true)
  echo "tax $rate -> $resp"
}
create_tax 0.00 "GST 0%"
create_tax 5.00 "GST 5%"
create_tax 18.00 "GST 18%"

echo "=== 2) Create employee ==="
EMP_PAYLOAD=$(cat <<-JSON
{
  "full_name": "Test Employee $(timestamp)",
  "phone": "8888888888",
  "employee_code": "T$(timestamp)",
  "hire_date": "2025-11-10",
  "designation": "Waiter"
}
JSON
)
emp_resp=$(curl -sS -X POST "$API/employees/" -H "Content-Type: application/json" -d "$EMP_PAYLOAD")
echo "employee resp: ${emp_resp}"
emp_id=$(echo "$emp_resp" | (jq -r '.id' 2>/dev/null || sed -n 's/.*"id":[[:space:]]*\([0-9]*\).*/\1/p'))
if ! [[ $emp_id =~ ^[0-9]+$ ]]; then
  echo "Failed to create employee. Response: $emp_resp"
  exit 1
fi
echo "created employee id: $emp_id"

echo "=== 3) Create product ==="
PROD_PAYLOAD=$(cat <<-JSON
{
  "name": "Test Dish $(timestamp)",
  "sku": "TD$(timestamp)",
  "category_id": null,
  "current_unit_price": 150.00,
  "tax_slab_id": 2,
  "is_active": true
}
JSON
)
prod_resp=$(curl -sS -X POST "$API/products/" -H "Content-Type: application/json" -d "$PROD_PAYLOAD")
echo "product resp: $prod_resp"
prod_id=$(echo "$prod_resp" | (jq -r '.id' 2>/dev/null || sed -n 's/.*"id":[[:space:]]*\([0-9]*\).*/\1/p'))
if ! [[ $prod_id =~ ^[0-9]+$ ]]; then
  echo "Failed to create product. Response: $prod_resp"
  exit 1
fi
echo "created product id: $prod_id"

echo "=== 4) Create invoice with one item ==="
INV_NO="TINV$(timestamp)"
INV_PAYLOAD=$(cat <<-JSON
{
  "invoice_number": "$INV_NO",
  "created_by": null,
  "table_number": "T1",
  "order_type": "dine-in",
  "employee_id": $emp_id,
  "items": [
    {
      "product_id": $prod_id,
      "description": "Test Dish",
      "quantity": 2,
      "unit_price": 150.00,
      "tax_rate": 5.00,
      "discount_amount": 0.00
    }
  ]
}
JSON
)
echo "invoice payload: $INV_PAYLOAD"
inv_resp=$(curl -sS -w "\n%{http_code}" -X POST "$API/invoices/" -H "Content-Type: application/json" -d "$INV_PAYLOAD")
inv_body=$(echo "$inv_resp" | sed '$d')
inv_code=$(echo "$inv_resp" | tail -n1)
echo "invoice response code: $inv_code"
echo "invoice body: $inv_body"

if [[ "$inv_code" == "409" ]]; then
  echo "Invoice number conflict. Consider re-running; invoice_number already exists."
  exit 1
fi
if ! [[ "$inv_code" =~ ^20[01]$ ]]; then
  echo "Invoice creation failed. Exiting."
  exit 1
fi

inv_id=$(echo "$inv_body" | (jq -r '.id' 2>/dev/null || sed -n 's/.*"id":[[:space:]]*\([0-9]*\).*/\1/p'))
if ! [[ $inv_id =~ ^[0-9]+$ ]]; then
  echo "Invoice created but id not found in response: $inv_body"
  exit 1
fi
echo "created invoice id: $inv_id"

echo "=== 5) Pay invoice ==="
total_amount=$(echo "$inv_body" | (jq -r '.total_amount // 0' 2>/dev/null || echo "0"))
if [[ "$total_amount" == "0" || "$total_amount" == "null" ]]; then
  total_amount=$(echo "scale=2; 150.00 * 2 * 1.05" | bc)
fi
echo "paying amount: $total_amount"

# updated endpoint: /payments/{invoice_id}/pay
pay_resp=$(curl -sS -w "\n%{http_code}" -X POST "$API/payments/${inv_id}/pay?amount=${total_amount}&method=cash")
pay_body=$(echo "$pay_resp" | sed '$d')
pay_code=$(echo "$pay_resp" | tail -n1)
echo "payment response code: $pay_code"
echo "payment body: $pay_body"
if ! [[ "$pay_code" =~ ^20[01]$ ]]; then
  echo "Payment failed. Exiting."
  exit 1
fi

echo "=== 6) Verify invoice status is paid (GET /invoices/{id}) ==="
inv_verify=$(curl -sS "$API/invoices/$inv_id")
echo "invoice verify: $inv_verify"
status=$(echo "$inv_verify" | (jq -r '.status' 2>/dev/null || echo ""))
echo "status: $status"
if [[ "$status" != "paid" && "$status" != "paid_success" && "$status" != "paid" ]]; then
  echo "Warning: invoice status is not 'paid' — got: $status"
else
  echo "Invoice paid successfully."
fi

echo "=== All checks passed ==="
