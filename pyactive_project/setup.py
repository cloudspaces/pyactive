from setuptools import setup


setup(
    name='PyActive',
    version='1.1',
    author='Pedro Garcia Lopez & Edgar Zamora Gomez & Ruben Mondejar Andreu',
    author_email='pedro.garcia@urv.cat, edgar.zamora@urv.cat',
    packages=['pyactive', 'pyactive.abstract_actor', 'pyactive.exception', 'pyactive.Multi', 'pyactive.pyactive_thread','pyactive.pyactive_thread.stomp', 'pyactive.supervisor', 'pyactive.tasklet'],
    url='http://ast-deim.urv.cat/pyactive',
    license='LICENSE.txt',
    description='Active Object Middleware',
    long_description=open('README.md').read(),
)
