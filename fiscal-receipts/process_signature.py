import subprocess
import os
import hashlib
import re

def process_signature():
    """
    Converts the signature to PDF and scales it.

    :return: (bool) whether the signature has changed since last time
    """
    signfile = os.listdir('../input')
    signfile = [z for z in signfile if bool(re.search('signature\..*', z.lower()))][0]
    subprocess.run("convert ../input/{sign} signature.pdf".format(sign=signfile), shell=True, timeout=10)
    subprocess.run("pdfjam -q --papersize '{30mm,10mm}' signature.pdf", shell=True, timeout=10)
    subprocess.run("pdfjam -q --paper 'a4paper' --scale 0.26 --offset '6.27cm -10.8cm' signature-pdfjam.pdf", shell=True, timeout=10)

    # Check whether the signature has changed
    open('../output/log_signhash.txt', 'a').close()
    with open('../output/log_signhash.txt', 'rt') as file:
        signhash = file.read().strip()
    with open('../input/{sign}'.format(sign=signfile), 'rb') as afile:
        buf = afile.read()
        hasher = hashlib.sha256()
        hasher.update(buf)
        newhash = hasher.hexdigest()
        sign_changed = signhash==newhash
    with open('../output/log_signhash.txt', 'wt') as file:
        file.write(newhash)
    return(sign_changed)
