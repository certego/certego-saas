"""This command allow us to list all tasks from the queue (selected automatically)"""

from django.conf import settings
from django.core.management.base import BaseCommand



class QueueNotFoundException(Exception):
    """Exception raised in case the queue name is not found in the list of available queues"""


def _get_queue_message_number(queue_name: str) -> str:
    """Return the number of messages in the queue.

    :param queue_name: name of the queue to list the message number
    :type queue_name: str
    :raise QueueNotFoundException: raised in case the Queue is not present
    :return message_number: number of message in the queue
    :rtype message_number: str
    """
    client = boto3.client("sqs", settings.AWS_REGION)

    client_queue_url_list = client.list_queues().get("QueueUrls", [])
    # select queue url
    selected_queue_url = ""
    for client_url in client_queue_url_list:
        if queue_name in client_url:
            selected_queue_url = client_url
            break

    if not selected_queue_url:
        raise QueueNotFoundException(client_queue_url_list)

    if selected_queue_url:
        queue_data = client.get_queue_attributes(
            QueueUrl=selected_queue_url,
            AttributeNames=["ApproximateNumberOfMessages"],
        )
        return queue_data["Attributes"]["ApproximateNumberOfMessages"]


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
                message_in_the_queue = queue_data["Attributes"]["ApproximateNumberOfMessages"]
                self.stdout.write(
                    f"the number of the messages in the queue {queue} is {message_in_the_queue}"
                )
            else:
                self.stdout.write(self.style.ERROR(f"Skipping {queue}"))
