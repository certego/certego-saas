"""This command allow us to list all tasks from the queue (selected automatically)"""

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "List available messages in the queue used by this instance"

    def handle(self, *args, **options):
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
            if input(f"Are you sure you want to select {queue}? (y/n) ") == "y":
                queue_data = client.get_queue_attributes(
                    QueueUrl=queue,
                    AttributeNames=["ApproximateNumberOfMessages"],
                )
                message_in_the_queue = queue_data["Attributes"][
                    "ApproximateNumberOfMessages"
                ]
                self.stdout.write(
                    f"the number of the messages in the queue {queue} is {message_in_the_queue}"
                )
            else:
                self.stdout.write(self.style.ERROR(f"Skipping {queue}"))
