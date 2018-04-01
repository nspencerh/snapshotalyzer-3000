from setuptools import setup

setup(
    name='snapshotalyzer-3000',
    version='0.1',
    author='Nicolas Spencer',
    author_email="nicolaspencer@gmail.com",
    description="snapshotalyzer 3000 is a tool that manages EC2 instances",
    license="GPLv3+",
    packages=['shotty'],
    url="https://github.com/nspencerh/snapshotalyzer-3000",
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        shotty=shotty.shotty:cli
    '''

)
