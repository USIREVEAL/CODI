#!/bin/zsh

conda init zsh
source ~/.zshrc
conda activate codi
cd ../codi/
echo "starting codi's server..."
python3 manage.py runserver 127.0.0.1:8000
