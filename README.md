# stacks
Stack your progress and achieve greatness.

## Motivation
We like to stay connected, and we like to accomplish things. Do both with `stacks`; declare your goals to your friends and be held accountable.

## Develop

### Setup
This project has the fixins to use VSCode dev containers.
You need to mod `setup.sh` to include you git creds.

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
Add new deps to `requirements/*.in`, then run `./update-deps.sh` to recompile the lock files and reinstall.

### Postgres changes
alembic revision --autogenerate -m "message"