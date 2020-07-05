# Due to the many historical problems mixing python2/3 versions and
# upgrading packaged system pip/setuptools/virtualenv binaries with
# upstream non-packaged versions, we wish to avoid this completely on
# modern distros.
if [[ $DISTRO_NAME =~ (centos|rhel) && $DIB_RELEASE > 7 ]]; then
    export DIB_INSTALLTYPE_pip_and_virtualenv=${DIB_INSTALLTYPE_pip_and_virtualenv:-package}

    if [[ ${DIB_INSTALLTYPE_pip_and_virtualenv} == "source" ]]; then
        echo "*** pip-and-virtualenv does not support 'source' install for $DISTRO_NAME/$DIB_RELEASE"
        exit 1
    fi
fi

# The default variables setup below are only useful during the phases
# that dib-python exists
if [[ ! -e /usr/local/bin/dib-python ]]; then
    return 0
fi

# NOTE(ianw): you don't want to call "dib-python -m pip" because that
# can leave behind interpreters #!/usr/local/bin/dib-python in
# scripts.  De-reference the link
_dib_python_path=$(readlink /usr/local/bin/dib-python)
export DIB_PYTHON_PIP="$_dib_python_path -m pip"
# We make an opinionated, but simplifying decision here that on
# Python3 platforms, just use venv.  There are some corner cases that
# the external "virtualenv" package still handles better, but for most
# purposes "venv" should be fine.
if [[ $DIB_PYTHON_VERSION == 3 ]]; then
    export DIB_PYTHON_VIRTUALENV="$_dib_python_path -m venv"
else
    export DIB_PYTHON_VIRTUALENV="$_dib_python_path -m virtualenv"
fi
