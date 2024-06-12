export ARTIFACT_REGISTRY=us-central1-docker.pkg.dev/stacks-426020/stacks-api
# tag with both the commit hash and "latest". "latest" is used to decide which image to deploy
docker build . \
    --tag $ARTIFACT_REGISTRY/stacks-api:prod-$(git rev-parse --short HEAD) \
    --tag $ARTIFACT_REGISTRY/stacks-api:latest \
    --target prod \
    --platform linux/amd64
docker push $ARTIFACT_REGISTRY/stacks-api --all-tags