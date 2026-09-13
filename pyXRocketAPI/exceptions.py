class xRocketAPIException(Exception):
    """An HTTP or transport failure returned while calling xRocket Pay."""

    def __init__(
        self,
        message: str,
        status: int | None = None,
        problem_type: str | None = None,
        title: str | None = None,
        detail: str | None = None,
        instance: str | None = None,
        kind: str | None = None,
        info: object | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.problem_type = problem_type
        self.title = title
        self.detail = detail
        self.instance = instance
        self.kind = kind
        self.info = info


class xRocketWebhookException(ValueError):
    """Base class for errors while validating or parsing an xRocket webhook."""


class xRocketWebhookParseException(xRocketWebhookException):
    """Webhook body is not valid JSON or does not have the expected structure."""


class xRocketWebhookSignatureException(xRocketWebhookException):
    """Webhook signature is absent or does not match the supplied secret."""


class xRocketWebhookUnsupportedVersionException(xRocketWebhookSignatureException):
    """Webhook uses a signature scheme version unsupported by this library."""
