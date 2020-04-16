# Product labelling

Short description to do


## Quick start

### Using docker

```
docker run --env juliedjidji/djangoapp:latest
```

## Configuration

Each variable can be overriden using environment variables.

Product-labelling configuration
| Key | Default | Description |
| --------------------- | ------- | ------------------------------------------------------------------ |
| `model` | `none` | URL of text classification model (must be configured) |
| `db_type` | `sqlite3` | Supported modes are : `postgres` |

Product-labelling configuration if `dbtype`==`postgres`
| Key | Default | Description |
| --------------------- | ------- | ------------------------------------------------------------------ |
| `db_password` | `none` | See [django configuration](https://docs.djangoproject.com/fr/3.0/ref/settings/#std:setting-DATABASES) (must be configured) |
| `db_name` | `none` | See [django configuration](https://docs.djangoproject.com/fr/3.0/ref/settings/#std:setting-DATABASES) (must be configured) |
| `db_user` | `none` | See [django configuration](https://docs.djangoproject.com/fr/3.0/ref/settings/#std:setting-DATABASES) (must be configured) |
| `db_host` | `localhost` | See [django configuration](https://docs.djangoproject.com/fr/3.0/ref/settings/#std:setting-DATABASES) |
| `db_port` | `5432` | See [django configuration](https://docs.djangoproject.com/fr/3.0/ref/settings/#std:setting-DATABASES) |

## Documentation

See [Django documentation](https://docs.djangoproject.com/fr/3.0/)



