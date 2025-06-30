# def format_username(username):
#     """Capitalize the first letter of the username."""
#     return username.capitalize()

def log_action(user, action, details=None):
    """Log actions performed by users (simplified)."""
    msg = f"[ACTION LOG] {user.username} performed {action}"
    if details:
        msg += f" | Details: {details}"
    print(msg)
