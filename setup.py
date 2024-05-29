from setuptools import setup, find_packages

setup(
    name='ezctl',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'click'
    ],
    email='kishorekarthik98@gmail.com',
    author='Kishorekarthik P',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    entry_points='''
    [console_scripts]
    ezctl=ezctl:ezctl
    ''',
)
