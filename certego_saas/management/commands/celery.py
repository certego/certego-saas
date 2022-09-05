"""This module contains functions and classes to inspect celery workers"""
import datetime

from django.core.management import BaseCommand
from django.utils import timezone


# DATA EXAMPLE
# {'celery@worker_analyze': [],
#  'celery@worker_customers': [],
#  'celery@worker_errors': [],
#  'celery@worker_indicators': [],
#  'celery@worker_internal': [],
#  'celery@worker_primary': [{'acknowledged': False,
#                             'args': [10],
#                             'delivery_info': {'exchange': '',
#                                               'priority': 0,
#                                               'redelivered': False,
#                                               'routing_key': 'primary.fifo'},
#                             'hostname': 'celery@worker_primary',
#                             'id': '21a72341-2c94-4fb2-9b88-583875f02e5e',
#                             'kwargs': {},
#                             'name': 'quokka.tasks.test',
#                             'time_start': 1662043140.0618265,
#                             'type': 'quokka.tasks.test',
#                             'worker_pid': 15},
#                            {'acknowledged': False,
#                             'args': [100],
#                             'delivery_info': {'exchange': '',
#                                               'priority': 0,
#                                               'redelivered': False,
#                                               'routing_key': 'primary.fifo'},
#                             'hostname': 'celery@worker_primary',
#                             'id': 'a53499a4-2a60-4482-a430-25619f036d2d',
#                             'kwargs': {},
#                             'name': 'quokka.tasks.test',
#                             'time_start': 1662043140.0834947,
#                             'type': 'quokka.tasks.test',
#                             'worker_pid': 17}]
# }

# task's fields explanation: https://docs.celeryq.dev/en/latest/reference/celery.app.control.html#celery.app.control.Inspect.query_task


class Command(BaseCommand):
    help = "Monitor celery worker status"

    def add_arguments(self, parser):
        parser.add_argument(
            "app", type=str, help="App celery control python path"
        )

    def handle(self, *args, **options):
        import importlib
        app_python_path=options["app"]
        module, obj = app_python_path.rsplit(".", maxsplit=1)
        module = importlib.import_module(module)
        app = getattr(module, obj)

        inspect = app.control.inspect()
        active_worker_list = inspect.active()
        available_worker_name_list = active_worker_list.keys()
        self.stdout.write(
            self.style.WARNING(
                f"AVAILABLE WORKERS at {timezone.now()} ({len(available_worker_name_list)}): {', '.join(available_worker_name_list)}"
            )
        )
        self.stdout.write("WORKER STATUS:")
        self.stdout.write("---------")
        for worker_name, active_task_list in active_worker_list.items():
            self.stdout.write(self.style.WARNING(worker_name.upper()))
            self.stdout.write(f"running tasks: {len(active_task_list)}")
            for active_task in active_task_list:
                task_type = active_task["type"]
                task_args = active_task["args"]
                task_delivery_info = active_task["delivery_info"]
                task_priority = task_delivery_info["priority"]
                task_start_timestamp = active_task["time_start"]
                task_start_datetime = datetime.datetime.fromtimestamp(
                    task_start_timestamp
                )
                self.stdout.write(
                    f"type: {task_type}, args: {task_args}, priority: {task_priority} started time: {task_start_datetime}"
                )
            self.stdout.write("---------")
