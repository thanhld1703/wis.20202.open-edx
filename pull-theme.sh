#!/usr/bin/env bash

git pull
echo 2 | sudo rm -R ~/hust-edutech/edx-platform/themes/$1
cp -R ~/PycharmProjects/wis.20202.open-edx/edx-platform/themes/$1/ ~/hust-edutech/edx-platform/themes/$1

