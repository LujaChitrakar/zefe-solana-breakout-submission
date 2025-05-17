from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import NetworkingRequest, BaseEvent
from core.services.solana_service import SolanaService
import decimal

class Command(BaseCommand):
    help = 'Process delayed refunds for spam-marked requests after event date'

    def handle(self, *args, **options):
        # Get all past events
        past_events = BaseEvent.objects.filter(ending_date__lt=timezone.now().date())
        
        # Find all spam-marked requests with delayed refunds for these events
        pending_refunds = NetworkingRequest.objects.filter(
            status=NetworkingRequest.STATUS_SPAM,
            is_refund_delayed=True,
            refund_transaction_id__isnull=True,
            event__in=past_events
        )
        
        self.stdout.write(f"Found {pending_refunds.count()} pending refunds to process")
        
        solana_service = SolanaService()
        platform_fee_percentage = decimal.Decimal('0.10')  # 10% fee
        
        for request in pending_refunds:
            try:
                # Calculate refund amount with fee deducted
                refund_amount = request.amount_staked * (1 - platform_fee_percentage)
                
                # Get sender wallet
                sender_wallet = request.sender.wallet.wallet_address
                
                # Process refund
                refund_tx_id = solana_service.process_refund(
                    request.transaction_id, 
                    float(refund_amount), 
                    sender_wallet
                )
                
                if refund_tx_id:
                    # Update request with refund info
                    request.refund_transaction_id = refund_tx_id
                    request.refunded_at = timezone.now()
                    request.is_refund_delayed = False
                    request.save()
                    
                    self.stdout.write(self.style.SUCCESS(
                        f"Processed refund for request {request.id}, refund tx: {refund_tx_id}"
                    ))
                else:
                    self.stdout.write(self.style.ERROR(
                        f"Failed to process refund for request {request.id}"
                    ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Error processing refund for request {request.id}: {str(e)}"
                ))
                
        self.stdout.write(self.style.SUCCESS('Refund processing complete'))