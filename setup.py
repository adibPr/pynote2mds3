from setuptools import setup

setup(name='pynote2mds3',
    version='0.1',
    description='Convert a python notebook into markdown with image being uploaded to S3',
    url='http://github.com/adibPr/pynote2mds3',
    author='Adib Pratama',
    author_email='pratama.adib@gmail.com',
    license='MIT',
    packages=['pynote2mds3'],
    install_requires=[
        'boto3',
        'nbformat',
        'appdirs'
    ],
    zip_safe=False,
    scripts=['bin/pynote2mds3']
)

