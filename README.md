# stacks
Stack your progress and achieve greatness.

## Develop

### Setup
This project has the fixins to use VSCode dev containers.
You need to mod `setup-dev.sh` to include you git creds.

You should use the VS Code command palette and "reopen in Container".
But if you need to build and manage docker manually here are some useful commands:

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
```alembic revision --autogenerate -m "message"```

#### Postgres Changes on prod
```./cloud-sql-proxy $STACKS_DB_CONNECTION --port 9999```

```ENV=prod-debug alembic upgrade head```

### Run Locally 
``gunicorn```

Check `localhost:8000/docs` to confirm the API is running

### Deploy
```
gcloud auth login

gcloud auth configure-docker us-central1-docker.pkg.dev

./deploy.sh
```

# Decisions

## ULIDs
ULIDs are lexographically sortable and are shorter than UUIDs so they make for good IDs. They provide faster indexing than UUIDs. They are better than integers because they are resilient to db mess-ups.
I am generating ULIDs server-side because Postgres doesn't support ULID generation out-of-the-box. I looked at installing an extension but there's a learning curve. https://github.com/pksunkara/pgx_ulid

Typing throughout is defined as UUID, to be compatible with Postgres. But the UUIDs are generated as ULIDs, so they give us the benefits we want.
