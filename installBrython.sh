#!/bin/bash
if [ ! -d "static/brython" ]
then
	mkdir static/brython
	cd static/brython
	brython-cli --install
	cd ../..
	echo "Installed Brython in ./static"
else
	echo "Brython is already installed; Nothing to do."
fi
