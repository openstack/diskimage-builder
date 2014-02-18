#!/bin/bash

install-packages yum-utils

package-cleanup --oldkernels -y --count=1
