from django.db import models
from core.utils import BaseModel, DateTimeAbstractModel
from user.models import User

# kathmandu meetup

class BaseEvent(BaseModel):
    """
    The canonical base event shared across users.
    """
    name = models.CharField(max_length=150, null=True, blank=True)
    code = models.SlugField(max_length=100, unique=False)  # new slug-like identifier
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    starting_date = models.DateField(null=True, blank=True)
    ending_date = models.DateField(null=True, blank=True)
    created_by_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.code})"


class UserEvent(BaseModel):
    """
    User-specific perspective or participation in an event.
    Users can personalize event titles, descriptions, and attach codes.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    base_event = models.ForeignKey(BaseEvent, on_delete=models.CASCADE, related_name='user_events')
    title = models.CharField(max_length=200)  # User's custom title for the event
    description = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'base_event'], name='unique_user_event_view')
        ]

    def __str__(self):
        return f"{self.title} — {self.user}"


class UserNetwork(DateTimeAbstractModel):
    """
    Represents a connection between two users at an event.
    'scanner' is the user who scanned the QR code.
    'scanned' is the user whose QR was scanned. scanner_user_id, scanned_user_id
    """
    scanner_event_title = models.CharField(max_length=200, null=True, blank=True)  # User's custom title for the event
    scanned_event_title = models.CharField(max_length=200, null=True, blank=True)  # User's custom title for the event
    scanner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scanned_others')
    scanned = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scanned_by_others')
    meeting_date = models.DateTimeField(auto_now_add=True)
    base_event = models.ForeignKey(BaseEvent, on_delete=models.CASCADE, related_name="event_networks", null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['scanner', 'scanned'], name='unique_network_connection')
        ]

    def __str__(self):
        return f"{self.scanner.username} scanned {self.scanned.username} at {self.base_event.name if self.base_event else 'Unknown Event'}"
    
class MeetingInformation(DateTimeAbstractModel):
    """
    This store the images of the meeting.. Meeting objec can have multiple images
    """
    network = models.ForeignKey(UserNetwork, on_delete=models.CASCADE, related_name='images')
    summary_note = models.TextField(blank=True, null=True)
    information_saved_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users_saved_meeting_informations')

    def __str__(self):
        return f'{self.network} information'
    

class MeetingImage(DateTimeAbstractModel):
    meeting_information = models.ForeignKey(MeetingInformation, on_delete=models.CASCADE, related_name="meeting_images")
    note = models.TextField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)


    def __str__(self):
        return f'{self.note} image'

class WalletConnection(BaseModel):
    """Store user wallet information for Solana transactions"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    wallet_address = models.CharField(max_length=255, unique=True)
    last_connected = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Wallet for {self.user.name or self.user.username}"
class NetworkingRequest(BaseModel):
    """Pre-networking connection requests with SOL staking"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    note_content = models.TextField()
    
    # Blockchain fields for reliable transaction handling
    request_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    sender_wallet = models.CharField(max_length=44, blank=True, null=True)
    receiver_wallet = models.CharField(max_length=44, blank=True, null=True)
    escrow_account = models.CharField(max_length=44, blank=True, null=True)
    tx_signature = models.CharField(max_length=88, blank=True, null=True)
    
    # Make blockchain fields optional
    transaction_id = models.CharField(max_length=255, blank=True, null=True)  # Optional Solana transaction ID
    amount_staked = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)  # Optional SOL amount
    
    # Status options
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_SPAM = 'spam'
    STATUS_REMOVED = 'removed' 
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_SPAM, 'Spam'),
         (STATUS_REMOVED, 'Removed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    
    # For tracking refunds - also make optional
    refund_transaction_id = models.CharField(max_length=255, null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    # For spam tracking
    is_refund_delayed = models.BooleanField(default=False)
    event = models.ForeignKey(BaseEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name='networking_requests')
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['sender', 'receiver', 'status'],
                condition=models.Q(status='pending'),
                name='unique_pending_request'
            )
        ]
    
    def __str__(self):
        return f"Request from {self.sender} to {self.receiver} ({self.get_status_display()})"


class SpamReport(BaseModel):
    """Track spam reports for users"""
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='spam_reports')
    report_count = models.IntegerField(default=0)
    is_banned = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.reported_user} - Reports: {self.report_count} - {'BANNED' if self.is_banned else 'Active'}"  

