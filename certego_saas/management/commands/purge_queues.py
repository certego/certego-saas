from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Purge selected queues"

    def handle(self, *args, **options):
        # we should import it here so that projects that don't use boto3 can still use this library
        # since we are not adding this in the requirements.txt file
        try:
            import boto3
        except ImportError:
            self.stdout.write(
                self.style.ERROR(
                    "boto3 is not installed. Please install boto3 to use this command."
                )
            )
            return
        client = boto3.client("sqs", settings.AWS_REGION)
        queues = client.list_queues().get("QueueUrls", [])
        for queue in queues:
            if input(f"Are you sure you want to purge {queue}? (y/n) ") == "y":
                client.purge_queue(QueueUrl=queue)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully purged queue {queue} with url {queue}"
                    )
                )
            else:
                self.stdout.write(self.style.ERROR(f"Skipping {queue}"))
