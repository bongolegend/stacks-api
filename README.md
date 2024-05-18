# stacks
Stack your progress and achieve greatness.

## Motivation
We like to stay connected, and we like to accomplish things. Do both with `stacks`; declare your goals to your friends and be held accountable.

## Develop

### Setup
Run your dev env in docker. You're welcome.

To build the image
```
docker build --tag stacks:dev --target dev .
```

To run the containers
```
docker compose up
docker compose down
```


### New dependencies
Add new deps to `requirements/*.in`, then run this to recompile the lock files, then reinstall.
```
pip-compile requirements/prod.in --output-file=requirements/prod.txt
pip-compile requirements/dev.in --output-file=requirements/dev.txt
pip install -r requirements/prod.txt
pip install -r requirements/dev.txt
```
