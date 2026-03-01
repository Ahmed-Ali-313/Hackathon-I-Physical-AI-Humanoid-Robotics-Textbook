# Deployment Scripts

This directory contains scripts for production deployment automation.

## Scripts

- `migrate-to-neon.sh` - Database migration from SQLite to Neon Postgres
- `rollback-database.sh` - Rollback procedure to revert to SQLite
- `verify-deployment.sh` - Post-deployment verification checklist

## Usage

All scripts should be run from the repository root:

```bash
# Database migration
./scripts/deployment/migrate-to-neon.sh

# Rollback if needed
./scripts/deployment/rollback-database.sh

# Verify deployment
./scripts/deployment/verify-deployment.sh
```

## Safety

- Always backup before migration
- Test rollback procedures before production
- Verify all environment variables are set
