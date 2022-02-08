import boto3
from typing import Dict, List
from flask import Flask, g
import logging
import traceback


def initialize_metrics(
        app: Flask,
        namespace: str,
        aws_region_name: str,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None):
    # Create metrics reporter in Flask global context
    g.cloudwatch_metrics_reporter = CloudWatchMetricsReporter.new_reporter(
        app,
        namespace,
        aws_region_name,
        aws_access_key_id,
        aws_secret_access_key)


def get_metrics():
    if 'cloudwatch_metrics_reporter' not in g:
        raise Exception("Can't find CloudWatch metrics reporter in application context. " +
                        "Make sure you run 'initialize_metrics' function before trying to use the metrics")
    return g.cloudwatch_metrics_reporter


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
    """
    def __init__(self,
                 app: Flask,
                 namespace: str,
                 cloudwatch_client):
        self.cloudwatch_client = cloudwatch_client
        self.namespace = namespace
        self._attach_interceptor_to_app(app)

    @staticmethod
    def new_reporter(
            app: Flask,
            namespace: str,
            aws_region_name: str,
            aws_access_key_id: str = None,
            aws_secret_access_key: str = None):
        if aws_access_key_id and aws_secret_access_key:
            cloudwatch_client = boto3.client(
                'cloudwatch',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region_name
            )
        else:
            cloudwatch_client = boto3.client('cloudwatch', region_name=aws_region_name)

        return CloudWatchMetricsReporter(app, namespace, cloudwatch_client)

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
                logging.warning("Skip publishing CloudWatch metrics, no metrics buffer found in global context")
                return
            metrics_buffer = g.cloudwatch_metrics_buffer
            while len(metrics_buffer) > 0:
                # Get a batch of metrics with maximum size 20
                batch_metrics = self._get_batch_metrics(metrics_buffer)

                # Translate metric model and publish to CloudWatch
                metric_data = [self._translate_metric_model(metric) for metric in batch_metrics]
                try:
                    self.cloudwatch_client.put_metric_data(
                        Namespace=self.namespace,
                        MetricData=metric_data
                    )
                except Exception as e:
                    logging.error("Fail to publish metrics to CloudWatch. " + traceback.format_exc())

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
