import pandas as pd
import unicodedata
import matplotlib as mpl
from pathlib import Path
from matplotlib.afm import AFM

afm_path = Path(mpl.get_data_path(), 'fonts', 'afm', 'ptmr8a.afm')
with afm_path.open('rb') as fh:
    afm = AFM(fh)

def strwidth(s, afm=afm):
    noaccents = ''.join(c for c in unicodedata.normalize('NFD', str(s)) if unicodedata.category(c) != 'Mn').upper()
    return(afm.string_width_height(noaccents)[0])

def split_obj_by_width(org, maxwidth=65000, afm=afm):
    """
    Splits the "objet" input of organization characteristics when it is too
    long to fit in one row

    :param org: (dict) dictionary of organization characteristics
    :param maxwidth: (int) maximum width for a single row
    :param afm:
    :return: (dict)
    """
    fullstr = org['objet']
    if strwidth(fullstr, afm) <= maxwidth:
        org['obj1'] = fullstr
        org['obj2'] = ''
        org['obj3'] = ''
    else:
        lstr = fullstr.split()
        tmpstr = ' '.join(lstr[:-1])
        x = 0
        while strwidth(tmpstr, afm) > maxwidth:
            x += 1
            tmpstr = ' '.join(lstr[:-x])
        org['obj1'] = tmpstr
        lstr = lstr[len(lstr)-x:]
        tmpstr = ' '.join(lstr)
        if strwidth(tmpstr, afm) <= maxwidth:
            org['obj2'] = tmpstr
            org['obj3'] = ''
        else:
            tmpstr = ' '.join(lstr[:-1])
            x = 0
            while strwidth(tmpstr, afm) > maxwidth:
                x += 1
                tmpstr = ' '.join(lstr[:-x])
            lstr = lstr[len(lstr)-x:]
            org['obj2'] = tmpstr
            org['obj3'] = ' '.join(lstr)
    return(org)

def try_read_csv(path, expected, sep=[',',';','\t']):
    """
    Tries to open a CSV with different separators until the expected columns appear.

    :param path: (str) path of the CSV file
    :param expected: (list) list of expected columns
    :param sep: (list) list of separators to try
    :return: (pd.DataFrame)
    """
    for separator in list(sep):
        try:
            df = pd.read_csv(path, sep=separator)
            df.columns = [z.lower() for z in df.columns]
            if min([z in df.columns for z in expected])==1:
                return(df)
        except:
            pass
    raise ValueError('Cannot load file {csv}\nPlease make sure to use either "{sep}" as a delimiter.'.format(csv=path, sep='" or "'.join(list(sep))))
