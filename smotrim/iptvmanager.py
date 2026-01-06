"""Implementation of IPTVManager class."""


class IPTVManager:
    """Interface to IPTV Manager."""

    def __init__(self, extra) -> None:
        """Initialize IPTV Manager object."""
        self.extra = extra
        self.port = int(extra.site.params["port"])

    def via_socket(func):  # pylint: disable=no-self-argument
        """Send the output of the wrapped function to socket."""

        def send(self) -> None:
            """Decorator to send data over a socket."""
            import json
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("127.0.0.1", self.port))
            try:
                sock.sendall(json.dumps(func(self)).encode())  # pylint: disable=not-callable
            finally:
                sock.close()

        return send

    @via_socket
    def send_channels(self):  # pylint: disable=no-method-argument,no-self-use
        """Return JSON-STREAMS formatted information to IPTV Manager."""
        return {"version": 1, "streams": self.extra.export_channels()}

    @via_socket
    def send_epg(self):  # pylint: disable=no-method-argument,no-self-use
        """Return JSON-EPG formatted information to IPTV Manager."""
        return {"version": 1, "epg": self.extra.export_tv_guide()}
