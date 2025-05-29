from django.core.management.base import BaseCommand
from _user.task import process_daily_profits


class Command(BaseCommand):
    help = "Processes daily investment profits."

    def handle(self, *args, **options):
        process_daily_profits()
