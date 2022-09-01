from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Queue management"

    def add_arguments(self, parser):
        parser.add_argument("-p", "--prefix", type=str, help="Prefix of the queues")

        subparsers = parser.add_subparsers(help="Queues commands", dest="mode")
        subparsers.add_parser("purge", help="Purge a queue")
        subparsers.add_parser("count_messages", help="Count messages of a queue")
        parser_a = subparsers.add_parser(
            "show_messages", help="Show messages ofa  queue"
        )
        parser_a.add_argument(
            "-c",
            "--count",
            type=int,
            help="How many messages to show",
        )

    def _dynamic_import(self):
        try:
            import boto3
        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(
                    "boto3 is not installed. Please install boto3 to use this command."
                )
            )
            raise e
        else:
            self.client = boto3.client("sqs", settings.AWS_REGION)

    def _purge(self, queue, **kwargs):
        self.client.purge_queue(QueueUrl=queue)
        self.stdout.write(
            self.style.SUCCESS(f"Successfully purged queue {queue} with url {queue}")
        )

    def _count_messages(self, queue, **kwargs):
        queue_data = self.client.get_queue_attributes(
            QueueUrl=queue,
            AttributeNames=["ApproximateNumberOfMessages"],
        )
        message_in_the_queue = int(queue_data["Attributes"]["ApproximateNumberOfMessages"])
        if not message_in_the_queue:
            style = self.style.ERROR
        else:
            style = self.style.SUCCESS
        self.stdout.write(
            style(
                f"The number of the messages in the queue {queue} is {message_in_the_queue}"
            )
        )

    def _show_messages(self, queue, count=100, **kwargs):
        messages = self.client.receive_message(
                QueueUrl=queue, MaxNumberOfMessages=count, VisibilityTimeout=10
            ).get("Messages", [])
        if not messages:
            self.stdout.write(
                self.style.ERROR(
                    f"No messages available for queue {queue}"
                )
            )
        for i, message in enumerate(
            messages
        ):
            self.stdout.write(
                self.style.SUCCESS(f"Message {i} has content {message['Body']}")
            )

    def handle(self, *args, **options):
        # we should import it here so that projects that don't use boto3 can still use this library
        # since we are not adding this in the requirements.txt file
        self._dynamic_import()

        prefix = options.pop("prefix")
        if prefix:
            queues = self.client.list_queues(QueueNamePrefix=prefix)
        else:
            queues = self.client.list_queues()
        queues = queues.get("QueueUrls", [])

        if not queues:
            self.stdout.write(self.style.ERROR("No Queues"))
        dispatcher = {
            "purge": self._purge,
            "count_messages": self._count_messages,
            "show_messages": self._show_messages,
        }
        mode = options.pop("mode")
        for queue in queues:
            if (
                input(f"Are you sure you want to do {mode} on queue {queue}? (y/n) ")
                == "y"
            ):
                try:
                    dispatcher[mode](queue, **options)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error {e}"))
            else:
                self.stdout.write(self.style.ERROR(f"Skipping {queue}"))
