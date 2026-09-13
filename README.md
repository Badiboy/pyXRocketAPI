[![PyPi Package Version](https://img.shields.io/pypi/v/pyXRocketAPI.svg)](https://pypi.python.org/pypi/pyXRocketAPI)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pyXRocketAPI.svg)](https://pypi.python.org/pypi/pyXRocketAPI)
[![PyPi downloads](https://img.shields.io/pypi/dm/pyXRocketAPI.svg)](https://pypi.org/project/pyXRocketAPI/)

# <p align="center">pyXRocketAPI</p>

**pyXRocketAPI** is a Python client for the [xRocket Pay API](https://docs.xrocket.exchange/api/pay/pay-api-overview). It supports application information, balances, invoices, cheques, payouts, withdrawals, currency rates, and health checks.

## Installation

```shell
pip install pyXRocketAPI
```

## Quick start

```python
from pyXRocketAPI import xRocketPayAPI

client = xRocketPayAPI(token="your-pay-api-token")
invoice = client.create_invoice(price_currency="USDT", price_amount="10.00")
print(invoice.id, invoice.links.web_link)
```

For integration testing, use the xRocket testnet instead of production:

```python
client = xRocketPayAPI(token="testnet-token", testnet=True)
```

## Nested request models

Known nested API objects are passed as model instances, not dictionaries. The
same models deserialize API responses and implement `to_dict()` for request
bodies.

```python
from pyXRocketAPI import InvoiceCallback, InvoiceCustomer, InvoiceUrl, xRocketPayAPI

client = xRocketPayAPI(token="your-pay-api-token")
invoice = client.create_invoice(
    price_currency="USDT",
    price_amount="10.00",
    callback=InvoiceCallback(
        callbackUrl="https://example.com/webhooks/invoice",
        payload={"order_id": "123"},
    ),
    url=InvoiceUrl(
        successUrl="https://example.com/success",
        cancelUrl="https://example.com/cancel",
    ),
    customer=InvoiceCustomer(
        id="customer-123",
        email="customer@example.com",
        telegramId="123456789",
    ),
    data={"internal_order_id": "123"},
)
```

`payload` and `data` remain ordinary dictionaries because xRocket defines them
as arbitrary JSON objects without a fixed schema. Use `MassPayout` instances
for every item passed to `create_mass_payouts()`.

## Safety

The token grants access to the application and must not be committed to source control. Financial POST operations are not retried automatically. Supply and retain the relevant client identifier (`client_invoice_id`, `client_payout_id`, `client_cheque_id`, or `client_withdrawal_id`) so that a timed-out operation can be reconciled safely.

Errors from the API raise `xRocketAPIException`; its `problem_type`, `kind`, `status`, and `instance` attributes expose the RFC 9457 error response.

_AI-supported creation._
