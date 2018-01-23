export DISTRO_NAME=fedora
export DIB_RELEASE=${DIB_RELEASE:-27}

# Note the filename URL has a "sub-release" in it
#  http:// ... Fedora-Cloud-Base-25-1.3.x86_64.qcow2
#                                   ^^^
# It's not exactly clear how this is generated, or how we could
# determine this programatically.  Other projects have more
# complicated regex-based scripts to find this, which we can examine
# if this becomes an issue ... see thread at [1]
#
# [1] https://lists.fedoraproject.org/archives/list/cloud@lists.fedoraproject.org/thread/2WFO2FKIGUQYRQXIR35UVJGRHF7LQENJ/

if [[ ${DIB_RELEASE} == '26' ]]; then
    export DIB_FEDORA_SUBRELEASE=1.5
elif [[ ${DIB_RELEASE} == '27' ]]; then
    export DIB_FEDORA_SUBRELEASE=1.6
else
    echo "Unsupported Fedora release"
    exit 1
fi
