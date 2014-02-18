import ssl
import M2Crypto
import requests
import urllib2

from plistlib import writePlistToString
from base64 import b64encode
from hashlib import sha1

def _get_remote_cert(url):
    r = requests.get(url)
    data = r.raw.read()

# TODO(dustin): urllib2 was in the original design, and it produces a result that's twice as long. We don't know why, or which version of correct.
# data = urllib2.urlopen(url).read()

    return _cer_der_to_pem(data)

def _verify_csr(csr_text):
    M2Crypto.X509.load_request_string(csr_text)

def _verify_private_key(private_key_text):
    M2Crypto.RSA.load_key_string(private_key_text)

def _verify_mdm_vendor_certificate(mdm_vendor_certificate_der):
    M2Crypto.X509.load_cert_der_string(mdm_vendor_certificate_der)

def _get_der_from_pem_csr(csr_text):
    r = M2Crypto.X509.load_request_string(csr_text)
    return r.as_der()

def _sign_csr(csr_der, private_key_text):
    private_key = M2Crypto.RSA.load_key_string(private_key_text)

# TODO(dustin): Is DER alirght? Is SHA1 what we're supposed to be using?
# TODO(dustin): Verify that this returns pure binary.
    signature = private_key.sign(sha1(csr_der).digest())
    return b64encode(signature)

def _cer_der_to_pem(cer_certificate_der):
# TODO(dustin): Verify that this works.
    return ssl.DER_cert_to_PEM_cert(cer_certificate_der)

def mdm_vendor_sign(csr_text, private_key_text, mdm_vendor_certificate_der):
    _verify_csr(csr_text)
    _verify_private_key(private_key_text)
    _verify_mdm_vendor_certificate(mdm_vendor_certificate_der)

    csr_der = _get_der_from_pem_csr(csr_text)
    csr_der_b64 = b64encode(csr_der)

    csr_signature = _sign_csr(csr_der, private_key_text)

    ia_pem = _get_remote_cert('https://developer.apple.com/certificationauthority/AppleWWDRCA.cer')
    root_pem = _get_remote_cert('http://www.apple.com/appleca/AppleIncRootCertificate.cer')
    mdm_vendor_certificate_pem = _cer_der_to_pem(mdm_vendor_certificate_der)

    plist_dict = dict(
        PushCertRequestCSR=csr_der_b64,
        PushCertCertificateChain=mdm_vendor_certificate_pem + ia_pem + root_pem,
        PushCertSignature=csr_signature
    )

    plist_xml = writePlistToString(plist_dict)
    return b64encode(plist_xml)

def mdm_vendor_sign_with_files(private_key_filepath, csr_filepath, mdm_vendor_certificate_filepath):
    with open(csr_filepath) as f:
        csr_text = f.read()

    with open(private_key_filepath) as f:
        private_key_text = f.read()

    with open(mdm_vendor_certificate_filepath) as f:
        mdm_vendor_certificate_der = f.read()

    return mdm_vendor_sign(csr_text, private_key_text, mdm_vendor_certificate_der)
