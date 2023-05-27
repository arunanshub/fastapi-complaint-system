from __future__ import annotations

import typing
import uuid
from functools import lru_cache

import simplejson as json
from apiron import JsonEndpoint, Service
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from requests import HTTPError

from .. import exc
from ..core import settings
from ..models.base import Monetary  # noqa: TC002

T = typing.TypeVar("T", bound="WiseService")


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
    cancel_transfer = JsonEndpoint(
        path="/v1/transfers/{transfer_id}/cancel", default_method="PUT"
    )
    fund_transfer = JsonEndpoint(
        path="/v3/profiles/{profile_id}/transfers/{transfer_id}/payments",
        default_method="POST",
    )


class Transaction(BaseModel):
    quote_id: uuid.UUID
    transfer_id: int
    target_account_id: int
    amount: Monetary


class WiseService:
    def __init__(self) -> None:
        self._wise = WiseSDK()
        self._profile_id = self.get_profile_id()

    def get_profile_id(self) -> int:
        # wise returns two types of profiles: personal and business
        profile_resp = self._wise.profiles()
        _, business = typing.cast("list[dict]", profile_resp)
        self._profile_id = typing.cast("int", business["id"])
        return self._profile_id

    @property
    async def profile_id(self) -> int:
        return self._profile_id

    async def create_quote(self, amount: Monetary) -> str:
        """
        Creates a quote and returns the Quote ID as UUID.
        """
        quote_data = {
            "sourceCurrency": "EUR",
            "targetCurrency": "EUR",
            "targetAmount": amount,
        }

        quote_resp = await run_in_threadpool(
            self._wise.create_authenticated_quote,
            profile_id=await self.profile_id,
            data=json.dumps(quote_data),
        )
        quote_resp = typing.cast("dict", quote_resp)
        return typing.cast("str", quote_resp["id"])

    async def create_recipient_account(self, full_name: str, iban: str) -> int:
        recipient_data = {
            "currency": "EUR",
            "type": "iban",
            "profile": await self.profile_id,
            "accountHolderName": full_name,
            "details": {
                "legalType": "PRIVATE",
                "iban": iban,
            },
        }

        recipient_resp = await run_in_threadpool(
            self._wise.create_recipient_account,
            data=json.dumps(recipient_data),
        )
        recipient_resp = typing.cast("dict", recipient_resp)
        return typing.cast("int", recipient_resp["id"])

    async def create_transfer(
        self, target_account_id: int, quote_uuid: str
    ) -> int:
        transfer_data = {
            "targetAccount": target_account_id,
            "quoteUuid": quote_uuid,
            "customerTransactionId": str(uuid.uuid4()),
        }
        transfer_resp = await run_in_threadpool(
            self._wise.create_transfer,
            data=json.dumps(transfer_data),
        )
        transfer_resp = typing.cast("dict", transfer_resp)
        return typing.cast("int", transfer_resp["id"])

    async def cancel_transfer(self, transfer_id: int) -> None:
        try:
            await run_in_threadpool(
                self._wise.cancel_transfer,
                transfer_id=transfer_id,
            )
        except HTTPError as e:
            msg = "Transaction has already been cancelled"
            raise exc.CancelledTransactionError(msg) from e

    async def issue_transaction(
        self,
        user_name: str,
        iban: str,
        amount: Monetary,
    ) -> Transaction:
        target_account_id = await self.create_recipient_account(
            user_name, iban
        )
        quote_id = await self.create_quote(amount)
        transfer_id = await self.create_transfer(target_account_id, quote_id)
        return Transaction(
            quote_id=uuid.UUID(quote_id),
            transfer_id=transfer_id,
            target_account_id=target_account_id,
            amount=amount,
        )

    async def fund_transfer(self, transfer_id: int) -> None:
        transfer_data = {"type": "BALANCE"}
        try:
            await run_in_threadpool(
                self._wise.fund_transfer,
                profile_id=await self.profile_id,
                transfer_id=transfer_id,
                data=json.dumps(transfer_data),
            )
        except HTTPError as e:
            error_resp = e.response.json()
            if error_resp != "COMPLETED":
                msg = f"Transaction with id {transfer_id} failed"
                raise exc.FailedTransactionError(msg) from e
            raise e


@lru_cache
def _get_cached_wise_service() -> WiseService:
    return WiseService()


async def get_wise() -> typing.AsyncIterable[WiseService]:
    yield _get_cached_wise_service()
