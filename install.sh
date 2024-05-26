#!/bin/bash

set -e

git submodule init
git submodule update

./install_deps.sh
echo "Dependencies installed."

echo "Installing OpenFst..."
chmod +x install_openFst.sh
./install_openFst.sh
echo "OpenFst installed."

echo "Installing Kaldi..."
(cd ext && ./install_kaldi.sh)
echo "Kaldi installed."

echo "Installing models..."
./install_models.sh
echo "Models installed."

cd ext && make depend && make
echo "Gentle is ready to use."
