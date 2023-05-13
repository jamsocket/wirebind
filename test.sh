#!/bin/sh

set -e

cd javascript
turbo test

cd ../python
poetry run pytest
