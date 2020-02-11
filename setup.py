from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='timedpad',
      version=version,
      description="Expiriring Etherpads",
      long_description="""Tool to create Etherpads which expire after 30 days of inactivity
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='COM.lounge',
      author_email='info@comlounge.net',
      url='',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        "flask",
        "flask-pymongo",
        "jinja2",
        "etherpad_lite"
      ],
)
