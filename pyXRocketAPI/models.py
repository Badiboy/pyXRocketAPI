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
class HealthComponent(xRocketObject):
    """One component reported by the xRocket Pay health check.

    API: https://docs.xrocket.exchange/api/pay/reference/http/health-controller-health

    :param name: No description is provided.
    :param status: No description is provided.
    :param message: No description is provided.
    """
    def __init__(self):
        self.name = None
        self.status = None
        self.message = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(HealthComponent, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class Health(xRocketObject):
    """Response returned by the xRocket Pay health-check endpoint.

    API: https://docs.xrocket.exchange/api/pay/reference/http/health-controller-health

    :param status: No description is provided.
    :param info: No description is provided.
    :param error: No description is provided.
    :param details: No description is provided.
    """
    def __init__(self):
        self.status = None
        self.info = []
        self.error = []
        self.details = []

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(Health, cls).de_json(data, process_mode=2)
        instance.info = [HealthComponent.de_json(item) for item in instance.info]
        instance.error = [HealthComponent.de_json(item) for item in instance.error]
        instance.details = [HealthComponent.de_json(item) for item in instance.details]
        return instance


# noinspection method-overriding
class App(xRocketObject):
    """Current application returned by xRocket Pay.

    API: https://docs.xrocket.exchange/api/pay/reference/http/app-controller-get-app

    :param id: No description is provided.
    :param name: Name of current app.
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

    :param asset: Balance asset.
    :param balance: Asset balance.
    :param available: Available balance.
    :param holds: Holds balance.
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

    :param telegramBotLink: Invoice telegram bot link.
    :param telegramMiniAppLink: Invoice telegram mini app link.
    :param webLink: Invoice web link.
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
class InvoiceCallback(xRocketObject):
    """Webhook settings returned for an invoice.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-get-invoice

    :param callbackUrl: Url for notify when order status is changed.
    :param payload: Custom data sent to webhook.
    """

    def __init__(self):
        self.callbackUrl = None
        self.payload = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(InvoiceCallback, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class InvoiceUrl(xRocketObject):
    """User redirect URLs returned for an invoice.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-get-invoice

    :param successUrl: Redirect user to url after successful payment.
    :param cancelUrl: Redirect user to url after cancel payment.
    """

    def __init__(self):
        self.successUrl = None
        self.cancelUrl = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(InvoiceUrl, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class InvoiceCustomer(xRocketObject):
    """Customer information returned for an invoice.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-get-invoice

    :param id: Customer id in your app.
    :param email: Customer email.
    :param telegramId: Customer telegram ID.
    :param telegramUsername: Customer telegram username (without @).
    """

    def __init__(self):
        self.id = None
        self.email = None
        self.telegramId = None
        self.telegramUsername = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(InvoiceCustomer, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class Invoice(xRocketObject):
    """Invoice created in xRocket Pay.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-get-invoice

    :param id: Invoice id.
    :param priceAmount: Invoice price amount.
    :param minPayment: Minimum payment amount (for open-amount invoices).
    :param priceCurrency: Invoice price currency (crypto or fiat).
    :param payCurrencies: Currencies which can be used to pay the invoice (crypto or fiat).
    :param clientInvoiceId: Your unique identifier for this invoice to link with your internal system (e.g., order ID).
    :param description: Description for invoice.
    :param expiresIn: Invoice expires in milliseconds (from creation time).
    :param createdAt: Invoice creation time.
    :param expiresAt: Invoice expiration time (null if no expiration).
    :param status: Invoice status. **WARNING**: This list may be extended in the future. Always use exact status comparison and handle unknown statuses gracefully.
    :param callback: Invoice webhook settings.
    :param url: Invoice user redirect URLs.
    :param customer: Invoice customer information.
    :param links: Invoice payment links.
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
        if instance.callback is not None:
            instance.callback = InvoiceCallback.de_json(instance.callback)
        if instance.url is not None:
            instance.url = InvoiceUrl.de_json(instance.url)
        if instance.customer is not None:
            instance.customer = InvoiceCustomer.de_json(instance.customer)
        if instance.links is not None:
            instance.links = InvoiceLinks.de_json(instance.links)
        return instance


# noinspection method-overriding
class ChequeLinks(xRocketObject):
    """Links used to activate a cheque.

    API: https://docs.xrocket.exchange/api/pay/reference/http/cheque-controller-get-cheque

    :param telegramBotLink: Cheque activation telegram bot link.
    :param telegramMiniAppLink: Cheque activation telegram mini app link (soon).
    :param webLink: Cheque activation web link (soon).
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
class ChequeCallback(xRocketObject):
    """Webhook settings returned for a cheque.

    API: https://docs.xrocket.exchange/api/pay/reference/http/cheque-controller-get-cheque

    :param callbackUrl: Url for notifying when cheque status changes.
    :param payload: Custom data sent to webhook along with cheque status updates.
    """
    def __init__(self):
        self.callbackUrl = None
        self.payload = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(ChequeCallback, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class ChequeUrl(xRocketObject):
    """User redirect URLs returned for a cheque.

    API: https://docs.xrocket.exchange/api/pay/reference/http/cheque-controller-get-cheque

    :param successUrl: Redirect user to URL after successful cheque activation.
    :param cancelUrl: Redirect user to URL after cheque activation is cancelled/failed.
    """
    def __init__(self):
        self.successUrl = None
        self.cancelUrl = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(ChequeUrl, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class Cheque(xRocketObject):
    """Cheque created in xRocket Pay.

    API: https://docs.xrocket.exchange/api/pay/reference/http/cheque-controller-get-cheque

    :param chequeId: Cheque ID.
    :param clientChequeId: Unique cheque ID in your system to prevent double spends.
    :param asset: Currency of transfer.
    :param description: Description for cheque.
    :param targetType: Target type for cheque.
    :param target: Target for cheque.
    :param links: Cheque activation links.
    :param state: Cheque state.
    :param deleted: Cheque is cancelled and the reserved funds are returned to the application balance.
    :param callback: Cheque webhook settings.
    :param url: Cheque user redirect URLs.
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
        if instance.callback is not None:
            instance.callback = ChequeCallback.de_json(instance.callback)
        if instance.url is not None:
            instance.url = ChequeUrl.de_json(instance.url)
        return instance


# noinspection method-overriding
class PayoutCallback(xRocketObject):
    """Webhook settings returned for a payout.

    API: https://docs.xrocket.exchange/api/pay/reference/http/payout-controller-get-payout

    :param callbackUrl: Url for notify when payout status is changed.
    :param payload: Custom data sent to webhook.
    """
    def __init__(self):
        self.callbackUrl = None
        self.payload = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(PayoutCallback, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class Payout(xRocketObject):
    """Payout from the current application to a user.

    API: https://docs.xrocket.exchange/api/pay/reference/http/payout-controller-get-payout

    :param payoutId: Payout ID.
    :param clientPayoutId: Unique payout ID in your system to prevent double spends.
    :param target: Target.
    :param targetType: Target type.
    :param asset: Asset of payout.
    :param amount: Payout amount.
    :param description: Payout description.
    :param status: Payout status.
    :param callback: Webhook settings of this payout.
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
        instance = super(Payout, cls).de_json(data, process_mode=2)
        if instance.callback is not None:
            instance.callback = PayoutCallback.de_json(instance.callback)
        return instance


# noinspection method-overriding
class WithdrawalCallback(xRocketObject):
    """Webhook settings returned for a withdrawal.

    API: https://docs.xrocket.exchange/api/pay/reference/http/withdrawal-controller-get-withdrawal

    :param callbackUrl: Url for notify when withdrawal status is changed.
    :param payload: Custom data sent to webhook.
    """
    def __init__(self):
        self.callbackUrl = None
        self.payload = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(WithdrawalCallback, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class Withdrawal(xRocketObject):
    """Withdrawal from the current application to an external wallet.

    API: https://docs.xrocket.exchange/api/pay/reference/http/withdrawal-controller-get-withdrawal

    :param withdrawalId: Unique withdrawal ID in your system to prevent double spends.
    :param network: Network code.
    :param address: Withdrawal address.
    :param asset: Asset code.
    :param amount: Withdrawal amount. 9 decimal places, others cut off.
    :param status: Withdrawal status.
    :param comment: Withdrawal comment.
    :param txHash: Withdrawal TX hash. Provided only after withdrawal.
    :param txLink: Withdrawal TX link. Provided only after withdrawal.
    :param callback: Webhook settings of this withdrawal.
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
        instance = super(Withdrawal, cls).de_json(data, process_mode=2)
        if instance.callback is not None:
            instance.callback = WithdrawalCallback.de_json(instance.callback)
        return instance


# noinspection method-overriding
class CurrencyNetwork(xRocketObject):
    """Network supported by a currency.

    API: https://docs.xrocket.exchange/api/pay/reference/http/currencies-controller-get-currencies

    :param code: Network code.
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

    :param code: No description is provided.
    :param title: No description is provided.
    :param kind: No description is provided.
    :param networks: No description is provided.
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

    :param currency: No description is provided.
    :param rate: Current rate.
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

    :param items: No description is provided.
    :param pagination: No description is provided.
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

    :param total: Total quantity of campaigns.
    :param next: Cursor for the next page of results.
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

    :param next: Cursor for the next page of results.
    """
    def __init__(self):
        self.next = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(InvoicePaymentsPagination, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class InvoicePaymentPayer(xRocketObject):
    """Payer information for an invoice payment transaction.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-get-invoice-payments

    :param email: Payer email.
    :param telegramId: Payer telegram ID.
    :param telegramUsername: Payer telegram username (without @).
    """
    def __init__(self):
        self.email = None
        self.telegramId = None
        self.telegramUsername = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(InvoicePaymentPayer, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class InvoicePaymentTransactionBlockchainDetails(xRocketObject):
    """Blockchain-specific details of an invoice payment transaction.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-get-invoice-payments

    :param network: Blockchain network code.
    :param txHash: Transaction hash.
    :param amount: Amount in this specific transaction.
    :param currency: Currency of this transaction.
    :param status: On-chain status. **WARNING**: This list may be extended in the future. Treat unknown statuses as "in progress".
    """
    def __init__(self):
        self.network = None
        self.txHash = None
        self.amount = None
        self.currency = None
        self.status = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        return super(InvoicePaymentTransactionBlockchainDetails, cls).de_json(data, process_mode=2)


# noinspection method-overriding
class InvoiceInternalTransaction(xRocketObject):
    """Internal transaction belonging to an invoice payment.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-get-invoice-payments

    :param id: Payment id.
    :param status: Payment status. **WARNING**: This list may be extended in the future. Use exact string comparison and treat unknown statuses as "in progress".
    :param payAmount: Amount payer sent (gross, before fees). Null when payment is created but amount is not yet known.
    :param payCurrency: Currency payer used. Null when payment is created but currency is not yet known.
    :param receiveAmount: Amount merchant receives after fees (in invoice priceCurrency). Null until payment is finalized.
    :param receiveCurrency: Currency merchant receives (= invoice priceCurrency). Null until payment is finalized.
    :param comment: Payer comment.
    :param payer: Payer information.
    :param createdAt: Payment creation time.
    :param finalizedAt: When payment reached final state (null for in-progress payments).
    :param type: Payment type.
    """
    def __init__(self):
        self.id = None
        self.status = None
        self.payAmount = None
        self.payCurrency = None
        self.receiveAmount = None
        self.receiveCurrency = None
        self.comment = None
        self.payer = None
        self.createdAt = None
        self.finalizedAt = None
        self.type = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(InvoiceInternalTransaction, cls).de_json(data, process_mode=2)
        if instance.payer is not None:
            instance.payer = InvoicePaymentPayer.de_json(instance.payer)
        return instance


# noinspection method-overriding
class InvoiceBlockchainTransaction(xRocketObject):
    """Blockchain transaction belonging to an invoice payment.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-get-invoice-payments

    :param id: Payment id.
    :param status: Payment status. **WARNING**: This list may be extended in the future. Use exact string comparison and treat unknown statuses as "in progress".
    :param payAmount: Amount payer sent (gross, before fees). Null when payment is created but amount is not yet known.
    :param payCurrency: Currency payer used. Null when payment is created but currency is not yet known.
    :param receiveAmount: Amount merchant receives after fees (in invoice priceCurrency). Null until payment is finalized.
    :param receiveCurrency: Currency merchant receives (= invoice priceCurrency). Null until payment is finalized.
    :param comment: Payer comment.
    :param payer: Payer information.
    :param createdAt: Payment creation time.
    :param finalizedAt: When payment reached final state (null for in-progress payments).
    :param type: Payment type.
    :param tx: Blockchain-specific details. Present only for ``type=blockchain`` transactions.
    """
    def __init__(self):
        self.id = None
        self.status = None
        self.payAmount = None
        self.payCurrency = None
        self.receiveAmount = None
        self.receiveCurrency = None
        self.comment = None
        self.payer = None
        self.createdAt = None
        self.finalizedAt = None
        self.type = None
        self.tx = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(InvoiceBlockchainTransaction, cls).de_json(data, process_mode=2)
        if instance.payer is not None:
            instance.payer = InvoicePaymentPayer.de_json(instance.payer)
        if instance.tx is not None:
            instance.tx = InvoicePaymentTransactionBlockchainDetails.de_json(instance.tx)
        return instance


# noinspection method-overriding
class InvoicePayment(xRocketObject):
    """A payment made for an invoice.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-get-invoice-payments

    :param id: Unique payment id. Use it to match webhook events with the invoice payments endpoint.
    :param status: Payment status. **WARNING**: This list may be extended in the future. Use exact string comparison and treat unknown statuses as "in progress".
    :param finalizedAt: When payment reached final state (null for in-progress payments).
    :param payAmount: Gross amount payer sent in total across all transactions of this payment (before fees).
    :param payCurrency: Currency payer used.
    :param receiveAmount: Net amount merchant receives after fees, summed across all transactions of this payment (in invoice priceCurrency).
    :param receiveCurrency: Currency merchant receives (= invoice priceCurrency).
    :param transactions: No description is provided.
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
        instance = super(InvoicePayment, cls).de_json(data, process_mode=2)
        transactions = []
        for transaction in instance.transactions:
            transaction_data = cls.check_json(transaction)
            if transaction_data.get("type") == "internal":
                transactions.append(InvoiceInternalTransaction.de_json(transaction_data))
            elif transaction_data.get("type") == "blockchain":
                transactions.append(InvoiceBlockchainTransaction.de_json(transaction_data))
            else:
                transactions.append(xRocketObject.de_json(transaction_data, process_mode=2))
        instance.transactions = transactions
        return instance


# noinspection method-overriding
class InvoicesList(xPage):
    """Paginated list of invoices.

    API: https://docs.xrocket.exchange/api/pay/reference/http/invoice-controller-get-invoices

    :param items: No description is provided.
    :param pagination: No description is provided.
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

    :param items: No description is provided.
    :param pagination: No description is provided.
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

    :param items: No description is provided.
    :param pagination: No description is provided.
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

    :param items: No description is provided.
    :param pagination: No description is provided.
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

    :param items: No description is provided.
    :param pagination: No description is provided.
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

    :param address: Deposit address.
    :param payCurrency: Currency code.
    :param payNetwork: Network code.
    :param expiresAt: Payment expired at.
    :param minAmount: Minimum deposit amount (invoice has no fixed amount).
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

    :param withdrawMinSize: Minimum withdrawal amount.
    :param withdrawFee: Withdrawal fee.
    :param withdrawFeeAsset: Withdrawal fee asset.
    :param precision: Floating point precision.
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

    :param telegramBotLink: Withdrawal telegram bot link.
    :param telegramMiniAppLink: Withdrawal telegram mini app link (soon).
    :param webLink: Withdrawal web link (soon).
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

    :param type: A URI reference that identifies the problem type.
    :param title: A short, human-readable summary of the problem type.
    :param status: HTTP status code.
    :param detail: A human-readable explanation specific to this occurrence of the problem.
    :param instance: A URI reference that identifies the specific occurrence of the problem.
    :param kind: Problem category for easier error handling.
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

    :param target: Target.
    :param targetType: Target type (only TelegramUserId is supported for mass payouts).
    :param amount: Payout amount.
    :param clientPayoutId: Unique payout ID in your system to prevent double spends.
    :param description: Payout description.
    :param reason: Payout error reason.
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

    :param successPayouts: Successful payouts.
    :param errorPayouts: Error payouts.
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
