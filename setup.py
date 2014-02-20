from setuptools import setup, find_packages
import sys, os

version = '0.3.4'

setup(name='apns_csr',
      version=version,
      description="A tool to produce encoded Plist-CSRs for APNS.",
      long_description="""\
The process of packaging a client's CSR to be sent to Apple in order to 
authorize you to send notifications on its behalf is excruciating. This tool
does the hard work.   
""",
      classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Environment :: Handhelds/PDA\'s',
      'Environment :: Web Environment',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
      'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      keywords='apns, plist, csr',
      author='Dustin Oprea',
      author_email='myselfasunder@gmail.com',
      url='https://github.com/dsoprea/ApnsPlistCsr',
      license='GPL 2',
      packages=find_packages(exclude=[]),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'M2Crypto',
        'pyOpenSSL'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      scripts=['scripts/csr_to_apns_csr'],
      )

