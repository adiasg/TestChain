from setuptools import setup

setup(name='blockchain_python',
      version='0.2',
      description='A basic version of blockchain_python',
      url='http://github.com/adiasg/blockchain_python',
      author='Aditya & Pranav',
      author_email='none@none.none',
      license='MIT',
      packages=['blockchain_core', 'blockchain_gui'],
      install_requires=[
          'flask', 'psycopg2', 'netifaces'
      ],
      zip_safe=False)
