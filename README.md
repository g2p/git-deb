
# git-deb

git-deb downloads the full history of a Debian package into Git.

# Requirements

Python 3.3, Pip, GPG, Git

You may install the following packages first:

    sudo aptitude install python3-{apt,chardet,debian,isodate,pip,requests}

# Installation

    pip3 install --user git-deb
    cp -lt ~/bin ~/.local/bin/git-{remote-,}deb

# Usage
    
    git clone deb::pkgname

The history contains authors (from Debian changelogs) and
committers (from dsc signatures), both with appropriate dates.

    git log --graph --all --pretty='%Cred%H%Cblue%d%Creset%nChangelog %ai %an %ae%nSignature %ci %cn %ce%n%s%b%n'

Packages that have been in the archive for some time may have
signatures that can't be verified with current Debian keyrings.

    git deb get-keyrings

will download historical keyrings (using Apt).
In the case of bad/invalid/missing signatures, you may need to skip versions:

    git clone deb::sudo?skip=1.6.2p2-2.2 sudo
    git clone deb::gnupg?skip=1.4.6-1~bpo.1,1.4.6-2.1 gnupg

