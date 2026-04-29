"""Application-wide rate limiter.

Defined in its own module so routers and the application factory can
share the same Limiter instance without circular imports.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Per-IP limiter; default_limits left empty so endpoints opt in via the
# `@limiter.limit(...)` decorator. The in-memory storage is fine for a
# single-process deployment; switch to a redis storage_uri if you scale
# horizontally.
limiter = Limiter(key_func=get_remote_address, default_limits=[])
