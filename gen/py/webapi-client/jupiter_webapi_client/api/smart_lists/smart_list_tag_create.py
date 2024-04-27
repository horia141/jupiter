from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.smart_list_tag_create_args import SmartListTagCreateArgs
from ...models.smart_list_tag_create_result import SmartListTagCreateResult
from ...types import Response


def _get_kwargs(
    *,
    body: SmartListTagCreateArgs,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/smart-list-tag-create",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, SmartListTagCreateResult]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = SmartListTagCreateResult.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = cast(Any, None)
        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, SmartListTagCreateResult]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: SmartListTagCreateArgs,
) -> Response[Union[Any, SmartListTagCreateResult]]:
    """The command for creating a smart list tag.

     The command for creating a smart list tag.

    Args:
        body (SmartListTagCreateArgs): SmartListTagCreate args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SmartListTagCreateResult]]
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
    body: SmartListTagCreateArgs,
) -> Optional[Union[Any, SmartListTagCreateResult]]:
    """The command for creating a smart list tag.

     The command for creating a smart list tag.

    Args:
        body (SmartListTagCreateArgs): SmartListTagCreate args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SmartListTagCreateResult]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: SmartListTagCreateArgs,
) -> Response[Union[Any, SmartListTagCreateResult]]:
    """The command for creating a smart list tag.

     The command for creating a smart list tag.

    Args:
        body (SmartListTagCreateArgs): SmartListTagCreate args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SmartListTagCreateResult]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: SmartListTagCreateArgs,
) -> Optional[Union[Any, SmartListTagCreateResult]]:
    """The command for creating a smart list tag.

     The command for creating a smart list tag.

    Args:
        body (SmartListTagCreateArgs): SmartListTagCreate args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SmartListTagCreateResult]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
