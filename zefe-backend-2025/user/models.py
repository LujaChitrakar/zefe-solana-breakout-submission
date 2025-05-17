from django.db import models

# Create your models here.
#Stdlib import
import uuid

#django core import
from django.db import models
from django.contrib.auth.models import AbstractUser

#app import
from core.utils import BaseModel
from .managers import CustomUserManager

import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model supporting both Telegram login and email login for admins.

    """

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, null=True, blank=True)  # Used by admins
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)  # Used by Telegram users
    name = models.CharField(max_length=400, null=True, blank=True)
    username = models.CharField(max_length=150, null=True, blank=True)  # Optional Telegram username
    photo_url = models.URLField(max_length=2000, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)  # Admin users have staff access

    objects = CustomUserManager()

    USERNAME_FIELD = "email"  # Default login is by email (for admins)
    REQUIRED_FIELDS = []  # Superusers must provide an email

    def __str__(self):
        return self.email if self.email else f"Telegram User {self.telegram_id}-{self.name}"

    
    USER_SOURCE_CHOICES = [
        ('WEB', 'Web Application'),
        ('TELEGRAM', 'Telegram Mini App'),
        ('ADMIN', 'Admin Created'),
    ]
    source = models.CharField(
        max_length=20, 
        choices=USER_SOURCE_CHOICES,
        default='WEB',
        db_index=True,  # Add index for faster filtering
        help_text="Platform where the user registered from"
    )
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

   

class Position(BaseModel):
    name = models.CharField(max_length=100)
    code=models.CharField(max_length=10)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class Field(BaseModel):
    name = models.CharField(max_length=100)
    code=models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
    

class UserProfile(BaseModel):

    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

    GENDER_TYPE = [
        (MALE, "Male"),
        (FEMALE, "Female"),
        (OTHER, "Other"),
    ]

    USER_POSITION = [
        ("ADVISOR", "Advisor"),
        ("AMBASSADOR", "Ambassador"),
        ("ANALYST", "Analyst"),
        ("AUDITOR", "Auditor"),
        ("BLOCKCHAIN_ARCHITECT", "Blockchain Architect"),
        ("BLOCKCHAIN_DEVELOPER", "Blockchain Developer"),
        ("COMMUNITY_MANAGER", "Community Manager"),
        ("CO_FOUNDER", "Co-Founder"),
        ("CURATOR", "Curator"),
        ("DATA_ANALYST", "Data Analyst"),
        ("DESIGNER", "Designer"),
        ("DEVELOPER", "Developer"),
        ("DEVOPS_ENGINEER", "DevOps Engineer"),
        ("DAPP_DEVELOPER", "dApp Developer"),
        ("ECOSYSTEM_LEAD", "Ecosystem Lead"),
        ("ENGINEER", "Engineer"),
        ("ETHICAL_HACKER", "Ethical Hacker"),
        ("FULL_STACK_DEVELOPER", "Full-Stack Developer"),
        ("GAME_DESIGNER", "Game Designer"),
        ("GRAPHIC_DESIGNER", "Graphic Designer"),
        ("HOST", "Host"),
        ("INFRASTRUCTURE_ENGINEER", "Infrastructure Engineer"),
        ("INTERN", "Intern"),
        ("INVESTOR", "Investor"),
        ("KOL", "KOL"),
        ("LEGAL_CONSULTANT", "Legal Consultant"),
        ("MARKETER", "Marketer"),
        ("METAVERSE_ARCHITECT", "Metaverse Architect"),
        ("MODERATOR", "Moderator"),
        ("NFT_SPECIALIST", "NFT Specialist"),
        ("EVENT_ORGANIZER", "Event Organizer"),
        ("PRODUCT_MANAGER", "Product Manager"),
        ("PROJECT_MANAGER", "Project Manager"),
        ("PROTOCOL_DEVELOPER", "Protocol Developer"),
        ("RESEARCHER", "Researcher"),
        ("SECURITY_ENGINEER", "Security Engineer"),
        ("SMART_CONTRACT_DEVELOPER", "Smart Contract Developer"),
        ("SOCIAL_MEDIA_MANAGER", "Social Media Manager"),
        ("STRATEGIST", "Strategist"),
        ("TOKENOMICS_STRATEGIST", "Tokenomics Strategist"),
        ("TRADER", "Trader"),
        ("VALIDATOR", "Validator"),
        ("VENTURE_CAPITALIST", "Venture Capitalist"),
        ("CONSULTANT", "Consultant"),
    ]
    # Add this after the CHAIN_ECOSYSTEM list in user/models.py
    CITY_OPTIONS = [
        ("ABU_DHABI", "Abu Dhabi"),
        ("AMSTERDAM", "Amsterdam"),
        ("AUSTIN", "Austin"),
        ("BALI", "Bali"),
        ("BANGALORE", "Bangalore"),
        ("BANGKOK", "Bangkok"),
        ("BARCELONA", "Barcelona"),
        ("BELGRADE", "Belgrade"),
        ("BERLIN", "Berlin"),
        ("BRNO", "Brno"),
        ("BRUSSELS", "Brussels"),
        ("BUCHAREST", "Bucharest"),
        ("BUENOS_AIRES", "Buenos Aires"),
        ("CHIANG_MAI", "Chiang Mai"),
        ("DA_NANG", "Da Nang"),
        ("DAVOS", "Davos"),
        ("DUBAI", "Dubai"),
        ("HO_CHI_MINH_CITY", "Ho Chi Minh City"),
        ("HONG_KONG", "Hong Kong"),
        ("ISTANBUL", "Istanbul"),
        ("KUALA_LUMPUR", "Kuala Lumpur"),
        ("KYOTO", "Kyoto"),
        ("LA_PAZ", "La Paz"),
        ("LAGOS", "Lagos"),
        ("LISBON", "Lisbon"),
        ("LONDON", "London"),
        ("LOS_ANGELES", "Los Angeles"),
        ("LUGANO", "Lugano"),
        ("MADRID", "Madrid"),
        ("MALTA", "Malta"),
        ("MANILA", "Manila"),
        ("MEDELLIN", "Medellin"),
        ("MEXICO_CITY", "Mexico City"),
        ("MIAMI", "Miami"),
        ("MILAN", "Milan"),
        ("MONTREAL", "Montreal"),
        ("MUNICH", "Munich"),
        ("NAIROBI", "Nairobi"),
        ("NEW_YORK_CITY", "New York City"),
        ("OXFORD", "Oxford"),
        ("PARIS", "Paris"),
        ("PORTO", "Porto"),
        ("PRAGUE", "Prague"),
        ("RIO_DE_JANEIRO", "Rio de Janeiro"),
        ("ROATAN", "Roatan"),
        ("ROME", "Rome"),
        ("SALT_LAKE_CITY", "Salt Lake City"),
        ("SAN_FRANCISCO", "San Francisco"),
        ("SAN_JUAN", "San Juan"),
        ("SEOUL", "Seoul"),
        ("SINGAPORE", "Singapore"),
        ("SPLIT", "Split"),
        ("STANFORD", "Stanford"),
        ("STOCKHOLM", "Stockholm"),
        ("TAIPEI", "Taipei"),
        ("TEL_AVIV", "Tel Aviv"),
        ("TOKYO", "Tokyo"),
        ("TORONTO", "Toronto"),
        ("VIENNA", "Vienna"),
        ("WARSAW", "Warsaw"),
        ("ZUG", "Zug"),
        ("ZURICH", "Zurich"),
        ("OTHER", "Other")
    ]
    CHAIN_ECOSYSTEM = [
        ("BITCOIN", "Bitcoin"),
        ("ETHEREUM", "Ethereum"),
        ("SOLANA", "Solana"),
        ("BINANCE_SMART_CHAIN", "Binance Smart Chain"),
        ("CARDANO", "Cardano"),
        ("POLKADOT", "Polkadot"),
        ("AVALANCHE", "Avalanche"),
        ("TRON", "Tron"),
        ("COSMOS", "Cosmos"),
        ("NEAR", "Near"),
        ("TEZOS", "Tezos"),
        ("ALGORAND", "Algorand"),
        ("FLOW", "Flow"),
        ("HEDERA", "Hedera"),
        ("RIPPLE", "Ripple"),
        ("DOGECOIN", "Dogecoin"),
        ("CHIA", "Chia"),
        ("STELLAR", "Stellar"),
        ("EOS", "EOS"),
        ("NEO", "NEO"),
        ("VECHAIN", "VeChain"),
        ("IOTA", "IOTA"),
        ("LISK", "Lisk"),
        ("ARK", "Ark"),
        ("ZILLIQA", "Zilliqa"),
        ("QTUM", "Qtum"),
        ("WANCHAIN", "Wanchain"),
        ("MULTIVERSX", "MultiversX"),
        ("CELO", "Celo"),
        ("THORCHAIN", "THORChain"),
        ("KLAYTN", "Klaytn"),
        ("HARMONY", "Harmony"),
        ("SECRET_NETWORK", "Secret Network"),
        ("OASIS_NETWORK", "Oasis Network"),
        ("SKALE", "Skale"),
        ("TELOS", "Telos"),
        ("ENERGI", "Energi"),
        ("RSK", "RSK"),
        ("ERGO", "Ergo"),
        ("BERACHAIN", "Berachain"),
        ("PLUME_NETWORK", "Plume Network"),
        ("TON", "TON"),
        ("MONAD", "Monad"),
        ("MOVEMENT", "Movement"),
        ("SEI", "Sei"),
        ("CELESTIA", "Celestia"),
        ("POLYGON", "Polygon"),
        ("ARBITRUM", "Arbitrum"),
        ("OPTIMISM", "Optimism"),
        ("BASE", "Base"),
        ("MANTLE", "Mantle"),
        ("BLAST", "Blast"),
        ("STARKNET", "Starknet"),
        ("HYPERLEDGER", "Hyperledger"),
        ("MAPLE_FINANCE", "Maple Finance"),
        ("BABYLON", "Babylon"),
        ("DEEPBOOK", "DeepBook"),
    ]

    bio = models.TextField(null=True, blank=True)
    wallet_address = models.CharField(max_length=255, null=True, blank=True)

    chain_ecosystem = models.CharField(
        max_length=50, choices=CHAIN_ECOSYSTEM, null=True, blank=True
    )

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        "User", on_delete=models.CASCADE, null=True,blank=True,related_name="user_profile"
    )
    address = models.TextField(null=True, blank=False)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(
        max_length=10, choices=GENDER_TYPE, default=MALE, null=True
    )
    position = models.CharField(
        max_length=60, choices=USER_POSITION, default=MALE, null=True
    )
    project_name = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=150, choices=CITY_OPTIONS, null=True, blank=True)

    user_image = models.ImageField(upload_to="user_images", null=True, blank=True)
    telegram_account = models.CharField(max_length=150, null=True, blank=True) #this is telegram username
    linkedin_url = models.CharField(max_length=150, null=True, blank=True)
    twitter_account = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    company_name = models.CharField(max_length=150, null=True, blank=True)
    #this need to verfiy again (need to check if these relation is correct or not)

    def __str__(self):
        return f"{self.user.username}"
    
class UserField(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_fields")
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name="field_users")
    def __str__(self):
        return f"{self.user} - {self.field}"
    

class UserFeedback(BaseModel):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="feedbacks")
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to="feedback_images/", null=True, blank=True)
    rating = models.FloatField(default=0.0)


    def __str__(self):
        return f"Feedback from {self.user.username} - {self.description[:30]}..."
    

    



    
