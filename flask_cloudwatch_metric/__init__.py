import boto3
from typing import Dict, List
from flask import Flask, g


class Metric(object):
    """
    An internal model class for metrics.
    """

    def __init__(self, metric_name: str, value: float, unit: str, dimensions: List[Dict[str, str]]):
        self.metric_name = metric_name
        self.value = value
        self.unit = unit
        self.dimensions = dimensions


class CloudWatchMetricsReporter(object):
    """
    CloudWatch metrics reporter.

    This metrics reporter batch publishes metrics to CloudWatch at the end of every request.
    When user calls the addMetrics API, the metrics reporter will store the metric in an internal array,
    After the application logic is finished, the reporter wil publish the metrics in batches of 20 metrics to CloudWatch.
    This behavior is designed to reduce the amount of time to publish metrics for requests.
    The flask g context is used to store per-request metric data as recommended in:
    https://flask.palletsprojects.com/en/2.0.x/api/#flask.g

    Sample usage:

        app = Flask(__name__)
        metrics_reporter = CloudWatchMetricsReporter(app)

        @app.route('/')
        def main():
            response = # ... Your application logic
            metrics_reporter.add_metric(
                metric_name="RequestCount",
                value=1,
                unit="Count",
                dimensions=[]
            )
            return response, 200
    """
    def __init__(self,
                 app: Flask,
                 namespace: str,
                 aws_access_key_id: str = None,
                 aws_secret_access_key: str = None,
                 aws_region_name: str = None):
        if aws_access_key_id and aws_secret_access_key and aws_region_name:
            self.cloudwatch_client = boto3.client(
                'cloudwatch',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region_name
            )
        else:
            self.cloudwatch_client = boto3.client('cloudwatch')
        self.namespace = namespace
        self._attach_interceptor_to_app(app)

    @staticmethod
    def add_metric(metric_name: str, value: float, unit: str, dimensions: List[Dict[str, str]]):
        if 'cloudwatch_metrics_buffer' not in g:
            return

        g.cloudwatch_metrics_buffer.append(Metric(
            metric_name=metric_name,
            value=value,
            unit=unit,
            dimensions=dimensions
        ))

    def _attach_interceptor_to_app(self, app: Flask):
        def before_request():
            # create an empty array to store metric objects in global context
            g.cloudwatch_metrics_buffer = []

        def teardown_request(exception=None):
            if 'cloudwatch_metrics_buffer' not in g:
                return
            metrics_buffer = g.cloudwatch_metrics_buffer
            while len(metrics_buffer) > 0:
                # Get a batch of metrics with maximum size 20
                batch_metrics = self._get_batch_metrics(metrics_buffer)

                # Translate metric model and publish to CloudWatch
                metric_data = [self._translate_metric_model(metric) for metric in batch_metrics]
                self.cloudwatch_client.put_metric_data(
                    Namespace=self.namespace,
                    MetricData=metric_data
                )

        app.before_request(before_request)
        app.teardown_request(teardown_request)

    def _get_batch_metrics(self, metrics_buffer):
        batch_metrics = []
        if len(metrics_buffer) <= 20:
            while len(metrics_buffer) > 0:
                batch_metrics.append(metrics_buffer.pop())
        else:
            # Create a batch of metrics with size 20, due to the limitation of CloudWatch client:
            # https://flask.palletsprojects.com/en/2.0.x/api/#flask.Flask.after_request
            for i in range(20):
                batch_metrics.append(metrics_buffer.pop())
        return batch_metrics

    @staticmethod
    def _translate_metric_model(metric: Metric):
        return {
            'MetricName': metric.metric_name,
            'Dimensions': metric.dimensions,
            'Value': metric.value,
            'Unit': metric.unit
        }
