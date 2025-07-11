# errors.py

import requests
from typing import Callable, Any
from exceptions import RevcontentError
import json


def api_error_handler(error_type=RevcontentError):
    """
    Decorator factory for handling and raising custom Revcontent exceptions.
    Prints response JSON (if any) from API on HTTP errors.
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.HTTPError as err:
                response = getattr(err, 'response', None)
                if response is not None:
                    print(f"HTTP {response.status_code} error: {response.reason}")
                    # Пробуем красиво вывести JSON
                    try:
                        error_json = response.json()
                        print("API response JSON:\n" + json.dumps(error_json, indent=2,
                                                                  ensure_ascii=False))
                    except Exception:
                        print("Response text:", response.text)
                    raise error_type(f"{err}\n{response.text}") from err
                else:
                    raise error_type(str(err)) from err
            except requests.exceptions.RequestException as err:
                raise error_type(str(err)) from err
            except Exception as err:
                raise error_type(str(err)) from err

        return wrapper

    return decorator
