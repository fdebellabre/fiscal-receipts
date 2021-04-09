import re
import pandas as pd
from num2words import num2words

def fill_fdf_template(fdf, org, ind):
    """
    Fills the FDF template

    :param fdf: (str) FDF template
    :param org: (dict) dictionary of organization attributes
    :param ind: (dict) dictionary of individual attributes
    :return: (str) filled FDF template
    """

    inddate = ind['date']
    orgdate = pd.to_datetime('today' if 'date' not in list(org) else org['date'])
    ind = dict(zip([z for z in ind if z!='date'], [str(ind[z]) for z in ind if z!='date']))
    org = dict(zip([z for z in org if z!='date'], [str(org[z]) for z in org if z!='date']))

    ind['day'] = str(inddate.day) if len(str(inddate.day))==2 else '0'+str(inddate.day)
    org['day'] = str(orgdate.day) if len(str(orgdate.day))==2 else '0'+str(orgdate.day)
    ind['month'] = str(inddate.month) if len(str(inddate.month))==2 else '0'+str(inddate.month)
    org['month'] = str(orgdate.month) if len(str(orgdate.month))==2 else '0'+str(orgdate.month)
    ind['year'] = str(inddate.year)
    org['year'] = str(orgdate.year)

    montant = float(ind['montant'])
    cents = 100*(montant%1)
    if cents>0:
        ind['montant_lettres'] = num2words(int(montant), lang='fr') + ' euros et ' + num2words(int(cents), lang='fr') + ' centimes'
    else:
        ind['montant_lettres'] = num2words(int(montant), lang='fr') + ' euros'

    # Numéro d'ordre
    fdf = fdf.replace('NUM_ORDRE', ind['num_ordre'])

    # Organisation
    fdf = fdf.replace('O_NOM', org['nom'])
    fdf = fdf.replace('O_NUM', org['num'])
    fdf = fdf.replace('O_RUE', org['rue'])
    fdf = fdf.replace('O_CODE', org['code'])
    fdf = fdf.replace('O_COMMUNE', org['commune'])
    fdf = fdf.replace('O_OBJ1', org['obj1'])
    fdf = fdf.replace('O_OBJ2', org['obj2'])
    fdf = fdf.replace('O_OBJ3', org['obj3'])

    # Type d'organisation
    types = list(range(1,20))
    types.sort(reverse=True)
    for x in types:
        if x==int(org['type']):
            fdf = fdf.replace('T_' + str(x), 'Oui')
        else:
            fdf = fdf.replace('T_' + str(x), 'Off')

    # Donateur
    fdf = fdf.replace('D_NOM', ind['nom'])
    fdf = fdf.replace('D_PRENOM', ind['prenom'])
    fdf = fdf.replace('D_ADRESSE', ind['adresse'])
    fdf = fdf.replace('D_CODE', ind['code'])
    fdf = fdf.replace('D_COMMUNE', ind['commune'])

    # Montant du don
    fdf = fdf.replace('MONTANT_CHIFFRE', ind['montant'])
    fdf = fdf.replace('MONTANT_LETTRES', ind['montant_lettres'])

    # Date du versement
    fdf = fdf.replace('DON_DAY', ind['day'])
    fdf = fdf.replace('DON_MONTH', ind['month'])
    fdf = fdf.replace('DON_YEAR', ind['year'])

    # Date de signature du reçu
    fdf = fdf.replace('SIGN_DAY', org['day'])
    fdf = fdf.replace('SIGN_MONTH', org['month'])
    fdf = fdf.replace('SIGN_YEAR', org['year'])

    # Article CGI
    fdf = fdf.replace('CGI_200', 'Oui' if '200' in org['cgi'] else 'Off')
    fdf = fdf.replace('CGI_238', 'Oui' if '238' in org['cgi'] else 'Off')
    fdf = fdf.replace('CGI_885', 'Oui' if '885' in org['cgi'] else 'Off')

    # Forme du don
    fdf = fdf.replace('F_AUTHENTIQUE', 'Oui' if (ind['forme']=='1' or bool(re.search('authentique', ind['forme']))) else 'Off')
    fdf = fdf.replace('F_SEING_PRIVE', 'Oui' if (ind['forme']=='2' or bool(re.search('seing|priv.', ind['forme']))) else 'Off')
    fdf = fdf.replace('F_MANUEL', 'Oui'      if (ind['forme']=='3' or bool(re.search('manuel', ind['forme']))) else 'Off')
    fdf = fdf.replace('F_OTHER', 'Oui'       if (ind['forme']=='4' or bool(re.search('autre|other', ind['forme']))) else 'Off')

    # Nature du don
    fdf = fdf.replace('N_NUMERAIRE', 'Oui' if (ind['nature']=='1' or bool(re.search('num.raire', ind['nature']))) else 'Off')
    fdf = fdf.replace('N_TITRES', 'Oui'    if (ind['nature']=='2' or bool(re.search('titre', ind['nature']))) else 'Off')
    fdf = fdf.replace('N_OTHER', 'Oui'     if (ind['nature']=='3' or bool(re.search('autre|other', ind['nature']))) else 'Off')

    # Mode de versement du don
    fdf = fdf.replace('M_ESPECES', 'Oui' if (ind['mode']=='1' or bool(re.search('esp.ce|cash|liquide', ind['mode']))) else 'Off')
    fdf = fdf.replace('M_CHEQUE', 'Oui'  if (ind['mode']=='2' or bool(re.search('ch.que', ind['mode']))) else 'Off')
    fdf = fdf.replace('M_OTHER', 'Oui'   if (ind['mode']=='3' or bool(re.search('virement|pr.l.v.|carte', ind['mode']))) else 'Off')

    return(fdf)
