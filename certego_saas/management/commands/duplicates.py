import datetime

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Delete duplicates management"

    def add_arguments(self, parser):
        parser.add_argument(
            "python_model_path",
            type=str,
            help="Path for the model to check in python syntax",
        )
        parser.add_argument(
            "unique_field", type=str, help="Field that should have been unique"
        )
        parser.add_argument(
            "order_by",
            type=str,
            help="Date field that will be used to determinate which object to keep",
        )
        parser.add_argument(
            "-db",
            "--db_type",
            type=str,
            help="Postgres o db mongo",
            choices=["pg", "mongo"],
            default="mongo",
        )
        parser.add_argument(
            "-f",
            "--from",
            type=str,
            help="From date format DD/MM/YYYY",
        )
        parser.add_argument(
            "-t",
            "--to",
            type=str,
            help="From date format DD/MM/YY",
        )

        parser.add_argument(
            "-e",
            "--execute",
            action="store_true",
            help="Do not actually delete the object",
            default=False,
        )

    def handle(self, *args, **options):
        # we should import it here so that projects that don't use boto3 can still use this library
        # since we are not adding this in the requirements.txt file
        pmp: str = options["python_model_path"]
        import importlib

        order_by_field = options["order_by"]
        module, klass = pmp.rsplit(".", maxsplit=1)
        module = importlib.import_module(module)
        model_class = getattr(module, klass)
        for key in model_class._meta:
            if key.startswith("index"):
                model_class._meta[key] = {}
        db_type = options["db_type"]
        if db_type == "pg":
            raise NotImplementedError("Postgres has not been implement now")
        else:
            field = options["unique_field"]
            if hasattr(model_class ,"atlas"):
                qs = getattr(model_class, "atlas")
            else:
                qs = getattr(model_class, "objects")
            _from = options.get("from", None)
            _from = datetime.datetime.strptime(_from, "%d%m%Y")
            if _from:
                qs = qs.filter(
                    **{f"{field}__gte":
                _from}
                )
            _to = options.get("to", None)
            _to = datetime.datetime.strptime(_to, "%d%m%Y")
            if _to:
                qs = qs.filter(
                    **{f"{field}__lte":
                           _to}
                )

            groups = qs.aggregate(
                [
                    {"$project": {field: 1, "_id": 1, order_by_field: 1}},
                    {
                        "$group": {
                            "_id": f"${field}",
                            "count": {"$sum": 1},
                        }
                    },
                    {"$match": {"_id": {"$ne": None}, "count": {"$gt": 1}}},
                ]
            )

            dry_run = not options["execute"]

            for group in groups:
                _id = group["_id"]
                to_delete = model_class.objects.filter(id__in=group["ids"]).order_by(
                    order_by_field
                )[1:]
                if dry_run:
                    to_delete = to_delete.values_list("pk")
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"You would have deleted {len(to_delete)} objects {to_delete} with field {field} having "
                            f"value {_id}"
                        )
                    )
                else:
                    count = to_delete.delete()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"You have deleted {count} objects {to_delete} with field {field} having value {_id}"
                        )
                    )
            self.stdout.write(self.style.SUCCESS("The end"))
