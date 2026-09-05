-- =============================================================================
-- schema.sql
--
-- Raw SQL reference for the Customer Management database.
--
-- NORMAL WORKFLOW (recommended): let Django create the tables for you.
--   1. python database/create_database.py     -- creates an empty DB
--   2. python manage.py migrate                -- creates every table
--      (auth_user, profiles, customers, sessions, admin log, etc.)
--
-- This file is provided as a manual / reference alternative in case you
-- want to inspect or create the schema by hand, e.g. for documentation,
-- a DB review, or setting up the database on a server where you cannot
-- run Django migrations directly. It mirrors exactly what
-- `python manage.py migrate` produces for this project (Django's default
-- auth_user table + this app's profiles and customers tables).
--
-- If you run this file manually, tell Django the tables already exist by
-- "faking" the initial migrations afterwards:
--   python manage.py migrate --fake
-- =============================================================================

CREATE DATABASE IF NOT EXISTS `customer_management_db`
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `customer_management_db`;

-- -----------------------------------------------------------------------------
-- auth_user  (Django's built-in user table -- every login, distributor or admin)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `auth_user` (
    `id`            BIGINT AUTO_INCREMENT PRIMARY KEY,
    `password`      VARCHAR(128)  NOT NULL,
    `last_login`    DATETIME(6)   NULL,
    `is_superuser`  TINYINT(1)    NOT NULL DEFAULT 0,
    `username`      VARCHAR(150)  NOT NULL UNIQUE,
    `first_name`    VARCHAR(150)  NOT NULL DEFAULT '',
    `last_name`     VARCHAR(150)  NOT NULL DEFAULT '',
    `email`         VARCHAR(254)  NOT NULL DEFAULT '',
    `is_staff`      TINYINT(1)    NOT NULL DEFAULT 0,
    `is_active`     TINYINT(1)    NOT NULL DEFAULT 1,
    `date_joined`   DATETIME(6)   NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- profiles  (Distributor / Admin role, one row per user)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `profiles` (
    `id`            BIGINT AUTO_INCREMENT PRIMARY KEY,
    `role`          VARCHAR(20)   NOT NULL DEFAULT 'distributor',   -- 'distributor' | 'admin'
    `phone`         VARCHAR(17)   NOT NULL DEFAULT '',
    `company_name`  VARCHAR(150)  NOT NULL DEFAULT '',
    `created_at`    DATETIME(6)   NOT NULL,
    `user_id`       BIGINT        NOT NULL UNIQUE,
    CONSTRAINT `fk_profiles_user`
        FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- customers  (the core CRUD entity, owned by a distributor)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `customers` (
    `id`             BIGINT AUTO_INCREMENT PRIMARY KEY,
    `name`           VARCHAR(150)  NOT NULL,
    `email`          VARCHAR(254)  NOT NULL DEFAULT '',
    `phone`          VARCHAR(17)   NOT NULL,
    `company_name`   VARCHAR(150)  NOT NULL DEFAULT '',
    `address_line`   VARCHAR(255)  NOT NULL DEFAULT '',
    `city`           VARCHAR(100)  NOT NULL DEFAULT '',
    `state`          VARCHAR(100)  NOT NULL DEFAULT '',
    `pincode`        VARCHAR(10)   NOT NULL DEFAULT '',
    `gst_number`     VARCHAR(20)   NOT NULL DEFAULT '',
    `status`         VARCHAR(10)   NOT NULL DEFAULT 'active',        -- 'active' | 'inactive'
    `notes`          LONGTEXT     NOT NULL,
    `created_at`     DATETIME(6)   NOT NULL,
    `updated_at`     DATETIME(6)   NOT NULL,
    `distributor_id` BIGINT        NOT NULL,
    CONSTRAINT `fk_customers_distributor`
        FOREIGN KEY (`distributor_id`) REFERENCES `auth_user` (`id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX `customers_name_idx`   ON `customers` (`name`);
CREATE INDEX `customers_phone_idx`  ON `customers` (`phone`);
CREATE INDEX `customers_status_idx` ON `customers` (`status`);
CREATE INDEX `customers_distributor_idx` ON `customers` (`distributor_id`);

-- -----------------------------------------------------------------------------
-- Optional: seed one Admin / Super Admin and one Distributor for quick testing.
-- NOTE: Django hashes passwords with PBKDF2 - you cannot insert a usable
-- plaintext password here. Create users properly instead with:
--   python manage.py createsuperuser
-- then, in Django Admin (/admin/) or the Django shell, set their Profile
-- role to 'admin'. Any user who registers through the app's /register/
-- page automatically gets the 'distributor' role.
-- -----------------------------------------------------------------------------
