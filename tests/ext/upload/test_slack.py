from unittest import skip

from certego_saas.ext.upload import Slack

from ... import CustomTestCase


@skip
class TestUploadSlack(CustomTestCase):
    def test_send(self):
        slack = Slack()
        try:
            slack.send_message(title="Automated message because Github api sucks dicks")
        except Exception as e:
            self.fail(e)
