from setuptools import setup, find_packages

VERSION = '1.0.2'
DESCRIPTION = "Contiguity's official Python SDK"
LONG_DESCRIPTION = "Contiguity's official Python SDK makes using Contiguity easier than ever. See more information at https://github.com/use-contiguity/python"

setup(
    name="contiguity",
    version=VERSION,
    author="Contiguity",
    author_email="<support@contiguity.co>",
    url="https://github.com/use-contiguity/python",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["requests", "phonenumbers", "htmlmin"],
    keywords=['python', 'contiguity', 'sms', 'email', 'otp'],
)

# python3 setup.py sdist bdist_wheel
# twine upload dist/*