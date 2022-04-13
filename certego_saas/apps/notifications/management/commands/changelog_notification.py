import argparse
import os
import re
from typing import List, Tuple

import markdown
from django.core.management.base import BaseCommand

from certego_saas.apps.notifications.models import Notification
from certego_saas.ext.models import AppChoices


class Command(BaseCommand):
    help = "Create a notification with the latest changes"
    version_regex = r"\[v[0-9].[0-9].[0-9]\]"

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.markdown: str
        self.last_release: str
        self.last_version: str
        self.last_content: str
        self.html: str

    def add_arguments(self, parser):
        parser.add_argument("path", type=str)
        parser.add_argument(
            "appname", type=str, choices=[elem[0] for elem in AppChoices.choices]
        )
        parser.add_argument("--release", nargs="?", type=str, default=None)
        parser.add_argument("--number-of-releases", nargs="?", type=int, default=3)
        parser.add_argument(
            "--debug", action=argparse.BooleanOptionalAction, default=False
        )

    def _read_file(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"File {path} not found")
        self.markdown = open(path, "r", encoding="utf-8").read()

    def _get_release(
        self, number_of_releases: int, release: str = None
    ) -> List[Tuple[str, str]]:
        versions = re.findall(self.version_regex, self.markdown)
        # remove [v ]
        versions = [v[2:-1] for v in versions]
        if release:
            try:
                index = versions.index(release)
            except ValueError:
                return []
            else:
                body = self._get_body(release, index)
                return [(release, body)]
        else:
            return [
                (versions[i], self._get_body(versions[i], i))
                for i in range(number_of_releases)
            ]

    def _get_body(self, tag: str, position: int) -> str:
        body = re.split(rf"##\s{self.version_regex}", self.markdown)[position + 1]
        return f"## [v{tag}]{body}"

    def _create_notification(
        self, version: str, body: str, app_name: str
    ) -> Tuple[Notification, bool]:
        title = f"New changes in {version}"
        try:
            return Notification.objects.get(title__contains=title), False
        except (Notification.DoesNotExist, Notification.MultipleObjectsReturned):
            return (
                Notification.objects.create(appname=app_name, title=title, body=body),
                True,
            )

    def handle(self, *args, **options):
        self._read_file(options["path"])
        tag_and_body = self._get_release(
            options["number_of_releases"], options["release"]
        )
        for tag, body in tag_and_body:
            self.stdout.write(self.style.SUCCESS(f"Version {tag}"))
            if options["debug"]:
                self.stdout.write(f"Content:\n{body}")
            html = markdown.markdown(f"{body}")
            if options["debug"]:
                self.stdout.write(f"Html:\n{html}")
            notification, result = self._create_notification(
                tag, html, options["appname"]
            )
            if result:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"New notification created with success" f" for version {tag}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"Notification already exists" f" for version {tag}"
                    )
                )
        else:
            if options["release"]:
                self.stdout.write(
                    self.style.ERROR(
                        f"Release {options['release']} not found in the changelog"
                    )
                )
