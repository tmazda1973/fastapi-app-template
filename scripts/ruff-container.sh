#!/bin/bash
docker exec fastapi-app /opt/conda/envs/myenv/bin/ruff "$@"
