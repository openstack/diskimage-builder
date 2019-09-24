# For backward compat (centos vs centos7)
export DIB_FLAVOR=${DIB_RELEASE:-GenericCloud}
export DIB_RELEASE=7

# Useful for elements that work with fedora (dnf) & centos
export YUM=${YUM:-yum}

