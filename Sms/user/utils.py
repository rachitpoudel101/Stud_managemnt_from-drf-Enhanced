def format_username(username):
    """Capitalize the first letter of the username."""
    return username.capitalize()

def log_action(user, action):
    """Log actions performed by users (simplified)."""
    print(f"[ACTION LOG] {user.username} performed {action}")
