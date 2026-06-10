import base64
import json
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings


class PaymentGatewayError(RuntimeError):
    pass


class PayMongoGateway:
    def __init__(self):
        self.secret_key = settings.PAYMONGO_SECRET_KEY.strip()
        self.api_base = settings.PAYMONGO_API_BASE.rstrip("/")
        self.success_url = settings.PAYMONGO_SUCCESS_URL
        self.cancel_url = settings.PAYMONGO_CANCEL_URL

    def is_configured(self):
        return bool(self.secret_key)

    def create_checkout_session(self, order, cart_items):
        if not self.is_configured():
            raise PaymentGatewayError(
                "PayMongo is not configured. Set PAYMONGO_SECRET_KEY to enable card and GCash payments."
            )

        payload = {
            "data": {
                "attributes": {
                    "cancel_url": f"{self.cancel_url}?order_id={order.id}",
                    "success_url": f"{self.success_url}?order_id={order.id}",
                    "payment_method_types": [order.payment_method],
                    "description": f"CLEANLOOK.PH order #{order.id}",
                    "line_items": [
                        *[
                            {
                                "currency": "PHP",
                                "amount": int((item.product.price * item.quantity) * 100),
                                "name": item.product.name,
                                "quantity": item.quantity,
                                "description": item.product.description,
                            }
                            for item in cart_items
                        ],
                        {
                            "currency": "PHP",
                            "amount": int(Decimal("120.00") * 100),
                            "name": "Shipping Fee",
                            "quantity": 1,
                            "description": "Delivery charge",
                        },
                    ],
                    "metadata": {
                        "order_id": str(order.id),
                        "payment_method": order.payment_method,
                    },
                }
            }
        }

        response = self._request("POST", "/checkout_sessions", payload)
        data = response.get("data", {})
        attributes = data.get("attributes", {})

        checkout_url = attributes.get("checkout_url")
        session_id = data.get("id")

        if not checkout_url or not session_id:
            raise PaymentGatewayError("PayMongo did not return a checkout session URL.")

        return {
            "checkout_session_id": session_id,
            "checkout_url": checkout_url,
        }

    def retrieve_checkout_session(self, checkout_session_id):
        if not self.is_configured():
            raise PaymentGatewayError(
                "PayMongo is not configured. Set PAYMONGO_SECRET_KEY to enable payment verification."
            )

        response = self._request("GET", f"/checkout_sessions/{checkout_session_id}")
        data = response.get("data", {})
        attributes = data.get("attributes", {})
        return {
            "id": data.get("id"),
            "payment_status": attributes.get("payment_status"),
            "status": attributes.get("status"),
            "metadata": attributes.get("metadata", {}),
        }

    def _request(self, method, path, payload=None):
        url = f"{self.api_base}{path}"
        body = None

        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        request = Request(url, data=body, method=method)
        auth_token = base64.b64encode(f"{self.secret_key}:".encode("utf-8")).decode("utf-8")
        request.add_header("Authorization", f"Basic {auth_token}")
        request.add_header("Content-Type", "application/json")

        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            error_body = error.read().decode("utf-8") if error.fp else ""
            raise PaymentGatewayError(
                f"PayMongo request failed with status {error.code}: {error_body}"
            ) from error
        except URLError as error:
            raise PaymentGatewayError(f"PayMongo request failed: {error.reason}") from error