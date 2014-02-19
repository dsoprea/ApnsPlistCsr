#!/usr/bin/env python2.7

import sys
sys.path.insert(0, '.')

import argparse

from apns_csr import mdm_vendor_sign_with_files

parser = argparse.ArgumentParser(
            description="Produce an APNS Plist (encoded) from a standard CSR.")

parser.add_argument('key', 
                    help='Private key (PEM)')

parser.add_argument('csr', 
                    help='Certificate signing request (PEM)')

parser.add_argument('mdm', 
                    help='MDM vendor certificate (DER)')

parser.add_argument('mdm_passphrase', 
                    help='Passphrase for MDM vendor certificate')

parser.add_argument('-x', '--xml', 
                    help='Show raw XML', action='store_true')

args = parser.parse_args()

encoded_plist = mdm_vendor_sign_with_files(
                    args.key, 
                    args.csr, 
                    args.mdm, 
                    args.mdm_passphrase, 
                    encode_xml=not args.xml)

sys.stdout.write(encoded_plist)
