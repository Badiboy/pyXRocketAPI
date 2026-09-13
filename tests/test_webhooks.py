import hashlib
import hmac
import json
import unittest

from pyXRocketAPI import (
    Cheque,
    ChequeWebhook,
    Invoice,
    Payout,
    PayoutWebhook,
    PaymentStatusChangedWebhook,
    UnknownWebhook,
    Withdrawal,
    WithdrawalWebhook,
    parse_and_verify_webhook,
    parse_webhook,
    xRocketWebhookParseException,
    xRocketWebhookSignatureException,
)
from pyXRocketAPI.models import InvoicePayment


WEBHOOK_SECRET = "webhook-secret"
SIGNATURE_TIMESTAMP = "1735689600000"


def signed_webhook(payload):
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    signature = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        SIGNATURE_TIMESTAMP.encode("utf-8") + b"." + body,
        hashlib.sha256,
    ).hexdigest()
    return body, {
        "signature-timestamp": SIGNATURE_TIMESTAMP,
        "signature-version": "v1",
        "signature": signature,
    }


class XRocketWebhookTests(unittest.TestCase):
    def test_parses_and_verifies_payment_status_changed_webhook(self):
        body, headers = signed_webhook({
            "id": "delivery-1",
            "timestamp": "2025-01-01T00:00:00.000Z",
            "type": "invoice",
            "data": {
                "event": "payment_status_changed",
                "invoice": {"id": "invoice-1", "status": "paid"},
                "payment": {"id": "payment-1", "status": "paid", "finalizedAt": "2025-01-01T00:00:00.000Z"},
            },
        })

        event = parse_and_verify_webhook(body, headers, WEBHOOK_SECRET)

        self.assertIsInstance(event, PaymentStatusChangedWebhook)
        self.assertEqual(event.id, "delivery-1")
        self.assertIsInstance(event.data.invoice, Invoice)
        self.assertIsInstance(event.data.payment, InvoicePayment)
        self.assertEqual(event.data.payment.status, "paid")

    def test_rejects_invalid_signature_before_parsing(self):
        body, headers = signed_webhook({"id": "delivery-1", "timestamp": "now", "type": "payout", "data": {}})

        with self.assertRaises(xRocketWebhookSignatureException):
            parse_and_verify_webhook(body + b" ", headers, WEBHOOK_SECRET)

    def test_returns_unknown_webhook_for_future_type_and_invoice_event(self):
        future_type = parse_webhook({
            "id": "delivery-1", "timestamp": "now", "type": "future_type", "data": {"value": 1},
        })
        future_invoice_event = parse_webhook({
            "id": "delivery-2", "timestamp": "now", "type": "invoice", "data": {"event": "future_event"},
        })

        self.assertIsInstance(future_type, UnknownWebhook)
        self.assertEqual(future_type.data, {"value": 1})
        self.assertIsInstance(future_invoice_event, UnknownWebhook)
        self.assertEqual(future_invoice_event.data["event"], "future_event")

    def test_parses_other_documented_webhook_types(self):
        cases = (
            ("cheque", {"chequeId": "cheque-1"}, ChequeWebhook, Cheque),
            ("payout", {"payoutId": "payout-1"}, PayoutWebhook, Payout),
            ("withdrawal", {"withdrawalId": "withdrawal-1"}, WithdrawalWebhook, Withdrawal),
        )

        for webhook_type, data, webhook_class, data_class in cases:
            with self.subTest(webhook_type=webhook_type):
                event = parse_webhook({
                    "id": "delivery-1", "timestamp": "now", "type": webhook_type, "data": data,
                })
                self.assertIsInstance(event, webhook_class)
                self.assertIsInstance(event.data, data_class)

    def test_rejects_malformed_webhook_envelope(self):
        with self.assertRaises(xRocketWebhookParseException):
            parse_webhook(b"not json")
        with self.assertRaises(xRocketWebhookParseException):
            parse_webhook({"id": "delivery-1", "timestamp": "now", "type": "payout"})


if __name__ == "__main__":
    unittest.main()
