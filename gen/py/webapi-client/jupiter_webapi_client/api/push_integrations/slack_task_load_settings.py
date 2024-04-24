from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.slack_task_load_settings_args import SlackTaskLoadSettingsArgs
from ...models.slack_task_load_settings_result import SlackTaskLoadSettingsResult
from ...types import Response


def _get_kwargs(
    *,
    body: SlackTaskLoadSettingsArgs,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/slack-task-load-settings",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, SlackTaskLoadSettingsResult]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = SlackTaskLoadSettingsResult.from_dict(response.json())

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
) -> Response[Union[Any, SlackTaskLoadSettingsResult]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: SlackTaskLoadSettingsArgs,
) -> Response[Union[Any, SlackTaskLoadSettingsResult]]:
    """The command for loading the settings around slack tasks.

     The command for loading the settings around slack tasks.

    Args:
        body (SlackTaskLoadSettingsArgs): SlackTaskLoadSettings args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SlackTaskLoadSettingsResult]]
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
    body: SlackTaskLoadSettingsArgs,
) -> Optional[Union[Any, SlackTaskLoadSettingsResult]]:
    """The command for loading the settings around slack tasks.

     The command for loading the settings around slack tasks.

    Args:
        body (SlackTaskLoadSettingsArgs): SlackTaskLoadSettings args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SlackTaskLoadSettingsResult]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: SlackTaskLoadSettingsArgs,
) -> Response[Union[Any, SlackTaskLoadSettingsResult]]:
    """The command for loading the settings around slack tasks.

     The command for loading the settings around slack tasks.

    Args:
        body (SlackTaskLoadSettingsArgs): SlackTaskLoadSettings args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SlackTaskLoadSettingsResult]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: SlackTaskLoadSettingsArgs,
) -> Optional[Union[Any, SlackTaskLoadSettingsResult]]:
    """The command for loading the settings around slack tasks.

     The command for loading the settings around slack tasks.

    Args:
        body (SlackTaskLoadSettingsArgs): SlackTaskLoadSettings args.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SlackTaskLoadSettingsResult]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed