from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Increase the length of the username and email fields in the database
    
    Increases the length of these fields to be RFC3696/5321-compliant, allowing
    a maximum length of 254 characters.

    """
    help = ("Increase the length of the User model's username and email "
            "address fields in the database.")

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', 1))

        from django.db import connection, transaction
        cursor = connection.cursor()
        # TODO: This works for Postgres, but I'm not sure about other
        # databases
        cursor.execute("ALTER TABLE auth_user ALTER COLUMN username TYPE varchar(254)")
        cursor.execute("ALTER TABLE auth_user ALTER COLUMN email TYPE varchar(254)")
        transaction.commit_unless_managed()
        if verbosity >= 1:
          self.stdout.write("Field length increased successfully.\n")
