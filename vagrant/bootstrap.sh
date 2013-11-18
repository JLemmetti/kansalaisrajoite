#!/bin/bash

# Readies kansalaisrajoite server for development

# Install development tools (git, python dev tools, postgresql)
apt-get update
apt-get install -y git python-software-properties python-dev python-pip python-flup libffi-dev postgresql libpq-dev

# Install python dependencies
pip install bottle sqlalchemy bottle-sqlalchemy bcrypt beaker pycrypto
pip install argparse pycparser wsgiref cffi psycopg2 --upgrade

# Create a database user and the database, and import fixture contents
cd /vagrant/kansalaisrajoite/db/
sudo -u postgres createuser -E -d -r -S vagrant
sudo -u vagrant createdb kansalaisrajoite
sudo -u vagrant psql -d kansalaisrajoite -f create.sql
sudo -u vagrant psql -d kansalaisrajoite -f populate.sql