import sys

from setuptools import setup, find_namespace_packages

#repo_url = "http://..."

# check if current python version matches expected one
if sys.version_info[0] < 3:
    # throw an error if expected version is not matched
    sys.exit("Sorry, this package needs Python 3!")

setup(
    name = "environment-controller",
    version = "0.1.0",
    python_requires=">3.10.0",
#    url=repo_url,
    packages = find_namespace_packages(include=["controller.*"]),
    namespace_packages=["controller"],
    install_requires = [
        "paho-mqtt==2.1.0",
        "RPi.GPIO==0.7.1",
        "smbus2==0.5.0",
        "smbus==1.1.post2",
    ],
)
