##flask-cloudwatch-metric

A Flask extension to provide easy and efficient integration with CloudWatch to publish application metrics.

### Sample usage

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


### How it works?

flask-cloudwatch-metric is built on top of boto3 client and Flask framework,
to provide efficient per-request metrics publication to AWS CloudWatch.

When a `CloudWatchMetricsReporter` object is created with a Flask app,
the constructor will inject an interceptor(or called filter if you are familiar with JAXRS)
into the application. The interceptor runs for every request providing the following functionalities:

* before each request: initialize a in-memory buffer to store metrics for this request
* after each request: publish all the metrics in buffer to CloudWatch
* during the request: metrics are added to the buffer by calling the report API's(e.g. `add_metric`)

To support running Flask in multi-threading mode, we need to store the in-memory buffer
in a place that is separated for each request. To achieve this, we can use the application context
provided by Flask's `g` context(https://flask.palletsprojects.com/en/2.0.x/api/#flask.g).
Using the `g` context, each request can store its own metric objects without interfering with others.