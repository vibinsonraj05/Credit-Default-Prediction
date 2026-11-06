"""
Windows asyncio ProactorEventLoop Fix.
Silences harmless [WinError 10054] ConnectionResetError tracebacks that occur on Windows
when a browser tab is refreshed, navigated away, or disconnected from the Streamlit WebSocket.
"""
import sys


def apply_windows_asyncio_fix() -> None:
    """Patch asyncio._ProactorBasePipeTransport._call_connection_lost on Windows."""
    if sys.platform == "win32":
        try:
            import asyncio.proactor_events

            orig_call_connection_lost = (
                asyncio.proactor_events._ProactorBasePipeTransport._call_connection_lost
            )

            def silent_call_connection_lost(self, exc):
                try:
                    orig_call_connection_lost(self, exc)
                except (ConnectionResetError, OSError):
                    # Gracefully clean up socket resources without noisy console tracebacks
                    try:
                        if hasattr(self, "_sock") and self._sock is not None:
                            self._sock.close()
                            self._sock = None
                    except Exception:
                        pass
                    try:
                        if hasattr(self, "_server") and self._server is not None:
                            self._server._detach(self)
                            self._server = None
                    except Exception:
                        pass
                    self._called_connection_lost = True

            asyncio.proactor_events._ProactorBasePipeTransport._call_connection_lost = (
                silent_call_connection_lost
            )
        except Exception:
            pass


# Automatically execute on import
apply_windows_asyncio_fix()
