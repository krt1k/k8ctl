from setuptools import setup, find_packages

setup(
    name='k8ctl',
    version='0.0.6',
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
    k8ctl=k8ctl.k8ctl:k8ctl
    '''
)
