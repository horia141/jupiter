from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.load_top_level_info_args import LoadTopLevelInfoArgs
from ...models.load_top_level_info_result import LoadTopLevelInfoResult
from ...types import Response


def _get_kwargs(
    *,
    body: LoadTopLevelInfoArgs,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/load-top-level-info",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, LoadTopLevelInfoResult]]:
    if response.status_code == 200:
        response_200 = LoadTopLevelInfoResult.from_dict(response.json())

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
) -> Response[Union[Any, LoadTopLevelInfoResult]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: LoadTopLevelInfoArgs,
) -> Response[Union[Any, LoadTopLevelInfoResult]]:
    """The command for loading a user and workspace if they exist and other data too.

     The command for loading a user and workspace if they exist and other data too.

    Args:
        body (LoadTopLevelInfoArgs): Load user and workspsace args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, LoadTopLevelInfoResult]]
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
    body: LoadTopLevelInfoArgs,
) -> Optional[Union[Any, LoadTopLevelInfoResult]]:
    """The command for loading a user and workspace if they exist and other data too.

     The command for loading a user and workspace if they exist and other data too.

    Args:
        body (LoadTopLevelInfoArgs): Load user and workspsace args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, LoadTopLevelInfoResult]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: LoadTopLevelInfoArgs,
) -> Response[Union[Any, LoadTopLevelInfoResult]]:
    """The command for loading a user and workspace if they exist and other data too.

     The command for loading a user and workspace if they exist and other data too.

    Args:
        body (LoadTopLevelInfoArgs): Load user and workspsace args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, LoadTopLevelInfoResult]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: LoadTopLevelInfoArgs,
) -> Optional[Union[Any, LoadTopLevelInfoResult]]:
    """The command for loading a user and workspace if they exist and other data too.

     The command for loading a user and workspace if they exist and other data too.

    Args:
        body (LoadTopLevelInfoArgs): Load user and workspsace args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, LoadTopLevelInfoResult]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
