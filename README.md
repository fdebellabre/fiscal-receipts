Automatic generation and e-mailing of french fiscal receipts (cerfa 11580).

Génération et envoi automatique de reçus fiscaux par e-mail (cerfa 11580*3) à partir de données individuelles au format CSV, sous linux.


# Installation

Il n'y a pas d'installation à proprement parler, sinon des dépendances.

```bash
$ git clone https://github.com/fdebellabre/fiscal-receipts && cd fiscal-receipts
```

Création d'un environnement virtuel (facultatif), par exemple :

```bash
$ virtualenv venv
$ . venv/bin/activate
```

Installation des dépendances :

```bash
$ apt-get install pdfjam pdftk ps2pdf imagemagick
$ python3 -m pip install -r requirements.txt
```

`pdfjam` requiert une installation à jour de $\LaTeX$ comportant le paquet `pdfpages`.

# Utilisation

Génération de reçus fiscaux dans le dossier `output/pdf` :

```bash
$ python3 fiscal-receipts/__main.py__
```

Génération et envoi automatique d'e-mails :

```bash
$ python3 fiscal-receipts/__main.py__ --send
```

Le programme garde trace des e-mails envoyés. Si une erreur survient au cours de l'envoi, il suffit de relancer le programme pour poursuivre l'envoi des e-mails (le programme reprendra là où il s'était arrêté et n'enverra pas deux fois le même e-mail).


# Configuration

Remplacer les fichiers du dossier `input` :

- `contacts.csv` est le CSV contenant les données individuelles et doit comprendre les colonnes `nom`, `prenom`, `adresse`, `code`, `commune`, `montant`. Il peut aussi contenir les colonnes `email`, `date`, `forme`, `nature`, `mode`, `num_ordre`, pour spécifier l'adresse mail du donateur, la date du don, sa forme, sa nature, son mode de versement, le numéro d'ordre du reçu.
- `params.json` spécifie le montant minimum à partir duquel il faut générer un reçu fiscal, ainsi que les valeurs par défaut pour les colonnes `date`, `forme`, `nature`, `mode`, lorsqu'elles sont incomplètes ou absentes (pour ces trois dernières, `0` correspond à ne rien cocher, `1` à cocher la première modalité, `2` la deuxième, etc.).
- `organisation.json` spécifie les caractéristiques du bénéficiaire (nom, adresse, objet). Pour l'attribut `type`, rentrer le numéro de la case à cocher (par exempl `5` pour *Musée de France*).
- `email.json` spécifie les paramètres liés à l'envoi des e-mails (adresse, serveur SMTP, objet des mails).
- `email.txt` est le corps de l'e-mail. Il peut être personnalisé à l'aide des arguments `{prenom}`, `{nom}`, `{montant}` et `{date}`.
- `signature.*` est la signature du bénéficiaire des dons (au format `jpg`, `png`, `svg`, `pdf`, etc.).

En cas d'absence de numéro d'ordre du reçu, un numéro à 20 chiffres sera généré automatiquement. Ses 6 premiers chiffres correspondent à la date du don (format `yymmdd`) et les 14 chiffres suivants sont générés à partir des caractéristiques individuelles. Cela donne un numéro **ordonné** selon la date du don et **unique**, conformément à ce que demande la loi.

### Pour l'envoi des e-mails

En cas d'utilisation d'un compte Gmail, il faut commencer par [activer la connexion depuis des applications "moins sécurisées".][https://myaccount.google.com/lesssecureapps]

Les paramètres SMTP sont spécifiques au fournisseur de messagerie. En voici quelques exemples :

| Fournisseur de messagerie | Serveur SMTP        | Port |
| ------------------------- | ------------------- | ---- |
| Gmail                     | smtp.gmail.com      | 587  |
| Outlook                   | smtp.office365.com  | 587  |
| Yahoo                     | smtp.mail.yahoo.com | 587  |

