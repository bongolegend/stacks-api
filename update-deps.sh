pip-compile requirements/prod.in --output-file=requirements/prod.txt
pip-compile requirements/dev.in --output-file=requirements/dev.txt
pip install -r requirements/prod.txt
pip install -r requirements/dev.txt