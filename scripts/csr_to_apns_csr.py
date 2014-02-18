#!/usr/bin/env python2.7

import sys
sys.path.insert(0, '.')

import argparse

from apns_csr import mdm_vendor_sign_with_files

parser = argparse.ArgumentParser(description="Produce an APNS Plist (encoded) from a standard CSR.")
parser.add_argument('key', help='Private key (PEM)')
parser.add_argument('csr', help='Certificate signing request (PEM)')
parser.add_argument('mdm', help='MDM vendor certificate (DER)')

args = parser.parse_args()

encoded_plist = mdm_vendor_sign_with_files(args.key, args.csr, args.mdm)

print(encoded_plist)
