from setuptools import setup

setup(
    name='JAWS',
    version='1.0',
    packages=['jaws', 'jaws.tasks'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask', 'celery', 'requests', 'tinydb']
)
