#!/usr/bin/env bash

rm -R ~/PycharmProjects/wis.20202.open-edx/edx-platform/themes/$1/
cp -R ~/hust-edutech/edx-platform/themes/$1 ~/PycharmProjects/wis.20202.open-edx/edx-platform/themes/$1/
git add ~/PycharmProjects/wis.20202.open-edx/edx-platform/themes/
git commit -m "update $1"
git push -u origin backup
