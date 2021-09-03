import functools
from flask_cloudwatch_metric import CloudWatchMetricsReporter
from typing import Dict


class _MetricsDecoratorBase(object):
    NAME = "Name"
    VALUE = "Value"
    COUNT = 'Count'
    DEFAULT_STATUS_CODE = 200  # Default status code is 200 in Flask

    def _get_metric_dimension(self, name, value) -> Dict[str, str]:
        return {
            self.NAME: name,
            self.VALUE: value
        }

    """
    A static method to parse status code from view function return value(s).
    The possible return value could be found in: https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.make_response
    Here we assume that the response is a tuple (body, status, ...), where status is a number.
    If no status code is found, then default to 200.
    """
    def _get_status_code_from_response(self, response) -> int:
        if type(response) is tuple and len(response) > 1:
            if type(response[1]) is int:
                return response[1]
        return self.DEFAULT_STATUS_CODE


class _RequestCountDecorator(_MetricsDecoratorBase):
    """
    A request count decorator reports API-level request count to CloudWatch
    """
    def __init__(self, function, metrics_reporter: CloudWatchMetricsReporter, resource_name: str):
        # Update wrapper to keep the metadata of the wrapped function
        # more details see: https://docs.python.org/3/library/functools.html
        functools.update_wrapper(self, function)
        self.function = function
        self.metrics_reporter = metrics_reporter
        self.resource_name = resource_name

    def __call__(self, *args, **kwargs):
        response = self.function(*args, **kwargs)
        status_code = self._get_status_code_from_response(response)
        self.metrics_reporter.add_metric(
            metric_name='RequestCount',
            dimensions=[
                self._get_metric_dimension("ResourceName", self.resource_name),
                self._get_metric_dimension(
                    "StatusCode",
                    str(status_code)
                )
            ],
            unit=self.COUNT,
            value=1
        )
        print(status_code)
        return response


def request_count(metrics_reporter: CloudWatchMetricsReporter, resource_name: str):
    def _request_count(function):
        return _RequestCountDecorator(
            function=function,
            metrics_reporter=metrics_reporter,
            resource_name=resource_name
        )
    return _request_count
