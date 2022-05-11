from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as file:
    long_description = file.read()

setup(
  name='lightDB',
  packages=['lightDB'],
  version='2.0',
  python_requires='>=3.6',
  license='GPLv3',
  description='sqlite database reader/writer',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author='assassion',
  author_email='assassionblack666@gmail.com',
  keywords=['lightDB', 'database', 'light database'],
  install_requires=['jinja2', 'logging', 'toml'],
  classifiers=[
    'Development Status :: 1 - Testing',
    'Intended Audience :: small business',
    'Topic :: Business software :: Databases',
    'License :: GNU license :: GPLv3'
  ],
)
