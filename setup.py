from setuptools import setup

try:
    with open("readme.md", 'r') as f:
        long_description = f.read()
except:
    long_description = ''

setup(
    name='flask-cloudwatch-metric',
    version='0.1.7',
    url='https://github.com/yxiao1996/flask-cloudwatch-metric',
    license='MIT',
    author='Yu Xiao',
    author_email='yxiao96@bu.edu',
    description='A Flask extension to provide easy integration with CloudWatch to publish metrics',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['flask_cloudwatch_metric', 'flask_cloudwatch_metric.decorator'],
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