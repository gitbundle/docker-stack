#!/bin/sh

ls -al /
/nsqlookupd -version
/nsqd -version
/nsqadmin -version

/nsqlookupd -tcp-address=:4160 -http-address=:4161 -verbose >/data/nsqlookupd.log 2>&1 &
/nsqd --lookupd-tcp-address=:4160 -tcp-address=:4150 -http-address=:4151 -https-address=:4152 -max-req-timeout=240h -verbose >/data/nsqd.log 2>&1 &
# /nsqd --lookupd-tcp-address=:4160 -tcp-address=:4150 -http-address=:4151 -https-address=:4152 -verbose >/data/nsqd.log 2>&1 &
/nsqadmin --lookupd-http-address=:4161 -http-address=:4171 -verbose
