from __future__ import annotations

import typing
import uuid
from functools import lru_cache

import simplejson as json
from apiron import JsonEndpoint, Service
from requests import HTTPError

from .. import exc
from ..core import settings

if typing.TYPE_CHECKING:
    from decimal import Decimal


class WiseSDK(Service):
    @property
    def required_headers(cls) -> dict[str, str]:  # type: ignore[override]
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.WISE_TOKEN}",
        }

    domain = settings.WISE_ENDPOINT
    profiles = JsonEndpoint(path="/v1/profiles")
    create_authenticated_quote = JsonEndpoint(
        path="/v3/profiles/{profile_id}/quotes",
        default_method="POST",
    )
    create_recipient_account = JsonEndpoint(
        path="/v1/accounts", default_method="POST"
    )
    create_transfer = JsonEndpoint(path="/v1/transfers", default_method="POST")
    fund_transfer = JsonEndpoint(
        path="/v3/profiles/{profile_id}/transfers/{transfer_id}/payments",
        default_method="POST",
    )


class WiseService:
    def __init__(self) -> None:
        self._wise = WiseSDK()
        self._profile_id = self.get_profile_id()

    def get_profile_id(self) -> int:
        # wise returns two types of profiles: personal and business
        _, business = typing.cast("list[dict]", self._wise.profiles())
        return typing.cast("int", business["id"])

    def create_quote(self, amount: Decimal) -> str:
        """
        Creates a quote and returns the Quote ID as UUID.
        """
        quote_data = {
            "sourceCurrency": "EUR",
            "targetCurrency": "EUR",
            "targetAmount": amount,
        }

        quote_resp = self._wise.create_authenticated_quote(
            profile_id=self._profile_id,
            data=json.dumps(quote_data),
        )
        quote_resp = typing.cast("dict", quote_resp)
        return typing.cast("str", quote_resp["id"])

    def create_recipient_account(self, full_name: str, iban: str) -> int:
        recipient_data = {
            "currency": "EUR",
            "type": "iban",
            "profile": self._profile_id,
            "accountHolderName": full_name,
            "details": {
                "legalType": "PRIVATE",
                "iban": iban,
            },
        }

        recipient_resp = self._wise.create_recipient_account(
            data=json.dumps(recipient_data)
        )
        recipient_resp = typing.cast("dict", recipient_resp)
        return typing.cast("int", recipient_resp["id"])

    def create_transfer(self, target_account_id: int, quote_uuid: str) -> int:
        transfer_data = {
            "targetAccount": target_account_id,
            "quoteUuid": quote_uuid,
            "customerTransactionId": str(uuid.uuid4()),
        }
        transfer_resp = self._wise.create_transfer(
            data=json.dumps(transfer_data)
        )
        transfer_resp = typing.cast("dict", transfer_resp)
        return typing.cast("int", transfer_resp["id"])

    def fund_transfer(self, transfer_id: int) -> None:
        transfer_data = {"type": "BALANCE"}
        try:
            self._wise.fund_transfer(
                profile_id=self._profile_id,
                transfer_id=transfer_id,
                data=json.dumps(transfer_data),
            )
        except HTTPError as e:
            error_resp = e.response.json()
            if error_resp != "COMPLETED":
                raise exc.FailedTransactionError(
                    f"Transaction with id {transfer_id} failed"
                ) from e
            raise e


@lru_cache
def _get_cached_wise_service() -> WiseService:
    return WiseService()


def get_wise() -> typing.Iterable[WiseService]:
    yield _get_cached_wise_service()
