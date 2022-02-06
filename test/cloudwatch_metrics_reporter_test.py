import unittest
import boto3
from flask_cloudwatch_metric import CloudWatchMetricsReporter
from flask import Flask
from unittest.mock import MagicMock, Mock
from utils import ServerThread, make_test_call


class CloudWatchMetricsReporterTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = Flask(__name__)
        cls.cloudwatch_client = boto3.client('cloudwatch', region_name='us-east-1')
        cls.metrics_reporter = CloudWatchMetricsReporter(cls.app, "CloudWatchMetricsReporterTest", cls.cloudwatch_client)

        def index():
            cls.metrics_reporter.add_metric(
                metric_name="RequestCount",
                value=1,
                unit="Count",
                dimensions=[]
            )
            return "Hello world", 200
        cls.app.add_url_rule("/", view_func=index)

        cls.server = ServerThread(cls.app)
        cls.server.start()
        print("Test flask server started")

    @classmethod
    def tearDownClass(cls):
        print("Shuting down flask server")
        cls.server.shutdown()

    def test_happy_case(self):
        self.cloudwatch_client.put_metric_data = MagicMock(return_value=None)
        make_test_call()
        self.cloudwatch_client.put_metric_data.assert_called_once()

    def test_cloudwatch_throws_exception(self):
        self.cloudwatch_client.put_metric_data = Mock(side_effect=Exception("Mock Failure from CloudWatch"))
        make_test_call()
        self.cloudwatch_client.put_metric_data.assert_called_once()


if __name__ == '__main__':
    unittest.main()
