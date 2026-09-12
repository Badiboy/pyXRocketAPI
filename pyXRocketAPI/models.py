import json
from abc import ABC


class xRocketObject(ABC):
    """Base class for xRocket Pay API response models.

    Subclasses declare their API fields in ``__init__`` and override
    ``de_json`` to deserialize nested response objects where necessary.
    """

    @classmethod
    def de_json(cls, json_dict, process_mode=0):
        """Create an instance of this class from an xRocket response dictionary.

        This common implementation is used by subclasses after they validate
        ``json_dict`` with :meth:`check_json`.

        :param json_dict: Parsed response dictionary.
        :param process_mode: ``0`` returns ``None``; ``1`` creates an empty
            instance; ``2`` creates an instance and fills its fields from the
            response dictionary.
        :return: A class instance or ``None`` when ``process_mode`` is ``0``.
        """
        if process_mode == 0:
            return None
        instance = cls()
        if process_mode == 2:
            for key, value in json_dict.items():
                setattr(instance, key, value)
        return instance

    @staticmethod
    def check_json(input_json, dict_copy=False):
        """Validate and normalize an API response dictionary or JSON string.

        :param input_json: A parsed dictionary or a JSON-formatted string.
        :param dict_copy: Return a shallow copy when ``input_json`` is a
            dictionary.
        :return: The parsed dictionary or the original dictionary.
        :raises ValueError: If the input is neither a dictionary nor a JSON
            string.
        """
        if isinstance(input_json, dict):
            return input_json.copy() if dict_copy else input_json
        if isinstance(input_json, str):
            return json.loads(input_json)
        raise ValueError("input_json should be a JSON dictionary or string.")

    def __str__(self):
        """Return a readable string representation of the model fields."""
        data = {}
        for key, value in self.__dict__.items():
            if isinstance(value, list):
                data[key] = [str(item) for item in value]
            elif isinstance(value, dict):
                data[key] = {item_key: str(item_value) for item_key, item_value in value.items()}
            elif hasattr(value, "__dict__"):
                data[key] = value.__dict__
            else:
                data[key] = value
        return str(data)


