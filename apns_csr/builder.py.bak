import urllib2
import ssl
import M2Crypto
import OpenSSL

from plistlib import writePlistToString
from base64 import b64encode
from hashlib import sha1
from collections import OrderedDict

IA_CERT_URL = 'https://developer.apple.com/certificationauthority/AppleWWDRCA.cer'
CA_CERT_URL = 'http://www.apple.com/appleca/AppleIncRootCertificate.cer'

def _get_remote_cert(url):
# TODO(dustin): There's an encoding problem with requests.get(url).text, and partial data when we do requests.get(url).raw.read() .
# TODO(dustin): Cache/store this locally, or we'll be out of luck if their systems are unavailable.
    data = urllib2.urlopen(url).read()
    if not data:
        raise ValueError("Could not read remote certificate: %s" % (url))

    return _cer_der_to_pem(data).rstrip() + "\n"

def _verify_csr(csr_text):
    M2Crypto.X509.load_request_string(csr_text)

def _verify_and_read_mdm_vendor_certificate(mdm_vendor_p12_certificate_der, passphrase):
    mdm_vendor_certificate = OpenSSL.crypto.load_pkcs12(mdm_vendor_p12_certificate_der, passphrase)

    mdm_vendor_pk_internal = mdm_vendor_certificate.get_privatekey()
    mdm_vendor_certificate_internal = mdm_vendor_certificate.get_certificate()

    mdm_vendor_pk_pem = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, mdm_vendor_pk_internal)
    mdm_vendor_certificate_pem = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, mdm_vendor_certificate_internal)

    return { 'private_key_pem': mdm_vendor_pk_pem, 
             'certificate_pem': mdm_vendor_certificate_pem }

def _get_der_from_pem_csr(csr_text):
    r = M2Crypto.X509.load_request_string(csr_text)
    return r.as_der()

def _sign_csr(csr_der, mdm_vendor_private_key_text):
    mdm_vendor_private_key = M2Crypto.RSA.load_key_string(mdm_vendor_private_key_text)
    hashed = sha1(csr_der).digest()
    signature = mdm_vendor_private_key.sign(hashed)

    return b64encode(signature)

def _cer_der_to_pem(cer_certificate_der):
    return ssl.DER_cert_to_PEM_cert(cer_certificate_der)

def _chunks(l, n=64):
    for i in xrange(0, len(l), n):
        yield l[i:i+n] + "\n"

def mdm_vendor_sign(csr_text, 
                    mdm_vendor_certificate_der, 
                    mdm_vendor_certificate_passphrase, 
                    encode_xml=True):
    mdm_vendor_cert_info = \
        _verify_and_read_mdm_vendor_certificate(
            mdm_vendor_certificate_der, 
            mdm_vendor_certificate_passphrase)

    csr_der = _get_der_from_pem_csr(csr_text)

    csr_rows = csr_text.rstrip().split("\n")
    csr_rows_no_anchors = csr_rows[1:-1]
    csr_text_no_anchors = "\n".join(csr_rows_no_anchors)

    csr_signature = _sign_csr(csr_der, mdm_vendor_cert_info['private_key_pem'])

    ia_pem = _get_remote_cert(IA_CERT_URL)
    ca_pem = _get_remote_cert(CA_CERT_URL)

    _cert_chain = (mdm_vendor_cert_info['certificate_pem'] + ia_pem + ca_pem)
    _cert_sig = ''.join(_chunks(csr_signature))

    plist_dict = dict(
        PushCertRequestCSR=csr_text_no_anchors,
        PushCertCertificateChain=_cert_chain.rstrip(),
        PushCertSignature=_cert_sig.rstrip())

    plist_xml = writePlistToString(plist_dict)

    if encode_xml is False:
        return plist_xml

    encoded_plist = b64encode(plist_xml)
    return ''.join(_chunks(encoded_plist)).rstrip() + "\n"

def mdm_vendor_sign_with_files(csr_filepath, 
                               mdm_vendor_certificate_filepath, 
                               mdm_vendor_certificate_passphrase, 
                               *args, **kwargs):
    with open(csr_filepath) as f:
        csr_text = f.read()

    with open(mdm_vendor_certificate_filepath) as f:
        mdm_vendor_certificate_der = f.read()

    return mdm_vendor_sign(csr_text, 
                           mdm_vendor_certificate_der, 
                           mdm_vendor_certificate_passphrase, 
                           *args, **kwargs)
