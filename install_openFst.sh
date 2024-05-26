#!/bin/bash

sudo apt-get install -y gfortran make automake autoconf bzip2 sox wget

wget http://www.openfst.org/twiki/pub/FST/FstDownload/openfst-1.6.9.tar.gz
tar -xvzf openfst-1.6.9.tar.gz
cd openfst-1.6.9
./configure --prefix=`pwd` --enable-static --enable-shared --enable-far --enable-ngram-fsts
make -j
make install

echo "OpenFst installation is complete."
cd ..
