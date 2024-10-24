.PHONY: apply-apps deploy reconcile build-and-deploy-claif-api teardown apply-namespaces

# Apply namespaces resources
apply-namespaces:
	kubectl apply -f namespaces/namespaces.yaml

# Apply application resources
apply-apps:
	kubectl apply -k apps

# Deploy everything
deploy: apply-namespaces apply-apps

# Build, tag, push, and update deployment
build-and-deploy-claif-api:
	TAG=$$(date +%Y%m%d%H%M%S); \
	echo "Using tag: $$TAG"; \
	docker-compose build; \
	docker tag claif-api-claif-api:latest localhost:30500/claif-api:$$TAG; \
	docker push localhost:30500/claif-api:$$TAG; \
	kubectl set image deployment/claif-api claif-api=localhost:30500/claif-api:$$TAG -n claif-dev;

# Teardown everything including volumes
teardown:
	# Delete the application resources
	kubectl delete -k apps --ignore-not-found=true

	# Delete the namespaces resources
	kubectl delete -f namespaces/namespaces.yaml --ignore-not-found=true

	# Delete all PersistentVolumeClaims (PVCs)
	kubectl delete pvc --all --namespace=claif-dev --ignore-not-found=true
