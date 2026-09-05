from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from customers.models import Profile


class Command(BaseCommand):
    help = "Promote an existing user to the Admin / Super Admin role (or demote back to Distributor)."

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help="Username of the account to update.")
        parser.add_argument(
            '--role',
            type=str,
            choices=['admin', 'distributor'],
            default='admin',
            help="Role to assign (default: admin).",
        )

    def handle(self, *args, **options):
        username = options['username']
        role = options['role']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"No user found with username '{username}'.")

        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = role
        profile.save()

        self.stdout.write(self.style.SUCCESS(
            f"User '{username}' is now role='{role}'."
        ))
