# backwards compatability with the previous environment
# variable for the ironic-agent source repository
if [ -n "${DIB_REPOREF_agent:-}" ]; then
  echo "WARNING: DIB_REPOREF_agent is deprecated. Please update to use DIB_REPOREF_ironic_agent instead."
  export DIB_REPOREF_ironic_agent=${DIB_REPOREF_agent}
fi
