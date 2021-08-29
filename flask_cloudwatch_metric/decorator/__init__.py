import functools
from flask_cloudwatch_metric import CloudWatchMetricsReporter


class _RequestCountDecorator:
    """
    A request count decorator reports API-level request count to CloudWatch
    """
    def __init__(self, function, metrics_reporter: CloudWatchMetricsReporter, resource_name: str):
        functools.update_wrapper(self, function)
        self.function = function
        self.metrics_reporter = metrics_reporter
        self.resource_name = resource_name

    def __call__(self, *args, **kwargs):
        self.metrics_reporter.add_metric(
            metric_name='RequestCount',
            dimensions=[{
                "Name": "ResourceName",
                "Value": self.resource_name
            }],
            unit='Count',
            value=1
        )
        return self.function(*args, **kwargs)


def request_count(metrics_reporter: CloudWatchMetricsReporter, resource_name: str):
    def _request_count(function):
        return _RequestCountDecorator(
            function=function,
            metrics_reporter=metrics_reporter,
            resource_name=resource_name
        )
    return _request_count
