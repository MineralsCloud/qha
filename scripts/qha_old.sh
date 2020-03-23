#!/usr/bin/env bash

virtualenv qha_old
cd qha_old/bin/
source activate
cd ../ # I am at root/qha/qha_old
pip3 install qha==1.0.17
cp -R ../examples/* ./ # cp root/qha/examples to root/qha/qha_old/
cd silicon
qha run ./settings.yaml
cd ..
cd ice\ VII
qha run ./settings.yaml # I am at root/qha/qha_old/ice\ VII/
cd ..                   # I am at root/qha/qha_old
deactivate
cd ../ # I am at root/qha/
