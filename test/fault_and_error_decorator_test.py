from flask_cloudwatch_metric import CloudWatchMetricsReporter
from flask_cloudwatch_metric.decorator import fault_and_error
from flask import Flask

app = Flask(__name__)
metrics_reporter = CloudWatchMetricsReporter(app, 'FlaskApplication')


@app.route('/')
@fault_and_error(metrics_reporter=metrics_reporter, resource_name='IndexPage')
def main():
    response = "Hello World!"
    return response


if __name__ == '__main__':
    app.run()