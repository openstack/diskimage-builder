path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
path="$( dirname $path)"
export DIB_CONTAINER_FILE="$path/files/Dockerfile"
