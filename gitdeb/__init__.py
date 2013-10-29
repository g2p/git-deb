import collections
import debian.deb822
import email.utils
import os
import re
import subprocess
import sys


def ignore(*args):
    pass

def printerr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def bail(msg):
    printerr(msg)
    sys.exit(1)

warn = printerr
debug = ignore

def backtick(cmd):
    return subprocess.check_output(cmd).decode().rstrip()

# Don't write to ~/.local/share/keyrings,
# it's where gnome-keyrings stores secrets.
KEYRINGS_PATH = (
    os.path.expanduser('~/.local/share/public-keyrings'),
    os.path.expanduser('~/.local/share/keyrings'), '/usr/share/keyrings')


class Keyrings(collections.OrderedDict):
    def __init__(self):
        super().__init__()
        self.missing = False
        for sname, fname in self._init_list:
            for sp in KEYRINGS_PATH:
                kr_path = os.path.join(sp, fname)
                if os.path.exists(kr_path):
                    self[sname] = kr_path
                    break
            else:
                self.missing = True

    def warn_missing(self):
        warn('Some keyrings are missing, please run `git deb get-keyrings`')

    _init_list = (
        ('debian', 'debian-keyring.gpg'),
        ('debian-maintainers', 'debian-maintainers.gpg'),
        ('debian-emeritus', 'emeritus-keyring.gpg'),
        ('debian-emeritus-pgp', 'emeritus-keyring.pgp'),
        ('debian-removed', 'removed-keys.gpg'),
        ('debian-removed-pgp', 'removed-keys.pgp'),
    )


# very relaxed, we'll be dealing with historical data
VERSION_LINE_RE = re.compile(r'^[a-z0-9][a-z0-9+.-]*\s+\(([^ ]+)\)')
AUTHOR_LINE_RE = re.compile(r'^ --\s*([^<>]*<[^<>]+>)  (.*)$')

def parse_changelog(cl, skip_versions, just_one=False):
    top_entry = True
    within = False
    versions = []
    for line in cl:
        line = line.rstrip()
        if not line:
            continue
        if not within:
            if line in ('Local variables:', 'Old Changelog:'):
                break
            match = VERSION_LINE_RE.match(line)
            if not match:
                warn('Giving up on changelog {!r}'.format(line))
                break
            ver1, = match.groups()
            versions.append(ver1)
            if not top_entry and ver1 in skip_versions:
                break
            within = True
        else:
            match = AUTHOR_LINE_RE.match(line)
            if not match:
                continue
            if top_entry:
                author, date = match.groups()
                date = email.utils.parsedate_to_datetime(date)
                if just_one:
                    return author, date, versions[0]
            top_entry = False
            within = False
    if top_entry:
        # There was no valid changelog stanza
        raise BrokenChangelog
    return (author, date), versions


SigInfo = collections.namedtuple('SigInfo', 'kr_name kid uid sig_ts sigtype cleartext')


def check_sig(keyrings, sequence, desc):
    sequence = list(sequence)
    for kr_name, kr_path in keyrings.items():
        gi = debian.deb822.GpgInfo.from_sequence(
            sequence, keyrings=[kr_path])
        if not gi.valid():
            continue
        break
    else:
        # On wget_1.5.3-3.1.dsc
        # ERRSIG 7D7C0636C76F38D2 20 2 01 1039606003 4
        # indicating problems with an ElGamal signature
        # gnupg 1.2.5-3 can verify it, 1.4.0-3 can't:
        # 2002-12-11 1039606003 0 3 0 20 2 01 576E100B518D2F1636B028053CB892502FA3BC2D
        # On sudo_1.6.2p2-2.2.dsc
        # ERRSIG 7D7C0636C76F38D2 20 3 01 1019775429 4
        # Those keys are compromised:
        # http://lists.gnupg.org/pipermail/gnupg-announce/2003q4/000160.html

        # Or missing keys
        # On grub_0.97-16.1~bpo.1.dsc
        # ERRSIG 6908386EC98FE2A1 17 2 01 1160038149 9
        if 'NO_PUBKEY' in gi and keyrings.missing:
            keyrings.warn_missing()
        bail('No valid signature on {} {}'.format(desc, gi))
    # See /usr/share/doc/gnupg/DETAILS.gz
    for sigtype in 'GOODSIG REVKEYSIG EXPKEYSIG'.split():
        try:
            kid, uid, *extra = gi[sigtype]
        except KeyError:
            continue
        break
    else:
        bail('Not a good signature {}'.format(gi))
    # Getting (only) the cleartext is way too tricky,
    # hopefully this guarantees there is a single signature
    # and we're not getting junk outside the signed area
    with subprocess.Popen(
        ['gpg', '--decrypt', '--keyring', kr_path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE
    ) as proc:
        cleartext, err = proc.communicate(b''.join(sequence))
        assert proc.returncode == 0, (cleartext, err)
    (fprint, sig_date, sig_ts, exp_ts, sigver, reserved, pkalg,
     hashalg, sigclass, fprint1, *extra) = gi['VALIDSIG']
    #sigid, date1, ts1, *extra = gi['SIG_ID']
    return SigInfo(kr_name, kid, uid, sig_ts, sigtype, cleartext)

