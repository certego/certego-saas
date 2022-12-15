from certego_saas.ext.upload import Slack

from ... import CustomTestCase


class TestUploadSlack(CustomTestCase):
    def test_send(self):
        slack = Slack()
        try:
            slack.send_message(title="Automated message", channel="TEST")
        except Exception as e:
            self.fail(e)
