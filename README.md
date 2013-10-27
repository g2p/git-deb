**git-deb** downloads the full history of a Debian package into Git.

## Requirements

Python 3.3, Pip, GPG, Git, Dpkg (specifically the dpkg-dev subpackage)

#### On Debian and Ubuntu

    sudo apt-get install python3-{debian,isodate,pip,requests} dpkg-dev

## Installation

    pip3 install --user -r https://raw.github.com/g2p/git-deb/master/requirements.txt
    #pip3 install --user -e.  # If you prefer running straight from git
    cp -fst ~/bin ~/.local/bin/git-{remote-,}deb  # Not needed if ~/.local/bin is in the PATH

## Usage

    git clone deb::pkgname

The history contains authors (from Debian changelogs) and
committers (from dsc signatures), both with appropriate dates.

    git log --graph --all --pretty='%Cred%H%Cblue%d%Creset%nChangelog %ai %an <%ae>%nSignature %ci %cn <%ce>%n%s%b%n'

Packages that have been in the archive for some time may have
signatures that can't be verified with current Debian keyrings.

    git deb get-keyrings

will download historical keyrings (using Apt).
Commits using those keys will be annotated.

## Fixes

In the case of bad/invalid/missing signatures, you may need to skip versions:

    git clone deb::sudo?skip=1.6.2p2-2.2 sudo
    git clone deb::gnupg?skip=1.4.6-1~bpo.1,1.4.6-2.1 gnupg

If a key isn't in the Debian keyrings but you do have it in your own keyring,
you may trust it manually:

    git clone 'deb::gnupg?skip=1.4.6-2.1&trust=6908386EC98FE2A1' gnupg

If a key is missing an email identity, you may provide it with another parameter:

    ?email='0123456789ABCDEF <email@host>'

## Build status

[![Build Status](https://travis-ci.org/g2p/git-deb.png)](https://travis-ci.org/g2p/git-deb)

