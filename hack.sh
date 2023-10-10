#!/bin/sh

# NOTE: This is for local development. Should be removed in the production.
cat /workspace/local.crt >>/etc/ssl/certs/ca-certificates.crt