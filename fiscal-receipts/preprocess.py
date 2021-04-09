import pandas as pd
import numpy as np
import hashlib

def preprocess(df, params):
    """
    Preprocesses the individual data, mainly to fill (or add) incomplete columns

    :param df: (pd.DataFrame) individual data
    :param params: (dict) dictionary of default values
    :return: (pd.DataFrame) preprocessed data
    """
    if 'date' not in df.columns:
        df['date'] = pd.to_datetime(params['DEFAULT_DATE'])
    else:
        df['temp'] = pd.to_datetime(params['DEFAULT_DATE'])
        df['date'] = np.where(df.date.isna(), df.temp, pd.to_datetime(df.date))

    if 'email' not in df.columns: df['email'] = ''

    if 'forme' not in df.columns:
        df['forme'] = params['DEFAULT_FORME']
    else:
        df['forme'] = np.where(df.forme.isna(), str(params['DEFAULT_FORME']), df.forme)

    if 'nature' not in df.columns:
        df['nature'] = params['DEFAULT_NATURE']
    else:
        df['nature'] = np.where(df.nature.isna(), str(params['DEFAULT_NATURE']), df.nature)

    if 'mode' not in df.columns:
        df['mode'] = params['DEFAULT_MODE']
    else:
        df['mode'] = np.where(df.mode.isna(), str(params['DEFAULT_MODE']), df.mode)

    def hash14(s):
        # Returns a hash with 14 characters
        h = hashlib.md5(s.encode('utf-8'))
        return(int(h.hexdigest(),16) % (10**14))

    # Generate a 20-character identifier for each donation
    df['tmp'] = df.astype(str).values.sum(axis=1)
    df['tmp'] = df.date.dt.strftime('%y%m%d') + df['tmp'].apply(hash14).astype(str)
    if 'num_ordre' not in df.columns:
        df['num_ordre'] = df['tmp']
    else:
        df['num_ordre'] = np.where(df.num_ordre.isna(), df['tmp'], df.num_ordre.astype(str))

    df = df[['nom', 'prenom', 'email', 'adresse', 'code', 'commune', 'montant', 'date', 'forme', 'nature', 'mode', 'num_ordre']]

    df = df.loc[df.montant.isna()==False]
    if df.dtypes.montant==object:
        df.montant = df.montant.str.extract('(\d+.\d*)')
        df.montant = df.montant.str.replace(',','.').astype(float)

    df = df.loc[df.montant>=params['DON_MIN']]

    df.code = df.code.astype(int).astype(str)
    for col in df.columns[df.dtypes==object]:
        df[col] = df[col].str.strip()
        if params['ALL_UPPERCASE']: df[col] = df[col].str.upper()

    df.reset_index(drop=True, inplace=True)
    return(df)
