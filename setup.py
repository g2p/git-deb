#!/usr/bin/env python3.3
# encoding: utf-8

from distutils.core import setup

setup(
    name='git-deb',
    version='0.1.2',
    author='Gabriel de Perthuis',
    author_email='g2p.code+gitdeb@gmail.com',
    url='https://github.com/g2p/git-deb',
    license='GNU GPL',
    keywords='git debian packaging import debsnap snapshot.debian.org',
    description='Bring any Debian package to Git',
    scripts=['git-deb', 'git-remote-deb'],
    install_requires=[
        'chardet',
        'isodate',
        'python-debian >= 0.1.21-nmu1',
        'requests',
    ],
    classifiers='''
        Programming Language :: Python :: 3
        Programming Language :: Python :: 3.3
        License :: OSI Approved :: GNU General Public License (GPL)
        Operating System :: POSIX :: Linux
        Topic :: Utilities
        Environment :: Console
    '''.strip().splitlines(),
    long_description='''
    git-deb downloads the full history of a Debian package into Git.
    Usage:
    
        git clone deb::pkgname

    See `github.com/g2p/git-deb <https://github.com/g2p/git-deb#readme>`_
    for installation and usage instructions.''')