# noinspection method-overriding
class App(xRocketObject):
    """Current application returned by xRocket Pay.

    API: https://docs.xrocket.exchange/api/pay/reference/http/app-controller-get-app

    :ivar id: No description is provided.
    :ivar name: Name of current app.
    """
    def __init__(self):
        self.id = None
        self.name = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(App, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class Balance(xRocketObject):
    """Balance of an asset belonging to the current application.

    API: https://docs.xrocket.exchange/api/pay/reference/http/app-controller-get-app-balances

    :ivar asset: Balance asset.
    :ivar balance: Asset balance.
    :ivar available: Available balance.
    :ivar holds: Holds balance.
    """
    def __init__(self):
        self.asset = None
        self.balance = None
        self.available = None
        self.holds = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(Balance, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class InvoiceLinks(xRocketObject):
    """Links used to open an invoice payment page.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-get-invoice

    :ivar telegramBotLink: Invoice telegram bot link.
    :ivar telegramMiniAppLink: Invoice telegram mini app link.
    :ivar webLink: Invoice web link.
    """
    def __init__(self):
        self.telegramBotLink = None
        self.telegramMiniAppLink = None
        self.webLink = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(InvoiceLinks, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class Invoice(xRocketObject):
    """Invoice created in xRocket Pay.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-get-invoice

    :ivar id: Invoice id.
    :ivar priceAmount: Invoice price amount.
    :ivar minPayment: Minimum payment amount (for open-amount invoices).
    :ivar priceCurrency: Invoice price currency (crypto or fiat).
    :ivar payCurrencies: Currencies which can be used to pay the invoice (crypto or fiat).
    :ivar clientInvoiceId: Your unique identifier for this invoice to link with your internal system (e.g., order ID).
    :ivar description: Description for invoice.
    :ivar expiresIn: Invoice expires in milliseconds (from creation time).
    :ivar createdAt: Invoice creation time.
    :ivar expiresAt: Invoice expiration time (null if no expiration).
    :ivar status: Invoice status. **WARNING**: This list may be extended in the future. Always use exact status comparison and handle unknown statuses gracefully.
    :ivar callback: No description is provided.
    :ivar url: No description is provided.
    :ivar customer: No description is provided.
    :ivar links: No description is provided.
    """
    def __init__(self):
        self.id = None
        self.priceAmount = None
        self.minPayment = None
        self.priceCurrency = None
        self.payCurrencies = []
        self.clientInvoiceId = None
        self.description = None
        self.expiresIn = None
        self.createdAt = None
        self.expiresAt = None
        self.status = None
        self.callback = None
        self.url = None
        self.customer = None
        self.links = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(Invoice, cls).de_json(data, process_mode=2)
        if instance.links is not None:
            instance.links = InvoiceLinks.de_json(instance.links)
        return instance


# noinspection method-overriding
class ChequeLinks(xRocketObject):
    """Links used to activate a cheque.

    API: https://docs.xrocket.exchange/api/pay/reference/http/cheque-controller-get-cheque

    :ivar telegramBotLink: Cheque activation telegram bot link.
    :ivar telegramMiniAppLink: Cheque activation telegram mini app link (soon).
    :ivar webLink: Cheque activation web link (soon).
    """
    def __init__(self):
        self.telegramBotLink = None
        self.telegramMiniAppLink = None
        self.webLink = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(ChequeLinks, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class Cheque(xRocketObject):
    """Cheque created in xRocket Pay.

    API: https://docs.xrocket.exchange/api/pay/reference/http/cheque-controller-get-cheque

    :ivar chequeId: Cheque ID.
    :ivar clientChequeId: Unique cheque ID in your system to prevent double spends.
    :ivar asset: Currency of transfer.
    :ivar description: Description for cheque.
    :ivar targetType: Target type for cheque.
    :ivar target: Target for cheque.
    :ivar links: Cheque activation links.
    :ivar state: Cheque state.
    :ivar deleted: Cheque is cancelled and the reserved funds are returned to the application balance.
    :ivar callback: No description is provided.
    :ivar url: No description is provided.
    """
    def __init__(self):
        self.chequeId = None
        self.clientChequeId = None
        self.asset = None
        self.description = None
        self.targetType = None
        self.target = None
        self.links = None
        self.state = None
        self.deleted = None
        self.callback = None
        self.url = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(Cheque, cls).de_json(data, process_mode=2)
        if instance.links is not None:
            instance.links = ChequeLinks.de_json(instance.links)
        return instance


# noinspection method-overriding
class Payout(xRocketObject):
    """Payout from the current application to a user.

    API: https://docs.xrocket.exchange/api/pay/reference/http/payout-controller-get-payout

    :ivar payoutId: Payout ID.
    :ivar clientPayoutId: Unique payout ID in your system to prevent double spends.
    :ivar target: Target.
    :ivar targetType: Target type.
    :ivar asset: Asset of payout.
    :ivar amount: Payout amount.
    :ivar description: Payout description.
    :ivar status: Payout status.
    :ivar callback: Webhook settings of this payout.
    """
    def __init__(self):
        self.payoutId = None
        self.clientPayoutId = None
        self.target = None
        self.targetType = None
        self.asset = None
        self.amount = None
        self.description = None
        self.status = None
        self.callback = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(Payout, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class Withdrawal(xRocketObject):
    """Withdrawal from the current application to an external wallet.

    API: https://docs.xrocket.exchange/api/pay/reference/http/withdrawal-controller-get-withdrawal

    :ivar withdrawalId: Unique withdrawal ID in your system to prevent double spends.
    :ivar network: Network code.
    :ivar address: Withdrawal address.
    :ivar asset: Asset code.
    :ivar amount: Withdrawal amount. 9 decimal places, others cut off.
    :ivar status: Withdrawal status.
    :ivar comment: Withdrawal comment.
    :ivar txHash: Withdrawal TX hash. Provided only after withdrawal.
    :ivar txLink: Withdrawal TX link. Provided only after withdrawal.
    :ivar callback: Webhook settings of this withdrawal.
    """
    def __init__(self):
        self.withdrawalId = None
        self.network = None
        self.address = None
        self.asset = None
        self.amount = None
        self.status = None
        self.comment = None
        self.txHash = None
        self.txLink = None
        self.callback = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(Withdrawal, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class CurrencyNetwork(xRocketObject):
    """Network supported by a currency.

    API: https://docs.xrocket.exchange/api/pay/reference/http/currencies-controller-get-currencies

    :ivar code: Network code.
    """
    def __init__(self):
        self.code = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(CurrencyNetwork, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class Currency(xRocketObject):
    """Currency available in xRocket Pay.

    API: https://docs.xrocket.exchange/api/pay/reference/http/currencies-controller-get-currencies

    :ivar code: No description is provided.
    :ivar title: No description is provided.
    :ivar kind: No description is provided.
    :ivar networks: No description is provided.
    """
    def __init__(self):
        self.code = None
        self.title = None
        self.kind = None
        self.networks = []

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(Currency, cls).de_json(data, process_mode=2)
        instance.networks = [CurrencyNetwork.de_json(item) for item in instance.networks]
        return instance


# noinspection method-overriding
class Rate(xRocketObject):
    """Current exchange rate for a currency.

    API: https://docs.xrocket.exchange/api/pay/reference/http/rate-controller-get-rates

    :ivar currency: No description is provided.
    :ivar rate: Current rate.
    """
    def __init__(self):
        self.currency = None
        self.rate = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(Rate, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class xPage(xRocketObject):
    """Base class for paginated xRocket Pay responses.

    This is an SDK base model; the API has no standalone page endpoint.

    :ivar items: No description is provided.
    :ivar pagination: No description is provided.
    """
    def __init__(self):
        self.items = []
        self.pagination = None

    @classmethod
    def de_json(cls, json_dict, process_mode=None):
        data = cls.check_json(json_dict)
        return super(xPage, cls).de_json(data, process_mode=2 if process_mode is None else process_mode)


# noinspection method-overriding
class CursorPagination(xRocketObject):
    """Cursor pagination information for list responses.

    This shared response fragment has no standalone API endpoint.

    :ivar total: Total quantity of campaigns.
    :ivar next: Cursor for the next page of results.
    """
    def __init__(self):
        self.total = None
        self.next = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(CursorPagination, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class InvoicePaymentsPagination(xRocketObject):
    """Cursor pagination information for invoice-payment lists.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-get-invoice-payments

    :ivar next: Cursor for the next page of results.
    """
    def __init__(self):
        self.next = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(InvoicePaymentsPagination, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class InvoicePayment(xRocketObject):
    """A payment made for an invoice.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-get-invoice-payments

    :ivar id: Unique payment id. Use it to match webhook events with the invoice payments endpoint.
    :ivar status: Invoice status. **WARNING**: This list may be extended in the future. Always use exact status comparison and handle unknown statuses gracefully.
    :ivar finalizedAt: When payment reached final state (null for in-progress payments).
    :ivar payAmount: Gross amount payer sent in total across all transactions of this payment (before fees).
    :ivar payCurrency: Currency payer used.
    :ivar receiveAmount: Net amount merchant receives after fees, summed across all transactions of this payment (in invoice priceCurrency).
    :ivar receiveCurrency: Currency merchant receives (= invoice priceCurrency).
    :ivar transactions: No description is provided.
    """
    def __init__(self):
        self.id = None
        self.status = None
        self.finalizedAt = None
        self.payAmount = None
        self.payCurrency = None
        self.receiveAmount = None
        self.receiveCurrency = None
        self.transactions = []

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(InvoicePayment, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class InvoicesList(xPage):
    """Paginated list of invoices.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-get-invoices

    :ivar items: No description is provided.
    :ivar pagination: No description is provided.
    """
    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(InvoicesList, cls).de_json(data)
        instance.items = [Invoice.de_json(item) for item in instance.items]
        if instance.pagination is not None:
            instance.pagination = CursorPagination.de_json(instance.pagination)
        return instance


# noinspection method-overriding
class InvoicePaymentsList(xPage):
    """Paginated list of invoice payments.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-get-invoice-payments

    :ivar items: No description is provided.
    :ivar pagination: No description is provided.
    """
    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(InvoicePaymentsList, cls).de_json(data)
        instance.items = [InvoicePayment.de_json(item) for item in instance.items]
        if instance.pagination is not None:
            instance.pagination = InvoicePaymentsPagination.de_json(instance.pagination)
        return instance


# noinspection method-overriding
class ChequesList(xPage):
    """Paginated list of cheques.

    API: https://docs.xrocket.exchange/api/pay/reference/http/cheque-controller-get-cheques

    :ivar items: No description is provided.
    :ivar pagination: No description is provided.
    """
    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(ChequesList, cls).de_json(data)
        instance.items = [Cheque.de_json(item) for item in instance.items]
        if instance.pagination is not None:
            instance.pagination = CursorPagination.de_json(instance.pagination)
        return instance


# noinspection method-overriding
class PayoutsList(xPage):
    """Paginated list of payouts.

    API: https://docs.xrocket.exchange/api/pay/reference/http/payout-controller-get-list-payouts

    :ivar items: No description is provided.
    :ivar pagination: No description is provided.
    """
    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(PayoutsList, cls).de_json(data)
        instance.items = [Payout.de_json(item) for item in instance.items]
        if instance.pagination is not None:
            instance.pagination = CursorPagination.de_json(instance.pagination)
        return instance


# noinspection method-overriding
class WithdrawalsList(xPage):
    """Paginated list of withdrawals.

    API: https://docs.xrocket.exchange/api/pay/reference/http/withdrawal-controller-get-withdrawals

    :ivar items: No description is provided.
    :ivar pagination: No description is provided.
    """
    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(WithdrawalsList, cls).de_json(data)
        instance.items = [Withdrawal.de_json(item) for item in instance.items]
        if instance.pagination is not None:
            instance.pagination = CursorPagination.de_json(instance.pagination)
        return instance


# noinspection method-overriding
class InvoicePaymentAddress(xRocketObject):
    """Deposit address created for an invoice payment.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-payment-controller-create-invoice-payment-address

    :ivar address: Deposit address.
    :ivar payCurrency: Currency code.
    :ivar payNetwork: Network code.
    :ivar expiresAt: Payment expired at.
    :ivar minAmount: Minimum deposit amount (invoice has no fixed amount).
    """
    def __init__(self):
        self.address = None
        self.payCurrency = None
        self.payNetwork = None
        self.expiresAt = None
        self.minAmount = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(InvoicePaymentAddress, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class WithdrawalQuotas(xRocketObject):
    """Withdrawal quotas for an asset and network.

    API: https://docs.xrocket.exchange/api/pay/reference/http/withdrawal-controller-get-withdrawal-fees

    :ivar withdrawMinSize: Minimum withdrawal amount.
    :ivar withdrawFee: Withdrawal fee.
    :ivar withdrawFeeAsset: Withdrawal fee asset.
    :ivar precision: Floating point precision.
    """
    def __init__(self):
        self.withdrawMinSize = None
        self.withdrawFee = None
        self.withdrawFeeAsset = None
        self.precision = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(WithdrawalQuotas, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class WithdrawalLink(xRocketObject):
    """Links used to create a withdrawal from a user.

    API: https://docs.xrocket.exchange/api/pay/reference/http/withdrawal-links-controller-create-withdrawal-link

    :ivar telegramBotLink: Withdrawal telegram bot link.
    :ivar telegramMiniAppLink: Withdrawal telegram mini app link (soon).
    :ivar webLink: Withdrawal web link (soon).
    """
    def __init__(self):
        self.telegramBotLink = None
        self.telegramMiniAppLink = None
        self.webLink = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(WithdrawalLink, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class MassPayoutReason(xRocketObject):
    """Problem details for one failed mass payout.

    API: https://docs.xrocket.exchange/api/pay/reference/http/mass-payouts-controller-create-mass-payouts

    :ivar type: A URI reference that identifies the problem type.
    :ivar title: A short, human-readable summary of the problem type.
    :ivar status: HTTP status code.
    :ivar detail: A human-readable explanation specific to this occurrence of the problem.
    :ivar instance: A URI reference that identifies the specific occurrence of the problem.
    :ivar kind: Problem category for easier error handling.
    """
    def __init__(self):
        self.type = None
        self.title = None
        self.status = None
        self.detail = None
        self.instance = None
        self.kind = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(MassPayoutReason, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class MassPayoutError(xRocketObject):
    """A failed payout returned by a mass-payout request.

    API: https://docs.xrocket.exchange/api/pay/reference/http/mass-payouts-controller-create-mass-payouts

    :ivar target: Target.
    :ivar targetType: Target type (only TelegramUserId is supported for mass payouts).
    :ivar amount: Payout amount.
    :ivar clientPayoutId: Unique payout ID in your system to prevent double spends.
    :ivar description: Payout description.
    :ivar reason: Payout error reason.
    """
    def __init__(self):
        self.target = None
        self.targetType = None
        self.amount = None
        self.clientPayoutId = None
        self.description = None
        self.reason = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(MassPayoutError, cls).de_json(data, process_mode=2)
        if instance.reason is not None:
            instance.reason = MassPayoutReason.de_json(instance.reason)
        return instance


# noinspection method-overriding
class MassPayouts(xRocketObject):
    """Result of a mass-payout request.

    API: https://docs.xrocket.exchange/api/pay/reference/http/mass-payouts-controller-create-mass-payouts

    :ivar successPayouts: Successful payouts.
    :ivar errorPayouts: Error payouts.
    """
    def __init__(self):
        self.successPayouts = []
        self.errorPayouts = []

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(MassPayouts, cls).de_json(data, process_mode=2)
        instance.successPayouts = [Payout.de_json(item) for item in instance.successPayouts]
        instance.errorPayouts = [MassPayoutError.de_json(item) for item in instance.errorPayouts]
        return instance
