# Product labelling

Application for labelling transaction receipts, developed as part of the transaction data project. Predictions are made using the fastText algorithm.

The application includes two parts :

* The first one enables users to visualize the results (preprocessing and predictions of the model). The access to this functionality is through the link ~/post/author
* The second one available at ~/author aims at simplifying the labelling process.

## Quick start

### Using docker

```
docker run --env inseefrlab/product-labelling
```

## Configuration

Each variable can be overriden using environment variables.

Product-labelling configuration
| Key | Default | Description |
| --------------------- | ------- | ------------------------------------------------------------------ |
| `model` | `none` | URL of text classification model - fasttext model saved with .ftz extension (must be configured) |
| `nomenclature` | `none` | URL of a CSV file which contains complete list of nomenclature products with no header |
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



