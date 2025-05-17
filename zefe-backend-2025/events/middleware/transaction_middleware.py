from core.services.solana_service import SolanaService
from rest_framework.exceptions import ValidationError
import json

class SolanaTransactionMiddleware:
    """Middleware to validate Solana transactions in requests"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.solana_service = SolanaService()
        
    def __call__(self, request):
        # Only process POST requests to networking request creation endpoint
        if request.method == "POST" and request.path.endswith("/networking/send-request/"):
            try:
                # Parse request body as JSON
                if request.body:
                    body_data = json.loads(request.body)
                    
                    # Extract transaction data
                    transaction_id = body_data.get("transaction_id")
                    amount_staked = body_data.get("amount_staked")
                    platform_wallet = "YourPlatformWalletAddressHere"  # Replace with actual platform wallet
                    
                    # Verify the transaction
                    if transaction_id and amount_staked:
                        if not self.solana_service.verify_transaction(
                            transaction_id=transaction_id,
                            amount=float(amount_staked),
                            recipient=platform_wallet
                        ):
                            raise ValidationError(
                                "Invalid Solana transaction. Please ensure the transaction is confirmed and matches the required amount."
                            )
            except json.JSONDecodeError:
                # Handle invalid JSON
                pass
            except Exception as e:
                # Log the error but don't block the request
                print(f"Transaction verification error: {str(e)}")
        
        response = self.get_response(request)
        return response