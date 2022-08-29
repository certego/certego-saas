from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Queue management"

    def add_arguments(self, parser):
        parser.add_argument(
            "job", type=str, help="What to do", choices=["list_messages", "purge"]
        )
        parser.add_argument("-p", "--prefix", type=str, help="Prefix of the queues")

    def _dynamic_import(self):
        try:
            pass
        except ImportError:
            self.stdout.write(
                self.style.ERROR(
                    "boto3 is not installed. Please install boto3 to use this command."
                )
            )
            return False
        else:
            return True

    def _purge(self, client, queue):
        client.purge_queue(QueueUrl=queue)
        self.stdout.write(
            self.style.SUCCESS(f"Successfully purged queue {queue} with url {queue}")
        )

    def _list_messages(self, client, queue):
        queue_data = client.get_queue_attributes(
            QueueUrl=queue,
            AttributeNames=["ApproximateNumberOfMessages"],
        )
        message_in_the_queue = queue_data["Attributes"]["ApproximateNumberOfMessages"]
        self.stdout.write(
            self.style.SUCCESS(
                f"The number of the messages in the queue {queue} is {message_in_the_queue}"
            )
        )

    def handle(self, *args, **options):
        # we should import it here so that projects that don't use boto3 can still use this library
        # since we are not adding this in the requirements.txt file
        if not self._dynamic_import():
            return
        client = boto3.client("sqs", settings.AWS_REGION)

        prefix = options.get("prefix")
        if prefix:
            queues = client.list_queues(QueueNamePrefix=prefix)
        else:
            queues = client.list_queues()
        queues = queues.get("QueueUrls", [])
        dispatcher = {"purge": self._purge, "list_messages": self._list_messages}
        job = options["job"]
        for queue in queues:
            if (
                input(f"Are you sure you want to do {job} on queue {queue}? (y/n) ")
                == "y"
            ):
                try:
                    dispatcher[job](client, queue)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error {e}"))
            else:
                self.stdout.write(self.style.ERROR(f"Skipping {queue}"))
