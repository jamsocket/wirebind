#!/bin/sh

set -e

cd javascript
npm run test

cd ../python
poetry run pytest
