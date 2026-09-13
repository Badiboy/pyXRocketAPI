from collections.abc import Iterable, Mapping
from typing import Any

import requests

from .exceptions import xRocketAPIException
from .models import App, Balance, Cheque, ChequesList, Currency, Health, Invoice, InvoicePaymentAddress, InvoicePaymentsList, InvoicesList, MassPayouts, xPage, Payout, PayoutsList, Rate, Withdrawal, WithdrawalLink, WithdrawalQuotas, WithdrawalsList, xRocketObject

PRODUCTION_API_URL = "https://pay.api.xrocket.exchange"
TESTNET_API_URL = "https://pay.api.testnet.xrocket.exchange"


def _without_none(**values: Any) -> dict[str, Any]:
    """Keep valid falsey API values while omitting arguments not supplied."""
    return {key: value for key, value in values.items() if value is not None}


def _identifier(first_name: str, first_value: str | None, second_name: str, second_value: str | None) -> dict[str, str]:
    if first_value is None and second_value is None:
        raise ValueError(f"Specify {first_name} or {second_name}.")
    return _without_none(**{first_name: first_value, second_name: second_value})


class xRocketPayAPI:
    """Client for the current xRocket Pay API.

    Parameters
    ----------
    token:
        App-specific Pay API Bearer token. Public calls such as
        ``health_check()`` and ``get_available_currencies()`` do not require
        one.
    testnet:
        Select the xRocket Pay testnet URL. A testnet token is required.
    timeout:
        Timeout passed to every request, in seconds.
        ``None`` uses requests' default behaviour.
        Default is 30 seconds.
        A tuple of ``(connect, read)`` timeouts can be passed to override the default for each phase.
    """

    def __init__(
        self,
        token: str | None = None,
        testnet: bool = False,
        timeout: float | tuple[float, float] | None = 30,
    ) -> None:
        self.token = token
        self.timeout = timeout
        self.base_url = TESTNET_API_URL if testnet else PRODUCTION_API_URL

    def _request(
        self,
        method: str,
        path: str,
        params: Mapping[str, Any] | None = None,
        body: Mapping[str, Any] | None = None,
        auth_required: bool = True,
    ) -> Any:
        """Send one request to the xRocket Pay REST API.

        The method builds the standard ``Accept`` header, optionally adds the
        application's Bearer token, sends a JSON request, and converts a
        non-success response from the API's RFC 9457 Problem Details format
        into :class:`xRocketAPIException`.

        :param method: HTTP method, for example ``"GET"`` or ``"POST"``.
        :param path: API path beginning with ``/``, appended to the selected
            production or testnet base URL.
        :param params: Optional query-string parameters.
        :param body: Optional JSON request body.
        :param auth_required: Require an API token and send it in the Bearer
            header. Public endpoints pass ``False`` explicitly; rates may opt
            into authorization.
        :return: Parsed JSON response, or ``None`` for an empty ``204``
            response.
        :raises xRocketAPIException: If a required token is absent, a network
            request fails, the response is not a 2xx success, or a successful
            response does not contain valid JSON.
        """
        headers = {"Accept": "application/json"}
        if auth_required:
            if not self.token:
                raise xRocketAPIException("This endpoint requires an xRocket Pay API token.")
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            response = requests.request(
                method, f"{self.base_url}{path}", params=params, json=body, headers=headers, timeout=self.timeout
            )
        except requests.RequestException as error:
            raise xRocketAPIException(f"Request to xRocket Pay failed: {error}") from error

        if response.status_code < 200 or response.status_code >= 300:
            try:
                problem = response.json()
            except ValueError:
                problem = {}
            detail = problem.get("detail") or problem.get("title") or response.text or "xRocket Pay request failed"
            raise xRocketAPIException(
                detail,
                status=response.status_code,
                problem_type=problem.get("type"),
                title=problem.get("title"),
                detail=problem.get("detail"),
                instance=problem.get("instance"),
                kind=problem.get("kind"),
                info=problem.get("info"),
            )

        if response.status_code == 204 or not response.content:
            return None
        try:
            return response.json()
        except ValueError as error:
            raise xRocketAPIException("xRocket Pay returned invalid JSON.", status=response.status_code) from error

    def health_check(self) -> Health:
        """Run the public health check.

        API: https://docs.xrocket.exchange/api/pay/reference/http/health-controller-health

        :return: ``Health``.
        """
        return Health.de_json(self._request("GET", "/health", auth_required=False))

    def get_app_info(self) -> App:
        """Get information about your application.

        API: https://docs.xrocket.exchange/api/pay/reference/http/app-controller-get-app

        :return: ``App``.
        """
        return App.de_json(self._request("GET", "/api/v1/app-info"))

    def get_balances(self) -> list[Balance]:
        """Get balances of your application.

        API: https://docs.xrocket.exchange/api/pay/reference/http/app-controller-get-app-balances

        :return: ``list[Balance]``.
        """
        data = self._request("GET", "/api/v1/balances")
        return [Balance.de_json(item) for item in data.get("balances", [])]

    def get_currencies(self, kind: str | None = None) -> list[Currency]:
        """Get available currencies.

        API: https://docs.xrocket.exchange/api/pay/reference/http/currencies-controller-get-currencies

        :param kind: No description is provided.
        :return: ``list[Currency]``.
        """
        data = self._request(
            "GET", "/api/v1/currencies", params=_without_none(kind=kind), auth_required=False
        )
        return [Currency.de_json(item) for item in data]

    def get_rates(self, base: str, assets: Iterable[str], authorize: bool = False) -> list[Rate]:
        """Get currencies rates (optional auth).

        API: https://docs.xrocket.exchange/api/pay/reference/http/rate-controller-get-rates

        :param base: Fiat currency.
        :param assets: Asset codes.
        :param authorize: Send the optional Bearer authorization header.
        :return: ``list[Rate]``.
        """
        data = self._request(
            "GET", "/api/v1/rates", params={"base": base, "assets": list(assets)},
            auth_required=authorize,
        )
        return [Rate.de_json(item) for item in data]

    def create_invoice(
        self,
        price_currency: str,
        price_amount: str | None = None,
        min_payment: str | None = None,
        num_payments: int | None = None,
        payout_currency: str | None = None,
        pay_currencies: Iterable[str] | None = None,
        client_invoice_id: str | None = None,
        description: str | None = None,
        expires_in: int | None = None,
        callback: Mapping[str, Any] | None = None,
        url: Mapping[str, Any] | None = None,
        customer: Mapping[str, Any] | None = None,
        is_fee_paid_by_user: bool | None = None,
        data: Mapping[str, Any] | None = None,
        platform_id: str | None = None,
    ) -> Invoice:
        """Create invoice.

        API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-create-invoice

        :param price_currency: Invoice price currency (crypto or fiat).
        :param price_amount: Invoice price amount.
        :param min_payment: Minimum payment amount (for open-amount invoices).
        :param num_payments: Num payments for invoice.
        :param payout_currency: Invoice payout crypto currency.
        :param pay_currencies: Crypto currencies which can be used to pay the invoice.
        :param client_invoice_id: Client Invoice ID as assigned by the client.
        :param description: Description for invoice.
        :param expires_in: Payment expires in milliseconds.
        :param callback: Callback data.
        :param url: User redirect urls.
        :param customer: Customer info.
        :param is_fee_paid_by_user: If true, the user pays a commission.
        :param data: Custom user data passed through and returned in callbacks/webhooks (max size 4KB).
        :param platform_id: Platform identifier.
        :return: ``Invoice``.
        """
        body = _without_none(
            priceCurrency=price_currency, priceAmount=price_amount, minPayment=min_payment, numPayments=num_payments,
            payoutCurrency=payout_currency, payCurrencies=list(pay_currencies) if pay_currencies is not None else None,
            clientInvoiceId=client_invoice_id, description=description, expiresIn=expires_in, callback=callback, url=url,
            customer=customer, isFeePaidByUser=is_fee_paid_by_user, data=data, platformId=platform_id,
        )
        return Invoice.de_json(self._request("POST", "/api/v1/invoices", body=body))

    def get_invoices_list(self, asset: str | None = None, fiat: str | None = None, ids: Iterable[str] | None = None,
                 status: str | None = None, cursor: str | None = None, limit: int | None = None) -> InvoicesList:
        """Get list of invoices.

        API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-get-invoices

        :param asset: Filtering invoices by asset.
        :param fiat: Filtering invoices by fiat.
        :param ids: Filtering invoices by ids.
        :param status: Filtering invoices by status.
        :param cursor: Cursor for pagination.
        :param limit: No description is provided.
        :return: ``InvoicesList``.
        """
        params = _without_none(asset=asset, fiat=fiat, ids=list(ids) if ids is not None else None, status=status, cursor=cursor, limit=limit)
        return InvoicesList.de_json(self._request("GET", "/api/v1/invoices", params=params))

    def get_invoice_info(self, invoice_id: str | None = None, client_invoice_id: str | None = None) -> Invoice:
        """Get invoice info.

        API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-get-invoice
        Either invoiceId (xRocket) or clientInvoiceId (client-assigned) is required. If both are passed, invoiceId will be used.

        :param invoice_id: xRocket Invoice ID. Either invoiceId or clientInvoiceId is required. If both are passed, invoiceId will be used.
        :param client_invoice_id: Client Invoice ID assigned by the client. Either invoiceId or clientInvoiceId is required.
        :return: ``Invoice``.
        """
        return Invoice.de_json(self._request("GET", "/api/v1/invoice", params=_identifier("invoiceId", invoice_id, "clientInvoiceId", client_invoice_id)))

    def delete_invoice(self, invoice_id: str | None = None, client_invoice_id: str | None = None) -> None:
        """Delete invoice.

        API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-delete-invoice
        Either invoiceId (xRocket) or clientInvoiceId (client-assigned) is required. If both are passed, invoiceId will be used.

        :param invoice_id: xRocket Invoice ID. Either invoiceId or clientInvoiceId is required. If both are passed, invoiceId will be used.
        :param client_invoice_id: Client Invoice ID assigned by the client. Either invoiceId or clientInvoiceId is required.
        :return: ``None``.
        """
        self._request("DELETE", "/api/v1/invoice", params=_identifier("invoiceId", invoice_id, "clientInvoiceId", client_invoice_id))

    def get_invoice_payments(self, invoice_id: str | None = None, client_invoice_id: str | None = None,
                         cursor: str | None = None, limit: int | None = None) -> InvoicePaymentsList:
        """Get invoice payments.

        API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-get-invoice-payments
        Returns payments of an invoice in the same format as the payment_status_changed webhook. Either invoiceId (xRocket) or clientInvoiceId (client-assigned) is required. If both are passed, invoiceId will be used.

        :param invoice_id: xRocket Invoice ID. Either invoiceId or clientInvoiceId is required. If both are passed, invoiceId will be used.
        :param client_invoice_id: Client Invoice ID assigned by the client. Either invoiceId or clientInvoiceId is required.
        :param cursor: Cursor for pagination.
        :param limit: No description is provided.
        :return: ``InvoicePaymentsList``.
        """
        params = _identifier("invoiceId", invoice_id, "clientInvoiceId", client_invoice_id)
        params.update(_without_none(cursor=cursor, limit=limit))
        return InvoicePaymentsList.de_json(self._request("GET", "/api/v1/invoice/payments", params=params))

    def create_invoice_payment_address(self, pay_network: str, invoice_id: str | None = None,
                                       client_invoice_id: str | None = None) -> InvoicePaymentAddress:
        """Create invoice payment address.

        API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-payment-controller-create-invoice-payment-address

        :param pay_network: Network code for payment.
        :param invoice_id: xRocket Invoice ID. Either invoiceId or clientInvoiceId is required. If both are passed, invoiceId will be used.
        :param client_invoice_id: Client Invoice ID assigned by the client. Either invoiceId or clientInvoiceId is required.
        :return: ``InvoicePaymentAddress``.
        """
        return InvoicePaymentAddress.de_json(self._request(
            "POST", "/api/v1/invoices/payments/address",
            params=_identifier("invoiceId", invoice_id, "clientInvoiceId", client_invoice_id), body={"payNetwork": pay_network},
        ))

    def create_cheque(self, asset: str, amount: str, client_cheque_id: str | None = None, password: str | None = None,
                      description: str | None = None, callback: Mapping[str, Any] | None = None, url: Mapping[str, Any] | None = None,
                      target_type: str | None = None, target: str | None = None) -> Cheque:
        """Create cheque.

        API: https://docs.xrocket.exchange/api/pay/reference/http/cheque-controller-create-cheque
        Issue a personal cheque to perform an accept-type payout. The amount is reserved from the application balance and can be redeemed by the recipient or cancelled before redemption. When targetType and target are set, only the addressed user is allowed to redeem the cheque.

        :param asset: Currency of transfer.
        :param amount: Cheque amount.
        :param client_cheque_id: Unique cheque ID in your system to prevent double spends.
        :param password: Cheque password, the recipient has to enter it to redeem the cheque.
        :param description: Description for cheque.
        :param callback: Webhook settings for cheque activation updates.
        :param url: User redirect urls after cheque activation.
        :param target_type: Target type for cheque, has to be passed together with target.
        :param target: Target for cheque, has to be passed together with targetType.
        :return: ``Cheque``.
        """
        return Cheque.de_json(self._request("POST", "/api/v1/cheques", body=_without_none(
            asset=asset, amount=str(amount), clientChequeId=client_cheque_id, password=password, description=description,
            callback=callback, url=url, targetType=target_type, target=target,
        )))

    def get_cheques_list(self, from_date: str | None = None, to_date: str | None = None, target_type: str | None = None,
                target: str | None = None, state: str | None = None, cursor: str | None = None, limit: int | None = None) -> ChequesList:
        """Get list of cheques.

        API: https://docs.xrocket.exchange/api/pay/reference/http/cheque-controller-get-cheques
        List personal cheques issued for accept-type transfers. Use this to monitor pending, redeemed, or cancelled cheques. Cancelled cheques are excluded from the list.

        :param from_date: From date (ISO 8601).
        :param to_date: To date (ISO 8601).
        :param target_type: Target type for cheque, has to be passed together with target.
        :param target: Target identifier for cheque (depends on targetType), has to be passed together with targetType.
        :param state: Cheque state.
        :param cursor: Cursor for pagination.
        :param limit: No description is provided.
        :return: ``ChequesList``.
        """
        return ChequesList.de_json(self._request("GET", "/api/v1/cheques", params=_without_none(
            fromDate=from_date, toDate=to_date, targetType=target_type, target=target, state=state, cursor=cursor, limit=limit,
        )))

    def get_cheque_info(self, cheque_id: str | None = None, client_cheque_id: str | None = None) -> Cheque:
        """Get cheque info.

        API: https://docs.xrocket.exchange/api/pay/reference/http/cheque-controller-get-cheque
        Fetch details of a personal cheque used for an accept-type payout, including status and reserved amount. A cancelled cheque is returned with the deleted flag set.

        :param cheque_id: Cheque id.
        :param client_cheque_id: Unique cheque id in your system.
        :return: ``Cheque``.
        """
        return Cheque.de_json(self._request("GET", "/api/v1/cheque", params=_identifier("chequeId", cheque_id, "clientChequeId", client_cheque_id)))

    def update_cheque(self, description: str, cheque_id: str | None = None, client_cheque_id: str | None = None) -> Cheque:
        """Update cheque.

        API: https://docs.xrocket.exchange/api/pay/reference/http/cheque-controller-update-cheque
        Modify an active unredeemed cheque. Only description can be updated, pass an empty string to clear it. The cheque must be in active state, not cancelled and not yet redeemed.

        :param description: Cheque description (set empty string to clear description).
        :param cheque_id: Cheque id.
        :param client_cheque_id: Unique cheque id in your system.
        :return: ``Cheque``.
        """
        return Cheque.de_json(self._request("PUT", "/api/v1/cheques", params=_identifier("chequeId", cheque_id, "clientChequeId", client_cheque_id), body={"description": description}))

    def delete_cheque(self, cheque_id: str | None = None, client_cheque_id: str | None = None) -> None:
        """Delete cheque.

        API: https://docs.xrocket.exchange/api/pay/reference/http/cheque-controller-delete-cheque
        Cancel an unredeemed personal cheque. Upon cancellation, the reserved funds are released back to the application balance.

        :param cheque_id: Cheque id.
        :param client_cheque_id: Unique cheque id in your system.
        :return: ``None``.
        """
        self._request("DELETE", "/api/v1/cheques", params=_identifier("chequeId", cheque_id, "clientChequeId", client_cheque_id))

    def payout_funds_to_user(self, target: str, target_type: str, asset: str, amount: str, client_payout_id: str | None = None,
                      description: str | None = None, callback: Mapping[str, Any] | None = None) -> Payout:
        """Payout funds to user.

        API: https://docs.xrocket.exchange/api/pay/reference/http/payout-controller-payout

        :param target: Target.
        :param target_type: Target type.
        :param asset: Asset of transfer.
        :param amount: Payout amount.
        :param client_payout_id: Unique payout ID in your system to prevent double spends.
        :param description: Payout description.
        :param callback: Webhook settings for payout status updates.
        :return: ``Payout``.
        """
        return Payout.de_json(self._request("POST", "/api/v1/payouts", body=_without_none(
            target=target, targetType=target_type, asset=asset, amount=str(amount), clientPayoutId=client_payout_id,
            description=description, callback=callback,
        )))

    def get_payouts_list(self, from_date: str | None = None, to_date: str | None = None, cursor: str | None = None,
                limit: int | None = None) -> PayoutsList:
        """Get payouts list.

        API: https://docs.xrocket.exchange/api/pay/reference/http/payout-controller-get-list-payouts

        :param from_date: From date (ISO 8601).
        :param to_date: To date (ISO 8601).
        :param cursor: Cursor for pagination.
        :param limit: No description is provided.
        :return: ``PayoutsList``.
        """
        return PayoutsList.de_json(self._request("GET", "/api/v1/payouts", params=_without_none(fromDate=from_date, toDate=to_date, cursor=cursor, limit=limit)))

    def get_payout_info(self, payout_id: str | None = None, client_payout_id: str | None = None) -> Payout:
        """Get payout info.

        API: https://docs.xrocket.exchange/api/pay/reference/http/payout-controller-get-payout

        :param payout_id: Payout ID.
        :param client_payout_id: Unique payout ID in your system to prevent double spends.
        :return: ``Payout``.
        """
        return Payout.de_json(self._request("GET", "/api/v1/payout", params=_identifier("payoutId", payout_id, "clientPayoutId", client_payout_id)))

    def create_mass_payouts(self, asset: str, payouts: Iterable[Mapping[str, Any]]) -> MassPayouts:
        """Create mass payouts (Telegram users only).

        API: https://docs.xrocket.exchange/api/pay/reference/http/mass-payouts-controller-create-mass-payouts

        :param asset: Asset of payouts.
        :param payouts: List of payouts to process.
        :return: ``MassPayouts``.
        """
        return MassPayouts.de_json(self._request("POST", "/api/v1/mass-payouts", body={"asset": asset, "payouts": list(payouts)}))

    def withdrawal_funds(self, client_withdrawal_id: str, network: str, address: str, asset: str, amount: str,
                         comment: str | None = None, callback: Mapping[str, Any] | None = None) -> Withdrawal:
        """Withdrawal funds from application to external wallet.

        API: https://docs.xrocket.exchange/api/pay/reference/http/withdrawal-controller-create-withdrawal

        :param client_withdrawal_id: Unique withdrawal ID in your system to prevent double spends.
        :param network: Network code.
        :param address: Withdrawal address.
        :param asset: Asset code.
        :param amount: Withdrawal amount.
        :param comment: Withdrawal comment.
        :param callback: Webhook settings for withdrawal status updates.
        :return: ``Withdrawal``.
        """
        return Withdrawal.de_json(self._request("POST", "/api/v1/withdrawals", body=_without_none(
            clientWithdrawalId=client_withdrawal_id, network=network, address=address, asset=asset, amount=str(amount),
            comment=comment, callback=callback,
        )))

    def get_withdrawals_list(self, from_date: str | None = None, to_date: str | None = None, status: str | None = None,
                             cursor: str | None = None, limit: int | None = None) -> WithdrawalsList:
        """Get application withdrawals.

        API: https://docs.xrocket.exchange/api/pay/reference/http/withdrawal-controller-get-withdrawals

        :param from_date: From date (ISO 8601).
        :param to_date: To date (ISO 8601).
        :param status: Withdrawal status.
        :param cursor: Cursor for pagination.
        :param limit: No description is provided.
        :return: ``WithdrawalsList``.
        """
        return WithdrawalsList.de_json(self._request("GET", "/api/v1/withdrawals", params=_without_none(
            fromDate=from_date, toDate=to_date, status=status, cursor=cursor, limit=limit,
        )))

    def get_withdrawal_info(self, withdrawal_id: str | None = None, client_withdrawal_id: str | None = None) -> Withdrawal:
        """Get application withdrawal info.

        API: https://docs.xrocket.exchange/api/pay/reference/http/withdrawal-controller-get-withdrawal

        :param withdrawal_id: Withdrawal ID.
        :param client_withdrawal_id: Unique withdrawal ID in your system to prevent double spends.
        :return: ``Withdrawal``.
        """
        return Withdrawal.de_json(self._request("GET", "/api/v1/withdrawal", params=_identifier("withdrawalId", withdrawal_id, "clientWithdrawalId", client_withdrawal_id)))

    def get_withdrawal_quotas(self, network: str, asset: str) -> WithdrawalQuotas:
        """Get application withdrawal quotas.

        API: https://docs.xrocket.exchange/api/pay/reference/http/withdrawal-controller-get-withdrawal-fees

        :param network: Network code.
        :param asset: Asset code.
        :return: ``WithdrawalQuotas``.
        """
        return WithdrawalQuotas.de_json(self._request("GET", "/api/v1/withdrawal-quotas", params={"network": network, "asset": asset}))

    def create_withdrawal_link(self, network: str, address: str, asset: str, amount: str, comment: str | None = None,
                               platform: str | None = None) -> WithdrawalLink:
        """Create withdrawal link.

        API: https://docs.xrocket.exchange/api/pay/reference/http/withdrawal-links-controller-create-withdrawal-link

        :param network: Network code.
        :param address: Withdrawal address.
        :param asset: Asset code.
        :param amount: Withdrawal amount.
        :param comment: Withdrawal comment.
        :param platform: Platform identifier (optional, use only if provided by xRocket).
        :return: ``WithdrawalLink``.
        """
        return WithdrawalLink.de_json(self._request("POST", "/api/v1/withdrawal-link", body=_without_none(
            network=network, address=address, asset=asset, amount=str(amount), comment=comment, platform=platform,
        )))
