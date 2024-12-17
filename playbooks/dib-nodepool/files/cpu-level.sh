#!/usr/bin/env bash

function report_cpu_flags() {
    local flag

    for flag; do
        ## Note, it's important to keep a trailing space
        case " ${flags} " in
            *" ${flag} "*)
                echo "  ${flag} Found"
                ;;
            *)
                echo "  ${flag} NOT Found"
                ;;
        esac
    done
}

data=$(< /proc/cpuinfo)
flags=""
flags=$(grep "^flags[[:space:]]*:" <<< "${data}" | head -n 1)
flags="${flags#*:}"
flags="${flags## }"

echo "${flags}"

echo "x86_64-v1"
report_cpu_flags lm cmov cx8 fpu fxsr mmx syscall sse2
echo "x86_64-v2"
report_cpu_flags cx16 lahf_lm popcnt sse4_1 sse4_2 ssse3
echo "x86_64-v3"
report_cpu_flags avx avx2 bmi1 bmi2 f16c fma abm movbe xsave
echo "x86_64-v4"
report_cpu_flags avx512f avx512bw avx512cd avx512dq avx512vl
