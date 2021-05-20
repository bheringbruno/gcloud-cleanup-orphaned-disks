IMAGE_TAG?=bhtest
PROJECT?=tvg-network
REGION?=us-west1-b
CONTEXT_K8S?=qa-microservices-primary-us-west1
ENV?=qa
SLACK_CREDENTIALS:=$(shell ansible-vault view secrets/${PROJECT}/slack-bot-access --vault-password-file=vault_pass.sh | base64)
SLACK_CHANNEL_ID:=$(shell ansible-vault view secrets/${PROJECT}/slack-channel-id --vault-password-file=vault_pass.sh | base64)
SLACK_CREDENTIALS_DECODED=$(shell echo ${SLACK_CREDENTIALS} | base64 -d)
SLACK_CHANNEL_ID_DECODED=$(shell echo ${SLACK_CHANNEL_ID} | base64 -d)

build:
	cd docker/ && docker build -t $(IMAGE_TAG) .

run:
	docker run -it --rm \
		-v ~/.config/gcloud:/root/.config/gcloud \
		$(IMAGE_TAG) --channel $(SLACK_CHANNEL_ID_DECODED) --slack-token $(SLACK_CREDENTIALS_DECODED) --project $(PROJECT)

shell:
	docker run -it --rm \
		-v ~/.config/gcloud:/root/.config/gcloud:ro \
		--entrypoint="" \
		$(IMAGE_TAG) sh

kubernetes_secret_sed:
	sed -i.bak "s#\SLACK_CREDENTIALS_VALUE#${SLACK_CREDENTIALS_DECODED}#" kubernetes/cronjob-${ENV}.yaml && \
	sed -i.bak "s#\SLACK_CHANNEL_ID_VALUE#${SLACK_CHANNEL_ID_DECODED}#" kubernetes/cronjob-${ENV}.yaml
kubernetes_image_sed:
	sed -i.bak "s#\IMAGE_TAG#${IMAGE_TAG}#" kubernetes/cronjob-${ENV}.yaml
kubernetes_auth:
	gcloud container clusters get-credentials ${CONTEXT_K8S} --zone ${REGION} --project ${PROJECT}
kubernetes_dry_run:
	cd  kubernetes/ && kubectl apply --dry-run=true -f cronjob-${ENV}.yaml
kubernetes_apply: kubernetes_auth kubernetes_image_sed kubernetes_secret_sed kubernetes_dry_run 
	cd  kubernetes/ && kubectl apply -f cronjob-${ENV}.yaml
