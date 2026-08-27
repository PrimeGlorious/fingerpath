class NotificationService:
    def send_email_notification(self, email, message):
        """Send an email notification to a user."""
        if not email:
            raise ValueError("Email is required")

        return {
            "recipient": email,
            "message": message,
            "status": "sent",
        }
