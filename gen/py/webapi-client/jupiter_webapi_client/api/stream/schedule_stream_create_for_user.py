from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.schedule_stream_create_for_user_args import ScheduleStreamCreateForUserArgs
from ...models.schedule_stream_create_for_user_result import ScheduleStreamCreateForUserResult
from ...types import Response


def _get_kwargs(
    *,
    body: ScheduleStreamCreateForUserArgs,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/schedule-stream-create-for-user",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ScheduleStreamCreateForUserResult]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ScheduleStreamCreateForUserResult.from_dict(response.json())

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
) -> Response[Union[Any, ScheduleStreamCreateForUserResult]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: ScheduleStreamCreateForUserArgs,
) -> Response[Union[Any, ScheduleStreamCreateForUserResult]]:
    """Use case for creating a schedule stream.

     Use case for creating a schedule stream.

    Args:
        body (ScheduleStreamCreateForUserArgs): Args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ScheduleStreamCreateForUserResult]]
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
    body: ScheduleStreamCreateForUserArgs,
) -> Optional[Union[Any, ScheduleStreamCreateForUserResult]]:
    """Use case for creating a schedule stream.

     Use case for creating a schedule stream.

    Args:
        body (ScheduleStreamCreateForUserArgs): Args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ScheduleStreamCreateForUserResult]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: ScheduleStreamCreateForUserArgs,
) -> Response[Union[Any, ScheduleStreamCreateForUserResult]]:
    """Use case for creating a schedule stream.

     Use case for creating a schedule stream.

    Args:
        body (ScheduleStreamCreateForUserArgs): Args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ScheduleStreamCreateForUserResult]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: ScheduleStreamCreateForUserArgs,
) -> Optional[Union[Any, ScheduleStreamCreateForUserResult]]:
    """Use case for creating a schedule stream.

     Use case for creating a schedule stream.

    Args:
        body (ScheduleStreamCreateForUserArgs): Args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ScheduleStreamCreateForUserResult]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
