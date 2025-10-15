import json
from pathlib import Path
from typing import Optional

from twikit import Client

cookiesPath = Path('cookies.json')
cookiesJsonPath = Path('cookie.json')


def _apply_tokens(client: Client, cookies: dict) -> None:
    auth_token: Optional[str] = cookies.get('auth_token')
    ct0: Optional[str] = cookies.get('ct0')

    if auth_token and hasattr(client, 'auth_token'):
        client.auth_token = auth_token
    if ct0 and hasattr(client, 'ct0'):
        client.ct0 = ct0


def _load_cookies(client: Client) -> bool:
    if not cookiesPath.exists():
        return False

    try:
        with open(cookiesPath, 'r', encoding='utf-8') as f:
            stored = json.load(f)

        if not isinstance(stored, dict):
            raise ValueError('cookies.json must store a mapping of cookie name to value')

        client.set_cookies(stored, clear_cookies=True)
        _apply_tokens(client, stored)

        print('Loaded cookies from disk')
        return True
    except Exception as exc:
        print(f'Failed to load cookies: {exc}')
        return False


def _import_from_json(client: Client) -> None:
    if not cookiesJsonPath.exists():
        raise RuntimeError(f'{cookiesJsonPath} not found')

    print(f'Loading cookies from {cookiesJsonPath}...')

    with open(cookiesJsonPath, 'r', encoding='utf-8') as f:
        source_cookies = json.load(f)

    if not source_cookies:
        raise RuntimeError('No cookies found in JSON file')

    cookie_map: dict[str, str] = {}

    for cookie in source_cookies:
        domain = cookie.get('domain', '')
        if 'x.com' not in domain and 'twitter.com' not in domain:
            continue

        name = cookie.get('name')
        value = cookie.get('value')

        if not name or value is None:
            continue

        cookie_map[name] = value

    if not cookie_map:
        raise RuntimeError('No X/Twitter cookies found in JSON file')

    with open(cookiesPath, 'w', encoding='utf-8') as f:
        json.dump(cookie_map, f, ensure_ascii=False, indent=2)

    client.set_cookies(cookie_map, clear_cookies=True)
    _apply_tokens(client, cookie_map)

    print(f'Converted {len(cookie_map)} cookies to Twikit format')
    print('Cookies saved to cookies.json\n')


def getClient() -> Client:
    client = Client('en-US')

    if not _load_cookies(client):
        _import_from_json(client)
        if not _load_cookies(client):
            raise RuntimeError('Could not load cookies even after conversion')

    return client