#!/usr/bin/env bash
# Stop the local site (data is kept in Podman volumes srcmsr-db / srcmsr-html).
podman pod stop srcmsr
