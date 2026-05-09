from functools import wraps
from flask import flash, redirect, session, url_for


def login_required(view):
    """Redirect users to login before they can access private routes."""
    @wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user_id") is None:
            flash("Please log in to access your studio workspace.", "error")
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


def money(value):
    """Format money values consistently for templates."""
    try:
        amount = float(value or 0)
    except (TypeError, ValueError):
        amount = 0
    return f"${amount:,.2f}"


def to_float(value, default=0):
    """Return a non-negative float for form fields."""
    try:
        number = float(value or default)
    except (TypeError, ValueError):
        return default
    return max(number, 0)
