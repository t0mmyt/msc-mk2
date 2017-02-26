.PHONY: obsloader tsdatastore interface push

all: obsloader tsdatastore interface

tsdatastore:
	docker build --build-arg SERVICE=tsdatastore --build-arg PORT=8163 -t seismic/tsdatastore .

obsloader:
	docker build --build-arg SERVICE=obsloader --build-arg PORT=8164 -t seismic/obsloader .

interface:
	docker build --build-arg SERVICE=interface --build-arg PORT=8180 -t seismic/interface .

push:
	for i in obsloader tsdatastore interface ; do \
	    docker push seismic/$$i ; \
	done
