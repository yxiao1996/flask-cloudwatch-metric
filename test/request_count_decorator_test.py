from flask_cloudwatch_metric import CloudWatchMetricsReporter
from flask_cloudwatch_metric.decorator import request_count
from flask import Flask

app = Flask(__name__)
metrics_reporter = CloudWatchMetricsReporter(app, 'FlaskApplication')


@app.route('/')
@request_count(metrics_reporter=metrics_reporter, resource_name='IndexPage')
def main():
    response = "Hello World!"
    metrics_reporter.add_metric(
        metric_name="RequestCount",
        value=1,
        unit="Count",
        dimensions=[]
    )
    return response, 200


if __name__ == '__main__':
    app.run()