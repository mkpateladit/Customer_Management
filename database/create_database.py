#!/usr/bin/env python
"""
create_database.py
-------------------
Creates the MySQL database used by the Customer Management project.

This script ONLY creates the empty database (schema). The actual tables
are created afterwards by Django's migration system, which keeps the
database structure in sync with customers/models.py automatically:

    python create_database.py      # creates the database (this script)
    python manage.py migrate       # creates all the tables

If you would rather create the tables by hand (e.g. you don't want to
run Django's migrations), use database/schema.sql instead - it contains
the equivalent raw SQL `CREATE TABLE` statements.

Configuration is read from environment variables (with sensible
defaults), the same variables used by customer_project/settings.py:

    DB_NAME      (default: customer_management_db)
    DB_USER      (default: root)
    DB_PASSWORD  (default: empty)
    DB_HOST      (default: localhost)
    DB_PORT      (default: 3306)

Usage:
    python create_database.py
    # or override credentials inline:
    DB_USER=root DB_PASSWORD=secret python create_database.py
"""

import os
import sys

try:
    import mysql.connector
    from mysql.connector import errorcode
except ImportError:
    print("The 'mysql-connector-python' package is required.")
    print("Install it with:  pip install mysql-connector-python")
    sys.exit(1)


def main():
    db_name = os.environ.get('DB_NAME', 'customer_management_db')
    db_user = os.environ.get('DB_USER', 'root')
    db_password = os.environ.get('DB_PASSWORD', '')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = int(os.environ.get('DB_PORT', '3306'))

    print(f"Connecting to MySQL server at {db_host}:{db_port} as '{db_user}'...")

    try:
        connection = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
        )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied. Check DB_USER / DB_PASSWORD.")
        else:
            print(f"Could not connect to MySQL: {err}")
        sys.exit(1)

    cursor = connection.cursor()

    try:
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        print(f"Database '{db_name}' is ready.")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        sys.exit(1)
    finally:
        cursor.close()
        connection.close()

    print()
    print("Next steps:")
    print("  1. cd into the project root (where manage.py lives)")
    print("  2. python manage.py migrate      # creates all tables")
    print("  3. python manage.py createsuperuser   # create an Admin / Super Admin login")
    print("     (after creating the superuser, set its role to 'admin' in Django Admin")
    print("      under Profiles, or run: python manage.py shell and update it there)")


if __name__ == '__main__':
    main()
