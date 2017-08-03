from setuptools import setup

setup(name='funniest',
      version='0.1',
      description='A basic version of blockchain_python',
      url='http://github.com/adiasg/blockchain_python',
      author='Aditya & Pranav',
      author_email='none@none.none',
      license='MIT',
      packages=['blockchain_python'],
      install_requires=[
          'flask', 'psycopg2', 'netifaces' 
      ],
      zip_safe=False)
