.PHONY: apply-flux apply-apps deploy reconcile build-and-deploy-claif-api teardown apply-registry apply-namespaces

# Apply namespaces resources
apply-namespaces:
	kubectl apply -f namespaces/namespaces.yaml
	kubectl apply -f namespaces/kustomization.yaml

# Apply registry resources manually (optional, if not using Flux)
apply-registry:
	kubectl apply -f registry/registry-deployment.yaml
	kubectl apply -f registry/registry-service.yaml
	kubectl rollout status deployment/registry -n registry

# Apply flux-system resources, including registry and dev-apps kustomizations
apply-flux:
	kubectl apply -f flux-system/gitrepository.yaml 
	kubectl apply -f flux-system/namespaces-kustomization.yaml
	kubectl apply -f flux-system/registry-kustomization.yaml
	kubectl apply -f flux-system/dev-apps-kustomization.yaml
	# Wait until the registry deployment is available
	until kubectl rollout status deployment/registry -n registry | grep -q "successfully rolled out"; do \
		echo "Waiting for registry deployment to be ready..."; \
		sleep 10; \
	done
	# Call the build-and-deploy-claif-api block once the registry is ready
	$(MAKE) build-and-deploy-claif-api


# Apply application resources
apply-apps:
	kubectl apply -k apps

# Deploy everything (Flux manages registry and apps)
deploy: apply-namespaces apply-flux apply-apps

# Force a Flux reconciliation
reconcile:
	kubectl -n flux-system rollout restart deployment/kustomize-controller

# Build, tag, push, and update deployment
build-and-deploy-claif-api:
	TAG=$$(date +%Y%m%d%H%M%S); \
	echo "Using tag: $$TAG"; \
	docker-compose build; \
	docker tag claif-api-claif-api:latest localhost:30500/claif-api:$$TAG; \
	docker push localhost:30500/claif-api:$$TAG; \
	kubectl set image deployment/claif-api claif-api=localhost:30500/claif-api:$$TAG -n default;

# Teardown everything including volumes
teardown:
	# Delete the application resources
	kubectl delete -k apps --ignore-not-found=true

	# Delete the flux-system resources
	kubectl delete -f flux-system/namespaces-kustomization.yaml --ignore-not-found=true
	kubectl delete -f flux-system/registry-kustomization.yaml --ignore-not-found=true
	kubectl delete -f flux-system/dev-apps-kustomization.yaml --ignore-not-found=true
	kubectl delete -f flux-system/gitrepository.yaml --ignore-not-found=true

	# Delete the namespaces resources
	kubectl delete -f namespaces/namespaces.yaml --ignore-not-found=true

	# Delete all PersistentVolumeClaims (PVCs)
	kubectl delete pvc --all --namespace=default --ignore-not-found=true
	kubectl delete pvc --all --namespace=registry --ignore-not-found=true

	# Optionally delete all PersistentVolumes (PVs) if they are not dynamically managed
	kubectl delete pv --all --ignore-not-found=true
