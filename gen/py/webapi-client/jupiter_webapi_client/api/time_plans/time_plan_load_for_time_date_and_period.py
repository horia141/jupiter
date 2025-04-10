from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.time_plan_load_for_date_and_period_args import TimePlanLoadForDateAndPeriodArgs
from ...models.time_plan_load_for_date_and_period_result import TimePlanLoadForDateAndPeriodResult
from ...types import Response


def _get_kwargs(
    *,
    body: TimePlanLoadForDateAndPeriodArgs,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/time-plan-load-for-time-date-and-period",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, TimePlanLoadForDateAndPeriodResult]]:
    if response.status_code == 200:
        response_200 = TimePlanLoadForDateAndPeriodResult.from_dict(response.json())

        return response_200
    if response.status_code == 410:
        response_410 = cast(Any, None)
        return response_410
    if response.status_code == 406:
        response_406 = cast(Any, None)
        return response_406
    if response.status_code == 422:
        response_422 = cast(Any, None)
        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, TimePlanLoadForDateAndPeriodResult]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: TimePlanLoadForDateAndPeriodArgs,
) -> Response[Union[Any, TimePlanLoadForDateAndPeriodResult]]:
    """The command for loading details about a time plan.

     The command for loading details about a time plan.

    Args:
        body (TimePlanLoadForDateAndPeriodArgs): Args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, TimePlanLoadForDateAndPeriodResult]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: TimePlanLoadForDateAndPeriodArgs,
) -> Optional[Union[Any, TimePlanLoadForDateAndPeriodResult]]:
    """The command for loading details about a time plan.

     The command for loading details about a time plan.

    Args:
        body (TimePlanLoadForDateAndPeriodArgs): Args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, TimePlanLoadForDateAndPeriodResult]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: TimePlanLoadForDateAndPeriodArgs,
) -> Response[Union[Any, TimePlanLoadForDateAndPeriodResult]]:
    """The command for loading details about a time plan.

     The command for loading details about a time plan.

    Args:
        body (TimePlanLoadForDateAndPeriodArgs): Args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, TimePlanLoadForDateAndPeriodResult]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: TimePlanLoadForDateAndPeriodArgs,
) -> Optional[Union[Any, TimePlanLoadForDateAndPeriodResult]]:
    """The command for loading details about a time plan.

     The command for loading details about a time plan.

    Args:
        body (TimePlanLoadForDateAndPeriodArgs): Args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, TimePlanLoadForDateAndPeriodResult]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
