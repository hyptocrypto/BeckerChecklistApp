#/bin/bash

docker build . -t becker_app -f ./Dockerfile && docker tag becker_app gcr.io/proven-country-295110/becker_app:latest && docker push gcr.io/proven-country-295110/becker_app:latest
