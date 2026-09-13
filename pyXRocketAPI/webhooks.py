"""Verification and parsing of xRocket Pay webhooks.

API: https://docs.xrocket.exchange/api/pay/pay-api-overview

This module does not receive HTTP requests and does not depend on Flask,
FastAPI, Django, or another web framework. Pass the request body and headers
from the HTTP layer that your application already uses.

Always verify a webhook before parsing or acting on it. The verifier requires
the original request body, preferably as ``bytes``. Do not pass a JSON object
that was decoded and serialized again: whitespace, field order, or escaping
can change and invalidate the signature.

For applications using the current xRocket Pay API, xRocket sends these
headers:

* ``Signature-Timestamp``: Unix timestamp in milliseconds when the webhook was sent.
* ``Signature-Version``: Signature scheme version. The current value is ``v1``.
* ``Signature``: hexadecimal HMAC-SHA-256 signature.

For version ``v1``, the signed byte sequence is::
    {Signature-Timestamp}.{raw request body}

The application's webhook secret is the HMAC key without transformations.
Header names are compared case-insensitively. The legacy
``Rocket-Pay-Signature`` header is intentionally unsupported because it does
not use the current signature scheme.

Use :func:`parse_and_verify_webhook` for the usual case::
    event = parse_and_verify_webhook(
        raw_body=request.body,
        headers=request.headers,
        webhook_secret=WEBHOOK_SECRET,
    )

The returned object is one of :class:`InvoiceStatusChangedWebhook`,
:class:`PaymentStatusChangedWebhook`, :class:`ChequeWebhook`,
:class:`PayoutWebhook`, :class:`WithdrawalWebhook`, or
:class:`UnknownWebhook`.

The top-level webhook ``id`` identifies a delivery and remains stable across
retries. Persist and deduplicate this value in application storage before an
irreversible business action. Idempotency storage is deliberately outside this
library because its implementation depends on the application's database and
transaction rules.

xRocket can add new event and status values without notice. Unknown webhook
types or invoice event values become :class:`UnknownWebhook` instead of an
exception, so an application can log and safely ignore them. Invalid JSON,
missing required envelope fields, or an invalid signature are errors.

When a payment completes an invoice, xRocket sends both
``payment_status_changed`` and ``invoice_status_changed``. Delivery order is
not guaranteed, including after retries. Process each event independently.
Track successful payments only when ``event`` is
``payment_status_changed`` and ``event.data.payment.status`` is ``paid``;
track invoice completion only when ``event`` is
``invoice_status_changed`` and ``event.data.invoice.status`` is ``paid``.
Payment finality is indicated by ``event.data.payment.finalizedAt`` not being
``None``, rather than by relying on one fixed status value.

AI generated. Manually validated.
"""

import hashlib
import hmac
import json
from collections.abc import Mapping
from typing import Any

from .exceptions import (
    xRocketWebhookParseException,
    xRocketWebhookSignatureException,
    xRocketWebhookUnsupportedVersionException,
)
from .models import Cheque, Invoice, InvoicePayment, Payout, Withdrawal, xRocketObject


