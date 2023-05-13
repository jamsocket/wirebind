from __future__ import annotations

from typing import Optional


def expose(name: Optional[str] = None):
    def decorator(func):
        func._exposed_as = name or func.__name__
        return func

    return decorator
