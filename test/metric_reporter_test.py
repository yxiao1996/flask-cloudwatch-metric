from flask_cloudwatch_metric import CloudWatchMetricsReporter
from flask import Flask

app = Flask(__name__)
metricsReporter = CloudWatchMetricsReporter(app, 'FlaskApplication')


@app.route('/')
def main():
    response = "Hello World!"
    metricsReporter.add_metric(
        metric_name="RequestCount",
        value=1,
        unit="Count",
        dimensions=[]
    )
    return response, 200


if __name__ == '__main__':
    app.run()