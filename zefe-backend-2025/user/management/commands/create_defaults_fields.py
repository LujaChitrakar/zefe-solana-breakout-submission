from django.core.management.base import BaseCommand
from django.db import transaction
from user.models import Field

class Command(BaseCommand):
    help = 'Default Field for User'

    def handle(self, *args, **options):
        # values=["NFT.NYC","ETH DENVER","SOLCONF","ETHNJ","IBW"]
        values=[
             "Accelerator",
            "AI",
            "Blockchain",
            "Community",
            "DAO",
            "Data",
            "DeFi",
            "DEX",
            "EVM",
            "Event",
            "GameFi",
            "Investment",
            "Marketplace",
            "Metaverse",
            "Mining",
            "NFT",
            "Oracle",
            "RWA",
            "Security",
            "Social",
            "Stablecoin",
            "Storage",
            "Tokenization",
            "Trading",
            "Wallet"]

        try:
            with transaction.atomic():
                # create interview status
                for val in values:
                    Field.objects.get_or_create(name=val,code=val)

            self.stdout.write(
                '.......Default Field Created Successfully.......')

        except Exception as e:
            self.stderr.write(
                ".......Error Creating Field.......")
