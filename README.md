# Product labelling

Application for labelling transaction receipts, developed as part of the transaction data project. Predictions are made using the fastText algorithm.

The application available at ~/home includes two parts :

* The main part aims at simplifying the labelling process. One label from a file are automatically offered to the user who has to choose the rigth associated category/label.
* The second one enables users to visualize the results (preprocessing and predictions of the model).

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
| `db_type` | `sqlite3` | Other supported mode : `postgres` |

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



