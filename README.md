# Introduction

In order to push notifications to Apple devices belonging to client accounts,
you require a way to have your clients produce a CSR (certificate request),
attach your vendor information to it, and submit it to Apple. Unfortunately, 
the process of identifying the steps for this is tedious and undocumented.

This tool manages that for you, and is the result of combining multiple efforts of reverse-engineering of what little is available.

# OS Dependencies

- SWIG
- Python development headers/libraries

To install  under Ubuntu, run:

```
$ sudo apt-get install swig python-dev
```

# Python Dependencies

- M2Crypto
- pyOpenSSL

Run the following from the project root to install these dependencies:

```
$ sudo pip install -r requirements.txt
```

# Formal Process

The following are the typical steps required to produce a CSR that Apple will 
accept (steps that this tool manages). Note that **the "CSR" that they expect 
is *not* a standard cryptography CSR**. It is expected that you already have a 
2048-bit RSA private-key and a real (traditional) certificate request (CSR).

1. Extract a PEM-formatted private-key and certificate from the P12 vendor 
   certificate.

2. Produce a DER-formatted client CSR from the PEM-formatted client CSR.

3. Retrieve the remote DER-formatted CA certificates from the following URLs, 
   and convert them to PEM-formatted certificates:
   - [Intermediate WWDR ("World Wide Developer Relations") CA certificate](https://developer.apple.com/certificationauthority/AppleWWDRCA.cer)
   - [Root Apple CA certificate](http://www.apple.com/appleca/AppleIncRootCertificate.cer)
4. Convert the PEM-formatted client CSR to a DER-formatted CSR, and base64-
   encode it to 64-byte rows.

5. Sign a SHA1 hash of the DER-formatted client CSR with the vendor PEM-
   formatted private key to produce a binary digest/signature. Base64-encode
   this to 64-byte rows.

6. Compile a CA chain by concatenating the following PEM-certificates (with the 
   anchors at the top and bottom of each), in this order:
   1. Vendor certificate (the actual, signed PEM certificate *in* the P12).
   2. IA/WWDR certificate.
   3. Root/Apple certificate.
7. Build a Plist file with the generated certificates, where they have the 
   given names (on the left):

   | Name                         | Description       | Described in step |
   | ---------------------------- | ----------------- |:-----------------:|
   | **PushCertRequestCSR**       | Client CSR        | 4                 |
   | **PushCertSignature**        | Encoded signature | 5                 |
   | **PushCertCertificateChain** | Certificate chain | 6                 |

8. Base64-encode the final Plist XML to 64-byte rows.

The final, encoded Plist may now be submitted to Apple's [Push Certificate Portal](http://identity.apple.com).

If there's an error with your certificate, Apple will not accept your upload.

# Usage

To use the tool, you must have the following:

- Apple vendor MDM certificate (DER-formatted "p12" file), and passphrase.
- Client CSR (PEM-formatted "csr" file)

Command-line:

```
usage: csr_to_apns_csr [-h] [-x] csr vendor_p12 vendor_p12_pass

Produce an APNS Plist (encoded) from a standard CSR.

positional arguments:
  csr              Client CSR (PEM)
  vendor_p12       MDM vendor P12 certificate (DER)
  vendor_p12_pass  Passphrase for MDM vendor P12 certificate

optional arguments:
  -h, --help       show this help message and exit
  -x, --xml        Show raw XML
```

Example:

```
$ csr_to_apns_csr client.key client.csr mdm_vendor.cer "mdm_vendor_passphrase" > /tmp/client_encoded_plist_csr
```

Note that, in the example above, the MDM vendor P12 certificate that we were
given, as a vendor, from Apple, has a "cer" extension (rather than "p12").

# Use as a Library

```python
from apns_csr import mdm_vendor_sign_with_files,\
                     mdm_vendor_sign

encoded_plist_csr = mdm_vendor_sign_with_files(
    csr_filepath, 
    mdm_vendor_certificate_filepath, 
    mdm_vendor_certificate_passphrase, 
    *args, **kwargs):

# or, directly:

encoded_plist_csr = mdm_vendor_sign(
    csr_text, 
    mdm_vendor_certificate_der, 
    mdm_vendor_certificate_passphrase)

```

# Comments

Special thanks to [mdmvendorsign](https://github.com/grinich/mdmvendorsign).
Though I can't be sure of its validity, it provided something to start 
from.

