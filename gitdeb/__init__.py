import email.utils
import re

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


