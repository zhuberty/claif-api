.PHONY: apply-flux apply-apps

# Apply flux-system resources
apply-flux:
	kubectl apply -f clusters/local/dev/flux-system/gitrepository.yaml
	kubectl apply -f clusters/local/dev/flux-system/kustomization.yaml

# Apply application resources
apply-apps:
	kubectl apply -k clusters/local/dev/apps

# Deploy everything (both flux-system and apps)
deploy: apply-flux apply-apps

# Force a Flux reconciliation
reconcile:
	kubectl -n flux-system rollout restart deployment/flux-system-kustomize-controller
