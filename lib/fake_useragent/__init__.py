"""Up-to-date simple useragent faker with real world database."""

from .errors import FakeUserAgentError, UserAgentError
from .fake import FakeUserAgent, UserAgent
from .get_version import __version__

__all__ = [
    "FakeUserAgent",
    "FakeUserAgentError",
    "UserAgent",
    "UserAgentError",
    "__version__",
]
