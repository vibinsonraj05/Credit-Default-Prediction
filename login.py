"""
Legacy login module shim for backward compatibility.
Delegates to frontend.views.login_view.
"""
from frontend.views.login_view import render_login_view


def show_login():
    """Backward compatible wrapper for login view."""
    render_login_view()
