""" flume editor distutils distribution and installation script. """


import sys

requiredVersion = (3, 0)
requiredVersionStr = ".".join([str(i) for i in requiredVersion])

versionError = "ERROR: flume editor requires Python %s or higher" % requiredVersionStr

try:
    sys.version_info
except:
    print(versionError)
    raise SystemExit(1)

if sys.version_info < requiredVersion:
    print(versionError)
    raise SystemExit(1)

from distutils.core import setup

classifiers = """\
Development Status :: 3 - Alpha
Intended Audience :: Developers
License ::
Operating System :: OS Independent
Programming Language :: Python
Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)
"""

setup(name="flume",
      version="0.1.0",
      description="Apache Flume configurations editor",
      long_description="See home page.",
      author="Alexander Dobrodey",
      author_email="Alexander.Dobrodey@gmail.com",
      url="http://",
      download_url="http://",
      packages=['flume'],
      license="",
      platforms=["Any"],
      keywords="Apache Flume editor configuration",
      classifiers=filter(None, classifiers.split("\n")), requires=['PyQt5']
)