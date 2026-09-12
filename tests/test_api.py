import unittest
from unittest.mock import patch

from pyXRocketAPI import Cheque, ChequesList, xPage, xRocketAPIException, xRocketPayAPI
from pyXRocketAPI import api as api_module


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
        client = self.client(Response(data={"status": "ok"}), token=None)
        health = client.health_check()
        self.assertEqual(health.status, "ok")
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
