import click
import getpass
import os
import pandas as pd
import numpy as np
import json
import subprocess
import sys

from process_signature import *
from fill_fdf_template import *
from helpers import *
from preprocess import *
from send_emails import *

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def main(mailsend):
    """
    Generates and e-mails fiscal receipts, based on data in the ../input folder

    :param mailsend: (bool) whether to send e-mails after generating the PDFs
    :return: None
    """
    # Load parameters
    with open('../input/params.json') as file:
        params = json.load(file)
    with open('../input/organisation.json') as file:
        org = json.load(file)
        org = split_obj_by_width(org)

    # Get parameters for the e-mail account
    if mailsend:
        with open('../input/email.json') as file:
            mailparams = json.load(file)
        print('Please enter your password for {email}'.format(email=mailparams['email']))
        mailparams['password'] = getpass.getpass()

    # Load and preprocess individual data
    df = try_read_csv('../input/' + params['CSV_PATH'], expected=['nom', 'prenom', 'adresse', 'code', 'commune', 'montant'])
    df = preprocess(df, params)
    os.makedirs('../output/pdf', exist_ok=True)
    df['path'] = '../output/pdf/' + df.nom + '_' + df.prenom + '_' + df.num_ordre + '.pdf'

    # Load FDF file
    with open('form.fdf', 'rt') as file:
        fdf = file.read()

    # Process the signature. If it has not changed, only generate the missing PDFs.
    sign_changed = process_signature()
    if sign_changed:
        def file_missing(s):
            return(os.path.exists(s)==False)
        df['missing'] = df.path.apply(file_missing)
    else:
        df['missing'] = True

    # PDF generation
    for i in range(df.shape[0]):
        ind = df.loc[i].to_dict()
        if ind['missing']:
            with open('tmp.fdf', 'wb') as outfile:
                filled_fdf = fill_fdf_template(fdf, org, ind)
                outfile.write(filled_fdf.encode('iso-8859-1'))
            subprocess.run('pdftk form.pdf fill_form tmp.fdf output tmp.pdf', shell=True, timeout=10)
            subprocess.run('pdftk tmp.pdf cat 1 output tmp1.pdf', shell=True, timeout=10)
            subprocess.run('pdftk tmp.pdf cat 2 output tmp2.pdf', shell=True, timeout=10)
            subprocess.run('pdftk tmp2.pdf stamp signature-pdfjam-pdfjam.pdf output tmp3.pdf', shell=True, timeout=10)
            subprocess.run('pdftk tmp1.pdf tmp3.pdf cat output tmp4.pdf', shell=True, timeout=10)
            subprocess.run('ps2pdf tmp4.pdf "{filename}"'.format(filename=ind['path']), shell=True, timeout=10)

    # Clean the working directory
    subprocess.run('rm -f tmp* signature*', shell=True, check=True, timeout=10)

    # Send the emails if specified
    if mailsend:
        send_emails(df, mailparams, org)

    df.drop('missing', axis=1, inplace=True)
    df.to_csv('../output/filled_' + params['CSV_PATH'])

@click.command()
@click.option('--send', '-s', is_flag=True, help='Send the e-mails.')
def launch(send):
    """
    Generate and send fiscal receipts (cerfa 11580*3).
    """
    main(send)

if __name__ == '__main__':
    launch()
