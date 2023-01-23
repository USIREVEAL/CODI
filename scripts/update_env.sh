#!/usr/bin/env zsh

echo 'Freezing conda environment...'

echo 'conda list --export > environment.yml'
conda env export --name codi --from-history | grep -v "prefix" > ../environment.yml

echo 'conda environment (environment.yml) updated'