# noinspection method-overriding
class xRocketWebhook(xRocketObject):
    """Base model for an xRocket webhook delivery.

    API: https://docs.xrocket.exchange/api/pay/pay-api-overview

    :param id: Unique webhook delivery id, can be used by the receiver for
        idempotency.
    :param timestamp: When webhook was sent.
    :param type: Webhook type.
    :param data: Typed webhook payload.
    """

    def __init__(self):
        self.id = None
        self.timestamp = None
        self.type = None
        self.data = None

    @classmethod
    def de_json(cls, json_dict):
        """Create a webhook model from its parsed envelope dictionary.

        :param json_dict: Parsed webhook envelope.
        :return: ``xRocketWebhook``.
        """
        data = cls.check_json(json_dict)
        return super(xRocketWebhook, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class InvoiceStatusChangedWebhookData(xRocketObject):
    """Payload of an ``invoice_status_changed`` webhook.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-create-invoice

    :param event: Event type. This value is ``invoice_status_changed``.
    :param invoice: Updated invoice.
    """

    def __init__(self):
        self.event = None
        self.invoice = None

    @classmethod
    def de_json(cls, json_dict):
        """Create the payload from a parsed webhook dictionary.

        :param json_dict: Parsed invoice-status-changed payload.
        :return: ``InvoiceStatusChangedWebhookData``.
        """
        data = cls.check_json(json_dict)
        instance = super(InvoiceStatusChangedWebhookData, cls).de_json(data, process_mode=2)
        instance.invoice = Invoice.de_json(instance.invoice)
        return instance


# noinspection method-overriding
class PaymentStatusChangedWebhookData(xRocketObject):
    """Payload of a ``payment_status_changed`` webhook.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-create-invoice

    :param event: Event type. This value is ``payment_status_changed``.
    :param invoice: Updated invoice.
    :param payment: Payment received for the invoice or whose status changed.
    """

    def __init__(self):
        self.event = None
        self.invoice = None
        self.payment = None

    @classmethod
    def de_json(cls, json_dict):
        """Create the payload from a parsed webhook dictionary.

        :param json_dict: Parsed payment-status-changed payload.
        :return: ``PaymentStatusChangedWebhookData``.
        """
        data = cls.check_json(json_dict)
        instance = super(PaymentStatusChangedWebhookData, cls).de_json(data, process_mode=2)
        instance.invoice = Invoice.de_json(instance.invoice)
        instance.payment = InvoicePayment.de_json(instance.payment)
        return instance


# noinspection method-overriding
class InvoiceStatusChangedWebhook(xRocketWebhook):
    """Invoice webhook reporting an invoice status transition.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-create-invoice

    :param id: Unique webhook delivery id, can be used by the receiver for idempotency.
    :param timestamp: When webhook was sent.
    :param type: Webhook type. This value is ``invoice``.
    :param data: ``InvoiceStatusChangedWebhookData`` payload.
    """

    @classmethod
    def de_json(cls, json_dict):
        """Create the webhook from a parsed envelope dictionary.

        :param json_dict: Parsed invoice webhook envelope.
        :return: ``InvoiceStatusChangedWebhook``.
        """
        data = cls.check_json(json_dict)
        instance = super(InvoiceStatusChangedWebhook, cls).de_json(data)
        instance.data = InvoiceStatusChangedWebhookData.de_json(instance.data)
        return instance


# noinspection method-overriding
class PaymentStatusChangedWebhook(xRocketWebhook):
    """Invoice webhook reporting a received payment or payment status change.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-create-invoice

    :param id: Unique webhook delivery id, can be used by the receiver for idempotency.
    :param timestamp: When webhook was sent.
    :param type: Webhook type. This value is ``invoice``.
    :param data: ``PaymentStatusChangedWebhookData`` payload.
    """

    @classmethod
    def de_json(cls, json_dict):
        """Create the webhook from a parsed envelope dictionary.

        :param json_dict: Parsed invoice webhook envelope.
        :return: ``PaymentStatusChangedWebhook``.
        """
        data = cls.check_json(json_dict)
        instance = super(PaymentStatusChangedWebhook, cls).de_json(data)
        instance.data = PaymentStatusChangedWebhookData.de_json(instance.data)
        return instance


class ChequeWebhook(xRocketWebhook):
    """Webhook reporting an update to a cheque.

    API: https://docs.xrocket.exchange/api/pay/reference/http/cheque-controller-create-cheque

    :param id: Unique webhook delivery id, can be used by the receiver for idempotency.
    :param timestamp: When webhook was sent.
    :param type: Webhook type. This value is ``cheque``.
    :param data: Updated ``Cheque``.
    """

    @classmethod
    def de_json(cls, json_dict):
        """Create the webhook from a parsed envelope dictionary.

        :param json_dict: Parsed cheque webhook envelope.
        :return: ``ChequeWebhook``.
        """
        data = cls.check_json(json_dict)
        instance = super(ChequeWebhook, cls).de_json(data)
        instance.data = Cheque.de_json(instance.data)
        return instance


class PayoutWebhook(xRocketWebhook):
    """Webhook reporting a payout status update.

    API: https://docs.xrocket.exchange/api/pay/reference/http/payout-controller-payout

    :param id: Unique webhook delivery id, can be used by the receiver for idempotency.
    :param timestamp: When webhook was sent.
    :param type: Webhook type. This value is ``payout``.
    :param data: Updated ``Payout``.
    """

    @classmethod
    def de_json(cls, json_dict):
        """Create the webhook from a parsed envelope dictionary.

        :param json_dict: Parsed payout webhook envelope.
        :return: ``PayoutWebhook``.
        """
        data = cls.check_json(json_dict)
        instance = super(PayoutWebhook, cls).de_json(data)
        instance.data = Payout.de_json(instance.data)
        return instance


class WithdrawalWebhook(xRocketWebhook):
    """Webhook reporting a withdrawal status update.

    API: https://docs.xrocket.exchange/api/pay/reference/http/withdrawal-controller-create-withdrawal

    :param id: Unique webhook delivery id, can be used by the receiver for idempotency.
    :param timestamp: When webhook was sent.
    :param type: Webhook type. This value is ``withdrawal``.
    :param data: Updated ``Withdrawal``.
    """

    @classmethod
    def de_json(cls, json_dict):
        """Create the webhook from a parsed envelope dictionary.

        :param json_dict: Parsed withdrawal webhook envelope.
        :return: ``WithdrawalWebhook``.
        """
        data = cls.check_json(json_dict)
        instance = super(WithdrawalWebhook, cls).de_json(data)
        instance.data = Withdrawal.de_json(instance.data)
        return instance


class UnknownWebhook(xRocketWebhook):
    """Webhook whose type or invoice event is not known to this library.

    xRocket may extend type and event values. This model retains the original
    envelope instead of failing, so an application can log and ignore it.

    :param id: Unique webhook delivery id, can be used by the receiver for idempotency.
    :param timestamp: When webhook was sent.
    :param type: Unknown webhook type, or ``invoice`` with an unknown event.
    :param data: Original untyped webhook payload.
    """


def verify_webhook_signature(raw_body: bytes | bytearray | str, headers: Mapping[str, Any], webhook_secret: str) -> None:
    """Verify the current xRocket Pay ``v1`` webhook signature.

    API: https://docs.xrocket.exchange/api/pay/pay-api-overview

    ``raw_body`` must be the original request body. ``bytes`` is preferred;
    a string is accepted only when it is the unchanged request body text.
    A parsed dictionary is intentionally rejected because serializing it again
    can alter the signed representation.

    :param raw_body: Original request body as bytes, bytearray, or unchanged
        text.
    :param headers: HTTP request headers. Header names are case-insensitive.
    :param webhook_secret: Application webhook secret used as the HMAC key
        without transformations.
    :return: ``None`` when the signature is valid.
    :raises xRocketWebhookUnsupportedVersionException: If
        ``Signature-Version`` is not ``v1``.
    :raises xRocketWebhookSignatureException: If a required header is absent,
        arguments are invalid, or the signature does not match.
    """
    body = _get_raw_body(raw_body)
    if not isinstance(headers, Mapping):
        raise xRocketWebhookSignatureException("headers must be a mapping.")
    if not isinstance(webhook_secret, str) or not webhook_secret:
        raise xRocketWebhookSignatureException("webhook_secret must be a non-empty string.")

    timestamp = _get_header(headers, "Signature-Timestamp")
    version = _get_header(headers, "Signature-Version")
    signature = _get_header(headers, "Signature")
    if not timestamp or not version or not signature:
        raise xRocketWebhookSignatureException(
            "Webhook headers Signature-Timestamp, Signature-Version, and Signature are required."
        )
    if version != "v1":
        raise xRocketWebhookUnsupportedVersionException(
            "Unsupported xRocket webhook signature version: {}.".format(version)
        )

    signed_body = timestamp.encode("utf-8") + b"." + body
    expected_signature = hmac.new(
        webhook_secret.encode("utf-8"), signed_body, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        raise xRocketWebhookSignatureException("xRocket webhook signature does not match.")


def parse_webhook(payload: bytes | bytearray | str | Mapping[str, Any]) -> xRocketWebhook:
    """Parse an xRocket Pay webhook body into a typed model without verifying it.

    API: https://docs.xrocket.exchange/api/pay/pay-api-overview

    Use this only after independently calling :func:`verify_webhook_signature`.
    In normal HTTP handling, prefer :func:`parse_and_verify_webhook`.

    :param payload: Original JSON body as bytes or text, or a parsed envelope
        mapping when signature verification has already occurred.
    :return: A typed webhook model, or ``UnknownWebhook`` for an unknown type or invoice event.
    :raises xRocketWebhookParseException: If the body is invalid JSON or does
        not have the required webhook envelope structure.
    """
    envelope = _get_envelope(payload)
    _validate_envelope(envelope)

    webhook_type = envelope["type"]
    if webhook_type == "invoice":
        return _parse_invoice_webhook(envelope)
    if webhook_type == "cheque":
        _require_mapping(envelope["data"], "data")
        return ChequeWebhook.de_json(envelope)
    if webhook_type == "payout":
        _require_mapping(envelope["data"], "data")
        return PayoutWebhook.de_json(envelope)
    if webhook_type == "withdrawal":
        _require_mapping(envelope["data"], "data")
        return WithdrawalWebhook.de_json(envelope)
    return UnknownWebhook.de_json(envelope)


def parse_and_verify_webhook(
    raw_body: bytes | bytearray | str,
    headers: Mapping[str, Any],
    webhook_secret: str,
) -> xRocketWebhook:
    """Verify and parse an xRocket Pay webhook in the safe order.

    API: https://docs.xrocket.exchange/api/pay/pay-api-overview

    The signature is verified against the unchanged request body before JSON
    parsing. The returned event must be deduplicated by its ``id`` in the
    application's persistent storage before an irreversible business action.

    :param raw_body: Original request body as bytes, bytearray, or unchanged
        text.
    :param headers: HTTP request headers. Header names are case-insensitive.
    :param webhook_secret: Application webhook secret used as the HMAC key without transformations.
    :return: A typed webhook model, or ``UnknownWebhook`` for an unknown type or invoice event.
    :raises xRocketWebhookSignatureException: If signature validation fails.
    :raises xRocketWebhookParseException: If the verified body is invalid JSON
        or does not have the required webhook envelope structure.
    """
    verify_webhook_signature(raw_body, headers, webhook_secret)
    return parse_webhook(raw_body)


def _get_raw_body(raw_body: bytes | bytearray | str) -> bytes:
    """Return the unchanged request body as bytes for signature verification."""
    if isinstance(raw_body, bytes):
        return raw_body
    if isinstance(raw_body, bytearray):
        return bytes(raw_body)
    if isinstance(raw_body, str):
        return raw_body.encode("utf-8")
    raise xRocketWebhookSignatureException(
        "raw_body must be bytes, bytearray, or unchanged request body text."
    )


def _get_header(headers: Mapping[str, Any], expected_name: str) -> str | None:
    """Read one HTTP header without relying on a framework's header type."""
    expected_name = expected_name.lower()
    for name, value in headers.items():
        if str(name).lower() == expected_name:
            return str(value)
    return None


def _get_envelope(payload: bytes | bytearray | str | Mapping[str, Any]) -> dict[str, Any]:
    """Decode a JSON webhook body or make a shallow copy of a mapping."""
    if isinstance(payload, Mapping):
        return dict(payload)
    if isinstance(payload, bytearray):
        payload = bytes(payload)
    if isinstance(payload, bytes):
        try:
            payload = payload.decode("utf-8")
        except UnicodeDecodeError as error:
            raise xRocketWebhookParseException("Webhook body is not UTF-8 JSON.") from error
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError as error:
            raise xRocketWebhookParseException("Webhook body is not valid JSON.") from error
    if not isinstance(payload, Mapping):
        raise xRocketWebhookParseException("Webhook body must contain a JSON object.")
    return dict(payload)


def _validate_envelope(envelope: Mapping[str, Any]) -> None:
    """Validate the fields required by every documented webhook envelope."""
    for field in ("id", "timestamp", "type", "data"):
        if field not in envelope:
            raise xRocketWebhookParseException(
                "Webhook body is missing required field: {}.".format(field)
            )
    if not isinstance(envelope["type"], str):
        raise xRocketWebhookParseException("Webhook field type must be a string.")


def _parse_invoice_webhook(envelope: dict[str, Any]) -> xRocketWebhook:
    """Choose the typed invoice webhook model using the nested event field."""
    data = _require_mapping(envelope["data"], "data")
    event = data.get("event")
    if event == "invoice_status_changed":
        _require_mapping(data.get("invoice"), "data.invoice")
        return InvoiceStatusChangedWebhook.de_json(envelope)
    if event == "payment_status_changed":
        _require_mapping(data.get("invoice"), "data.invoice")
        _require_mapping(data.get("payment"), "data.payment")
        return PaymentStatusChangedWebhook.de_json(envelope)
    return UnknownWebhook.de_json(envelope)


def _require_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    """Return a payload object or raise a precise structural parse error."""
    if not isinstance(value, Mapping):
        raise xRocketWebhookParseException(
            "Webhook field {} must be a JSON object.".format(field_name)
        )
    return value
