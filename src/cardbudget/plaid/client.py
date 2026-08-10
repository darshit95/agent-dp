from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import httpx

from cardbudget.errors import CardBudgetError


class PlaidAPIError(CardBudgetError):
    def __init__(self, *, error_code: str = "PLAID_ERROR", error_type: str = "API_ERROR", message: str = "Plaid request failed.") -> None:
        super().__init__(message)
        self.error_code = error_code
        self.error_type = error_type


class PlaidTransport(Protocol):
    def post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]: ...


@dataclass
class HTTPPlaidTransport:
    client_id: str
    secret: str
    environment: str = "sandbox"
    timeout_seconds: float = 20.0

    @property
    def base_url(self) -> str:
        if self.environment == "sandbox":
            return "https://sandbox.plaid.com"
        if self.environment == "production":
            return "https://production.plaid.com"
        raise ValueError("Unsupported Plaid environment.")

    def post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = dict(payload)
        body["client_id"] = self.client_id
        body["secret"] = self.secret
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(f"{self.base_url}{path}", json=body)
        except httpx.HTTPError as exc:
            raise PlaidAPIError(error_code="NETWORK_ERROR", message="Unable to reach Plaid.") from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise PlaidAPIError(error_code="INVALID_RESPONSE", message="Plaid returned an invalid response.") from exc

        if response.is_error or "error_code" in data:
            raise PlaidAPIError(
                error_code=str(data.get("error_code") or f"HTTP_{response.status_code}"),
                error_type=str(data.get("error_type") or "API_ERROR"),
                message="Plaid request failed.",
            )
        return data


class PlaidClient:
    def __init__(self, transport: PlaidTransport) -> None:
        self.transport = transport

    def create_link_token(self, *, client_user_id: str) -> str:
        response = self.transport.post(
            "/link/token/create",
            {
                "user": {"client_user_id": client_user_id},
                "client_name": "PocketTrack",
                "products": ["transactions"],
                "country_codes": ["US"],
                "language": "en",
                "transactions": {"days_requested": 120},
                "account_filters": {"credit": {"account_subtypes": ["credit card"]}},
            },
        )
        return str(response["link_token"])

    def create_update_link_token(self, *, client_user_id: str, access_token: str) -> str:
        response = self.transport.post(
            "/link/token/create",
            {
                "user": {"client_user_id": client_user_id},
                "client_name": "PocketTrack",
                "country_codes": ["US"],
                "language": "en",
                "access_token": access_token,
            },
        )
        return str(response["link_token"])

    def exchange_public_token(self, public_token: str) -> tuple[str, str]:
        response = self.transport.post(
            "/item/public_token/exchange",
            {"public_token": public_token},
        )
        return str(response["access_token"]), str(response["item_id"])

    def get_item(self, access_token: str) -> dict[str, Any]:
        return self.transport.post("/item/get", {"access_token": access_token})

    def get_accounts(self, access_token: str) -> list[dict[str, Any]]:
        response = self.transport.post("/accounts/get", {"access_token": access_token})
        return list(response.get("accounts") or [])

    def sync_transactions(self, access_token: str, cursor: str | None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "access_token": access_token,
            "count": 500,
        }
        if cursor:
            payload["cursor"] = cursor
        payload["options"] = {"personal_finance_category_version": "v2"}
        return self.transport.post("/transactions/sync", payload)

    def get_transactions(
        self,
        access_token: str,
        start_date: str,
        end_date: str,
        *,
        offset: int = 0,
        count: int = 500,
    ) -> dict[str, Any]:
        return self.transport.post(
            "/transactions/get",
            {
                "access_token": access_token,
                "start_date": start_date,
                "end_date": end_date,
                "options": {
                    "count": min(max(int(count), 1), 500),
                    "offset": max(int(offset), 0),
                    "personal_finance_category_version": "v2",
                },
            },
        )
