from setuptools import setup, find_packages

setup(
    name='nebuia_copilot_python',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'python-magic',
        'loguru',
        'requests_toolbelt'
    ],
    author='xellDart',
    author_email='miguel@nebuia.com',
    description='NebuIA Copilot python integration',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/dist-bit/copilot_integrations',
    classifiers=[
    ],
    python_requires='>=3.8',
)