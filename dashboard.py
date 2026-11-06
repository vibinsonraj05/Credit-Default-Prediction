"""
Legacy dashboard module shim for backward compatibility.
Delegates to frontend.views.dashboard_view.
"""
from backend.services.auth_service import get_current_user, logout_user
from frontend.views.dashboard_view import render_dashboard_view


def logout():
    """Backward compatible wrapper for logout."""
    logout_user()


def show_dashboard():
    """Backward compatible wrapper for dashboard view."""
    user = get_current_user()
    if user:
        render_dashboard_view(user)
