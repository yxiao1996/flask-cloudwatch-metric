from setuptools import setup

long_description = """flask-cloudwatch-metric
A Flask extension to provide easy integration with CloudWatch to publish metrics.

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

setup(
    name='flask-cloudwatch-metric',
    version='0.0.1',
    url='https://github.com/yxiao1996/flask-cloudwatch-metric',
    license='MIT',
    author='Yu Xiao',
    author_email='yxiao96@bu.edu',
    description='A Flask extension to provide easy integration with CloudWatch to publish metrics',
    long_description='A Flask extension to provide easy integration with CloudWatch to publish metrics',
    packages=['flask_cloudwatch_metric'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'boto3'
    ],
    keywords=['flask', 'cloudwatch', 'metrics', 'monitoring'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Monitoring',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8'
    ]
)