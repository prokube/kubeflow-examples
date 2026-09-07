override REGISTRY := europe-west3-docker.pkg.dev/prokube/development
TAG ?= local-$(shell git rev-parse --short HEAD)

IMAGES := minimal-mnist streamlit-example mobile-price-classification \
	minimal-custom-kserve-predictor minimal-predictor minimal-transformer

.PHONY: build-all push-all $(addprefix build-,$(IMAGES)) $(addprefix push-,$(IMAGES))

build-all: $(addprefix build-,$(IMAGES))

push-all: $(addprefix push-,$(IMAGES))

build-minimal-mnist:
	docker build -t $(REGISTRY)/minimal-mnist:$(TAG) images/minimal-mnist

build-streamlit-example:
	docker build -t $(REGISTRY)/streamlit-example:$(TAG) images/streamlit-example

build-mobile-price-classification:
	docker build -t $(REGISTRY)/mobile-price-classification:$(TAG) pipelines/lightweight-python-package

build-minimal-custom-kserve-predictor:
	docker build -t $(REGISTRY)/minimal-custom-kserve-predictor:$(TAG) serving/minimal-custom-kserve-predictor

build-minimal-predictor:
	docker build -t $(REGISTRY)/minimal-predictor:$(TAG) serving/minimal-example-shadow-deployment/minimal-predictor

build-minimal-transformer:
	docker build -t $(REGISTRY)/minimal-transformer:$(TAG) serving/minimal-example-shadow-deployment/minimal-transformer

$(addprefix push-,$(IMAGES)): push-%: build-%
	docker push $(REGISTRY)/$*:$(TAG)
