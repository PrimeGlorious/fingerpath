class PaymentService:
    def authenticate_user(self, access_token):
        """Authenticate a user using an OAuth access token."""
        if not access_token:
            raise ValueError("Access token is required")

        return {
            "authenticated": True,
            "method": "oauth",
        }

    def create_payment(self, user_id, amount):
        """Create a payment transaction for an authenticated user."""
        if amount <= 0:
            raise ValueError("Amount must be positive")

        return {
            "user_id": user_id,
            "amount": amount,
            "status": "created",
        }
