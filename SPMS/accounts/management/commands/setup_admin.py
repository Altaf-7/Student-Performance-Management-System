from django.core.management.base import BaseCommand
from accounts.models import User, Admin


class Command(BaseCommand):
    help = 'Create or reset the admin/superuser account without wiping the database'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, default='admin@spms.com', help='Admin email address')
        parser.add_argument('--password', type=str, default='Admin@12345', help='Admin password')
        parser.add_argument('--first-name', type=str, default='System', help='Admin first name')
        parser.add_argument('--last-name', type=str, default='Administrator', help='Admin last name')

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'role': User.RoleChoices.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )

        user.set_password(password)
        user.role = User.RoleChoices.ADMIN
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        if first_name and not user.first_name:
            user.first_name = first_name
        if last_name and not user.last_name:
            user.last_name = last_name
        user.save()

        # Ensure Admin profile exists
        Admin.objects.get_or_create(
            user=user,
            defaults={'designation': 'System Administrator'}
        )

        action = "Created new" if created else "Updated existing"
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully {action} admin account:\n"
                f"  Email:    {email}\n"
                f"  Password: {password}\n"
                f"  Role:     ADMIN (Superuser)\n"
            )
        )
