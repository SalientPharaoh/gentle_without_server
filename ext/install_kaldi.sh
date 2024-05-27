#!/bin/bash

# Prepare Kaldi
cd kaldi/tools
make clean
make
cd ../src
# make clean (sometimes helpful after upgrading upstream?)
./configure --static --static-math=yes --fst-root=/content/gentle_without_server/openfst-1.6.9 --fst-version=1.6.9 --static-fst=yes --use-cuda=no
make depend
cd ../../
