#!/usr/bin/env bash

# rebuild
docker-compose down && docker-compose build && docker-compose up -d && docker-compose down
# tag
docker tag py-frameworks-bench_frameworks containers.cisco.com/szelenka/frameworks
docker tag py-frameworks-bench_controller containers.cisco.com/szelenka/frameworks-controller
docker tag py-frameworks-bench_nginx containers.cisco.com/szelenka/frameworks-nginx
docker tag py-frameworks-bench_postgresql containers.cisco.com/szelenka/frameworks-postgresql
# push
docker push containers.cisco.com/szelenka/frameworks
docker push containers.cisco.com/szelenka/frameworks-controller
docker push containers.cisco.com/szelenka/frameworks-nginx
docker push containers.cisco.com/szelenka/frameworks-postgresql
# deploy
helm template --name v1 helm/py-frameworks-bench > helm.yaml && kubectl apply -f helm.yaml

# copy off server
kubectl cp $(kubectl get pods -l app.kubernetes.io/name=py-frameworks-bench -o jsonpath="{.items[*].metadata.name}"):/opt/app-root/src/reports/results.csv .