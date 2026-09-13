import unittest
from unittest.mock import patch

from pyXRocketAPI import Cheque, ChequesList, Health, xPage, xRocketAPIException, xRocketPayAPI
from pyXRocketAPI import api as api_module
from pyXRocketAPI.models import (
    ChequeCallback,
    ChequeUrl,
    InvoiceBlockchainTransaction,
    InvoiceCallback,
    InvoiceCustomer,
    InvoiceInternalTransaction,
    InvoiceLinks,
    InvoicePaymentPayer,
    InvoicePaymentTransactionBlockchainDetails,
    InvoiceUrl,
    HealthComponent,
    PayoutCallback,
    WithdrawalCallback,
)


class Response:
    def __init__(self, status_code=200, data=None, text=""):
        self.status_code = status_code
        self._data = data
        self.text = text
        self.content = b"" if data is None else b"json"

    def json(self):
        if isinstance(self._data, Exception):
            raise self._data
        return self._data


class XRocketPayAPITests(unittest.TestCase):
    def setUp(self):
        self.request = patch.object(api_module.requests, "request").start()

    def tearDown(self):
        patch.stopall()

    def client(self, response, token="token"):
        self.request.return_value = response
        return xRocketPayAPI(token=token, timeout=5)

    def test_public_health_requires_no_token(self):
        client = self.client(Response(data={
            "status": "ok",
            "info": [{"name": "database", "status": "up"}],
            "error": [],
            "details": [{"name": "api", "status": "up", "message": "ready"}],
        }), token=None)
        health = client.health_check()
        self.assertIsInstance(health, Health)
        self.assertEqual(health.status, "ok")
        self.assertIsInstance(health.info[0], HealthComponent)
        self.assertIsInstance(health.details[0], HealthComponent)
        self.assertEqual(health.details[0].message, "ready")
        method, url = self.request.call_args.args[:2]
        kwargs = self.request.call_args.kwargs
        self.assertEqual((method, url), ("GET", "https://pay.api.xrocket.exchange/health"))
        self.assertNotIn("Authorization", kwargs["headers"])

    def test_private_request_sends_bearer_token(self):
        client = self.client(Response(data={"id": "app-1", "name": "Demo"}))
        app = client.get_app_info()
        self.assertEqual((app.id, app.name), ("app-1", "Demo"))
        self.assertEqual(self.request.call_args.kwargs["headers"]["Authorization"], "Bearer token")

    def test_invoice_body_preserves_false_and_uses_camel_case(self):
        client = self.client(Response(201, {"id": "invoice-1", "links": {"webLink": "https://pay.example"}}))
        invoice = client.create_invoice(
            price_currency="USDT", price_amount="10.00", client_invoice_id="order-1", is_fee_paid_by_user=False
        )
        self.assertEqual(invoice.links.webLink, "https://pay.example")
        method, url = self.request.call_args.args[:2]
        kwargs = self.request.call_args.kwargs
        self.assertEqual((method, url), ("POST", "https://pay.api.xrocket.exchange/api/v1/invoices"))
        self.assertEqual(kwargs["json"], {
            "priceCurrency": "USDT", "priceAmount": "10.00", "clientInvoiceId": "order-1", "isFeePaidByUser": False,
        })

    def test_invoice_deserializes_all_nested_response_schemas(self):
        client = self.client(Response(data={
            "id": "invoice-1",
            "callback": {"callbackUrl": "https://example.com/webhook", "payload": {"order": "1"}},
            "url": {"successUrl": "https://example.com/success", "cancelUrl": "https://example.com/cancel"},
            "customer": {"id": "customer-1", "telegramUsername": "customer"},
            "links": {"telegramBotLink": "https://t.me/xRocket?start=invoice"},
        }))

        invoice = client.get_invoice_info(invoice_id="invoice-1")

        self.assertIsInstance(invoice.callback, InvoiceCallback)
        self.assertEqual(invoice.callback.payload, {"order": "1"})
        self.assertIsInstance(invoice.url, InvoiceUrl)
        self.assertEqual(invoice.url.successUrl, "https://example.com/success")
        self.assertIsInstance(invoice.customer, InvoiceCustomer)
        self.assertEqual(invoice.customer.telegramUsername, "customer")
        self.assertIsInstance(invoice.links, InvoiceLinks)

    def test_invoice_payment_deserializes_transaction_subschemas(self):
        client = self.client(Response(data={
            "items": [{
                "id": "payment-1", "status": "paid", "payAmount": "2", "payCurrency": "USDT",
                "receiveAmount": "2", "receiveCurrency": "USDT",
                "transactions": [
                    {
                        "id": "internal-1", "status": "confirmed", "type": "internal", "createdAt": "now",
                        "payer": {"telegramId": "123"},
                    },
                    {
                        "id": "blockchain-1", "status": "confirmed", "type": "blockchain", "createdAt": "now",
                        "payer": {"email": "payer@example.com"},
                        "tx": {"network": "TON", "txHash": "hash", "amount": "2", "currency": "USDT", "status": "confirmed"},
                    },
                ],
            }],
            "pagination": {"next": None},
        }))

        payments = client.get_invoice_payments(invoice_id="invoice-1")
        internal, blockchain = payments.items[0].transactions

        self.assertIsInstance(internal, InvoiceInternalTransaction)
        self.assertIsInstance(internal.payer, InvoicePaymentPayer)
        self.assertIsInstance(blockchain, InvoiceBlockchainTransaction)
        self.assertIsInstance(blockchain.payer, InvoicePaymentPayer)
        self.assertIsInstance(blockchain.tx, InvoicePaymentTransactionBlockchainDetails)

    def test_cheque_payout_and_withdrawal_deserialize_callback_subschemas(self):
        client = self.client(Response(data={
            "chequeId": "cheque-1",
            "callback": {"callbackUrl": "https://example.com/cheque", "payload": {"id": "1"}},
            "url": {"successUrl": "https://example.com/success", "cancelUrl": "https://example.com/cancel"},
        }))
        cheque = client.get_cheque_info(cheque_id="cheque-1")

        self.request.return_value = Response(data={
            "payoutId": "payout-1", "callback": {"callbackUrl": "https://example.com/payout", "payload": {"id": "2"}},
        })
        payout = client.get_payout_info(payout_id="payout-1")

        self.request.return_value = Response(data={
            "withdrawalId": "withdrawal-1", "callback": {"callbackUrl": "https://example.com/withdrawal", "payload": {"id": "3"}},
        })
        withdrawal = client.get_withdrawal_info(withdrawal_id="withdrawal-1")

        self.assertIsInstance(cheque.callback, ChequeCallback)
        self.assertIsInstance(cheque.url, ChequeUrl)
        self.assertEqual(cheque.callback.payload, {"id": "1"})
        self.assertIsInstance(payout.callback, PayoutCallback)
        self.assertEqual(payout.callback.payload, {"id": "2"})
        self.assertIsInstance(withdrawal.callback, WithdrawalCallback)
        self.assertEqual(withdrawal.callback.payload, {"id": "3"})

    def test_identifier_methods_validate_before_request(self):
        client = self.client(Response(data={}))
        with self.assertRaisesRegex(ValueError, "invoiceId or clientInvoiceId"):
            client.get_invoice_info()
        self.assertEqual(self.request.call_count, 0)

    def test_payout_and_withdrawal_payloads(self):
        client = self.client(Response(201, {"payoutId": "p-1", "amount": "1.20"}))
        payout = client.payout_funds_to_user(
            target="123", target_type="telegram_user_id", asset="USDT", amount="1.20", client_payout_id="pay-1"
        )
        self.assertEqual(payout.payoutId, "p-1")
        self.assertEqual(self.request.call_args.kwargs["json"]["clientPayoutId"], "pay-1")

        self.request.return_value = Response(201, {"withdrawalId": "w-1", "status": "pending"})
        withdrawal = client.withdrawal_funds(
            client_withdrawal_id="withdraw-1", network="TON", address="UQexample", asset="USDT", amount="2"
        )
        self.assertEqual(withdrawal.withdrawalId, "w-1")
        self.assertEqual(self.request.call_args.kwargs["json"]["clientWithdrawalId"], "withdraw-1")

    def test_problem_details_become_structured_exception(self):
        client = self.client(Response(429, {
            "type": "/api/problems/rate_limit_exceeded", "title": "Too many requests", "status": 429,
            "detail": "Try again later", "instance": "/api/problems/instances/example", "kind": "rate_limit",
        }))
        with self.assertRaises(xRocketAPIException) as raised:
            client.get_app_info()
        error = raised.exception
        self.assertEqual((error.status, error.problem_type, error.kind), (429, "/api/problems/rate_limit_exceeded", "rate_limit"))
        self.assertEqual(str(error), "Try again later")

    def test_lists_and_optional_rate_authorization(self):
        client = self.client(Response(data=[{"currency": "TON", "rate": "2.5"}]))
        rates = client.get_rates("USDT", ["TON"], authorize=False)
        self.assertEqual(rates[0].rate, "2.5")
        self.assertNotIn("Authorization", self.request.call_args.kwargs["headers"])
        self.assertEqual(self.request.call_args.kwargs["params"], {"base": "USDT", "assets": ["TON"]})

    def test_cheques_list_deserializes_items_and_pagination(self):
        client = self.client(Response(data={
            "items": [{"chequeId": "cheque-1", "asset": "USDT", "state": "active"}],
            "pagination": {"total": 1, "next": "next-page"},
        }))
        cheques = client.get_cheques_list()
        self.assertIsInstance(cheques, ChequesList)
        self.assertIsInstance(cheques, xPage)
        self.assertIsInstance(cheques.items[0], Cheque)
        self.assertEqual(cheques.items[0].chequeId, "cheque-1")
        self.assertEqual(cheques.pagination.next, "next-page")


if __name__ == "__main__":
    unittest.main()
