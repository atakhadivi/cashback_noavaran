from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from cashback_app.models import ActivityLog


class Command(BaseCommand):
    help = 'Clean up ActivityLog entries older than 6 months'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--months',
            type=int,
            default=6,
            help='Number of months to keep (default: 6)',
        )

    def handle(self, *args, **options):
        months = options['months']
        dry_run = options['dry_run']
        
        # Calculate the cutoff date
        cutoff_date = timezone.now() - timedelta(days=months * 30)
        
        # Find logs older than the cutoff date
        old_logs = ActivityLog.objects.filter(created_at__lt=cutoff_date)
        count = old_logs.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would delete {count} activity logs older than {months} months '
                    f'(before {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")})'
                )
            )
            if count > 0:
                self.stdout.write('Sample logs that would be deleted:')
                for log in old_logs[:5]:  # Show first 5 as examples
                    self.stdout.write(f'  - {log.created_at}: {log.user.username} - {log.activity_type}')
                if count > 5:
                    self.stdout.write(f'  ... and {count - 5} more')
        else:
            if count > 0:
                deleted_count, _ = old_logs.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully deleted {deleted_count} activity logs older than {months} months'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'No activity logs older than {months} months found'
                    )
                )