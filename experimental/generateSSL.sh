#!/bin/bash
if [ ! -f ./sslCert.pem ] && [ ! -f ./sslKey.pem ]
then
	openssl req -x509 -newkey rsa:4096 -nodes -out sslCert.pem -keyout sslKey.pem -days 365
else
	echo "Key files already exist; Nothing to do..."
fi
