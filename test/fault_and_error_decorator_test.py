from flask_cloudwatch_metric import CloudWatchMetricsReporter
from flask_cloudwatch_metric.decorator import fault_failure_error
from flask import Flask

app = Flask(__name__)
metrics_reporter = CloudWatchMetricsReporter(app, 'FlaskApplication')


@app.route('/')
@fault_failure_error(metrics_reporter=metrics_reporter, resource_name='IndexPage')
def main():
    response = "Hello World!"
    return response, 400


if __name__ == '__main__':
    app.run()