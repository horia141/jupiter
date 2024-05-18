from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.time_plan_associate_with_activities_args import TimePlanAssociateWithActivitiesArgs
from ...models.time_plan_associate_with_activities_result import TimePlanAssociateWithActivitiesResult
from ...types import Response


def _get_kwargs(
    *,
    body: TimePlanAssociateWithActivitiesArgs,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/time-plan-associate-with-activities",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, TimePlanAssociateWithActivitiesResult]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = TimePlanAssociateWithActivitiesResult.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.GONE:
        response_410 = cast(Any, None)
        return response_410
    if response.status_code == HTTPStatus.NOT_ACCEPTABLE:
        response_406 = cast(Any, None)
        return response_406
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = cast(Any, None)
        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, TimePlanAssociateWithActivitiesResult]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: TimePlanAssociateWithActivitiesArgs,
) -> Response[Union[Any, TimePlanAssociateWithActivitiesResult]]:
    """Use case for creating activities starting from already existin activities.

     Use case for creating activities starting from already existin activities.

    Args:
        body (TimePlanAssociateWithActivitiesArgs): Args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, TimePlanAssociateWithActivitiesResult]]
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
    body: TimePlanAssociateWithActivitiesArgs,
) -> Optional[Union[Any, TimePlanAssociateWithActivitiesResult]]:
    """Use case for creating activities starting from already existin activities.

     Use case for creating activities starting from already existin activities.

    Args:
        body (TimePlanAssociateWithActivitiesArgs): Args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, TimePlanAssociateWithActivitiesResult]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: TimePlanAssociateWithActivitiesArgs,
) -> Response[Union[Any, TimePlanAssociateWithActivitiesResult]]:
    """Use case for creating activities starting from already existin activities.

     Use case for creating activities starting from already existin activities.

    Args:
        body (TimePlanAssociateWithActivitiesArgs): Args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, TimePlanAssociateWithActivitiesResult]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: TimePlanAssociateWithActivitiesArgs,
) -> Optional[Union[Any, TimePlanAssociateWithActivitiesResult]]:
    """Use case for creating activities starting from already existin activities.

     Use case for creating activities starting from already existin activities.

    Args:
        body (TimePlanAssociateWithActivitiesArgs): Args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, TimePlanAssociateWithActivitiesResult]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
