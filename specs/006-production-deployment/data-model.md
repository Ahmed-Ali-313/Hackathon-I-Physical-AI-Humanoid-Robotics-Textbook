# Data Model: Production Deployment

**Feature**: 006-production-deployment
**Date**: 2026-03-02
**Purpose**: Define deployment-specific entities and their relationships

## Overview

This data model describes entities used during deployment and monitoring. These are **not database tables** but rather conceptual entities for tracking deployment state, configuration, and health.

---

## Entity Definitions

### 1. DeploymentEnvironment

Represents a complete production deployment across all platforms.

**Attributes**:
- `environment_id`: string (unique identifier, e.g., "prod-2026-03-02")
- `frontend_url`: string (Vercel deployment URL, e.g., "https://ai-native-book.vercel.app")
- `backend_url`: string (Render deployment URL, e.g., "https://ai-native-book-backend.onrender.com")
- `database_url`: string (Neon connection string, masked for security)
- `status`: enum (pending, deploying, live, failed, rolled_back)
- `deployed_at`: timestamp (ISO 8601)
- `deployed_by`: string (user or "automated")
- `git_commit`: string (commit hash, 7 chars)
- `version`: string (semantic version, e.g., "1.0.0")

**State Transitions**:
```
pending → deploying → live
deploying → failed → rolled_back
live → deploying (for updates)
```

**Validation Rules**:
- `frontend_url` must be valid HTTPS URL
- `backend_url` must be valid HTTPS URL
- `database_url` must start with "postgresql://"
- `git_commit` must be valid commit hash
- `status` cannot transition from `live` to `pending`

**Relationships**:
- Has many `EnvironmentVariable` (configuration)
- Has many `HealthCheck` (monitoring)
- Has one `RollbackPoint` (recovery)

---

### 2. EnvironmentVariable

Represents a configuration secret required for deployment.

**Attributes**:
- `variable_id`: string (unique identifier)
- `name`: string (e.g., "OPENAI_API_KEY")
- `platform`: enum (vercel, render, github, local)
- `required`: boolean (true if deployment fails without it)
- `validated`: boolean (true if startup validation passed)
- `value_set`: boolean (true if value configured, false if missing)
- `last_updated`: timestamp (ISO 8601)
- `validation_rule`: string (e.g., "starts_with:sk-", "min_length:32")

**Validation Rules**:
- `name` must be uppercase with underscores (e.g., "DATABASE_URL")
- `platform` must be one of: vercel, render, github, local
- `required` variables must have `value_set = true` before deployment
- `validation_rule` format: "rule_name:parameter"

**Relationships**:
- Belongs to `DeploymentEnvironment`

**Required Variables by Platform**:

| Platform | Variable | Validation Rule |
|----------|----------|-----------------|
| Render | DATABASE_URL | starts_with:postgresql:// |
| Render | OPENAI_API_KEY | starts_with:sk- |
| Render | QDRANT_URL | starts_with:https:// |
| Render | QDRANT_API_KEY | min_length:10 |
| Render | JWT_SECRET_KEY | min_length:32 |
| Render | FRONTEND_URL | starts_with:https:// |
| Vercel | REACT_APP_API_URL | starts_with:https:// |

---

### 3. MigrationRecord

Represents a database migration execution (SQLite → Neon or rollback).

**Attributes**:
- `migration_id`: string (unique identifier, e.g., "mig-2026-03-02-001")
- `direction`: enum (forward, rollback)
- `source_type`: enum (sqlite, neon)
- `target_type`: enum (sqlite, neon)
- `status`: enum (pending, running, completed, failed, rolled_back)
- `tables_migrated`: array of strings (e.g., ["users", "conversations"])
- `records_before`: object (table → count mapping)
- `records_after`: object (table → count mapping)
- `integrity_verified`: boolean (true if foreign keys intact)
- `started_at`: timestamp (ISO 8601)
- `completed_at`: timestamp (ISO 8601, null if not completed)
- `duration_seconds`: integer (calculated from timestamps)
- `error_message`: string (null if successful)
- `backup_path`: string (SQLite backup file path)

**State Transitions**:
```
pending → running → completed
running → failed → rolled_back
```

**Validation Rules**:
- `records_before` and `records_after` must match for successful migration
- `integrity_verified` must be true for status = completed
- `backup_path` must exist before starting migration
- `duration_seconds` must be < 300 (5 minutes) for <100MB database

**Relationships**:
- Belongs to `DeploymentEnvironment`
- Creates `RollbackPoint` (for recovery)

**Example Record Counts**:
```json
{
  "records_before": {
    "users": 10,
    "conversations": 25,
    "messages": 150,
    "translated_chapters": 5,
    "personalization_profiles": 10
  },
  "records_after": {
    "users": 10,
    "conversations": 25,
    "messages": 150,
    "translated_chapters": 5,
    "personalization_profiles": 10
  }
}
```

---

### 4. HealthCheck

Represents a service health status check.

**Attributes**:
- `check_id`: string (unique identifier)
- `service`: enum (backend, database, openai, qdrant, frontend)
- `status`: enum (healthy, degraded, unhealthy, unknown)
- `response_time_ms`: integer (null if unhealthy)
- `last_check`: timestamp (ISO 8601)
- `last_success`: timestamp (ISO 8601, null if never succeeded)
- `consecutive_failures`: integer (0 if healthy)
- `error_message`: string (null if healthy)
- `endpoint`: string (URL checked, e.g., "/api/health")

**State Transitions**:
```
unknown → healthy
healthy → degraded (slow response)
degraded → unhealthy (timeout/error)
unhealthy → healthy (recovery)
```

**Validation Rules**:
- `response_time_ms` must be < 2000 for status = healthy
- `response_time_ms` between 2000-5000 for status = degraded
- `response_time_ms` > 5000 or null for status = unhealthy
- `consecutive_failures` > 3 triggers alert

**Relationships**:
- Belongs to `DeploymentEnvironment`

**Health Status Criteria**:

| Service | Healthy | Degraded | Unhealthy |
|---------|---------|----------|-----------|
| Backend | <2s response | 2-5s response | >5s or error |
| Database | Connection OK | Slow queries | Connection failed |
| OpenAI | API responds | Rate limited | Invalid key |
| Qdrant | Vector search OK | Slow search | Connection failed |
| Frontend | Loads <3s | Loads 3-10s | Timeout or error |

---

### 5. RollbackPoint

Represents a snapshot for rollback recovery.

**Attributes**:
- `rollback_id`: string (unique identifier, e.g., "rb-2026-03-02-001")
- `component`: enum (database, backend, frontend, all)
- `version`: string (git commit hash or deployment ID)
- `backup_path`: string (for database: SQLite file path)
- `deployment_url`: string (for backend/frontend: previous deployment URL)
- `created_at`: timestamp (ISO 8601)
- `valid_until`: timestamp (ISO 8601, 7 days for database)
- `is_valid`: boolean (false if expired or deleted)
- `rollback_procedure`: string (command to execute rollback)

**Validation Rules**:
- `backup_path` must exist for component = database
- `valid_until` must be > current time for is_valid = true
- Database backups expire after 7 days
- Code rollbacks never expire (git history permanent)

**Relationships**:
- Belongs to `DeploymentEnvironment`
- Created by `MigrationRecord` (for database)

**Rollback Procedures**:

| Component | Procedure |
|-----------|-----------|
| Database | Update DATABASE_URL to SQLite, restart backend |
| Backend | Redeploy previous commit via Render dashboard |
| Frontend | Execute `vercel rollback` or use dashboard |
| All | Execute all three procedures in sequence |

---

## Entity Relationships

```
DeploymentEnvironment (1)
├── EnvironmentVariable (many)
├── MigrationRecord (many)
├── HealthCheck (many)
└── RollbackPoint (1)

MigrationRecord (1)
└── RollbackPoint (1) [creates]
```

---

## State Machine Diagrams

### DeploymentEnvironment States

```
[pending] --deploy--> [deploying]
[deploying] --success--> [live]
[deploying] --failure--> [failed]
[failed] --rollback--> [rolled_back]
[live] --update--> [deploying]
```

### MigrationRecord States

```
[pending] --start--> [running]
[running] --verify--> [completed]
[running] --error--> [failed]
[failed] --rollback--> [rolled_back]
```

### HealthCheck States

```
[unknown] --check--> [healthy]
[healthy] --slow--> [degraded]
[degraded] --timeout--> [unhealthy]
[unhealthy] --recover--> [healthy]
```

---

## Validation Matrix

| Entity | Field | Validation | Error Message |
|--------|-------|------------|---------------|
| DeploymentEnvironment | frontend_url | Must be HTTPS | "Frontend URL must use HTTPS" |
| DeploymentEnvironment | backend_url | Must be HTTPS | "Backend URL must use HTTPS" |
| DeploymentEnvironment | database_url | Must start with postgresql:// | "Invalid Neon connection string" |
| EnvironmentVariable | name | Must be uppercase | "Variable name must be uppercase" |
| EnvironmentVariable | required=true | value_set must be true | "Required variable not configured" |
| MigrationRecord | records_before | Must equal records_after | "Record count mismatch detected" |
| MigrationRecord | integrity_verified | Must be true for completed | "Foreign key integrity check failed" |
| HealthCheck | response_time_ms | Must be <2000 for healthy | "Response time exceeds healthy threshold" |
| RollbackPoint | backup_path | File must exist | "Backup file not found" |
| RollbackPoint | valid_until | Must be future date | "Rollback point expired" |

---

## Usage Examples

### Example 1: Successful Deployment

```json
{
  "environment_id": "prod-2026-03-02",
  "frontend_url": "https://ai-native-book.vercel.app",
  "backend_url": "https://ai-native-book-backend.onrender.com",
  "database_url": "postgresql://user:***@ep-xxx.neon.tech/db",
  "status": "live",
  "deployed_at": "2026-03-02T14:30:00Z",
  "deployed_by": "ahmeddev",
  "git_commit": "1cc00fa",
  "version": "1.0.0"
}
```

### Example 2: Failed Migration with Rollback

```json
{
  "migration_id": "mig-2026-03-02-001",
  "direction": "forward",
  "source_type": "sqlite",
  "target_type": "neon",
  "status": "rolled_back",
  "tables_migrated": ["users", "conversations"],
  "records_before": {"users": 10, "conversations": 25},
  "records_after": {"users": 10, "conversations": 23},
  "integrity_verified": false,
  "error_message": "Record count mismatch: conversations (25 vs 23)",
  "backup_path": "/mnt/e/ai-native-book/ai_native_book.db.backup"
}
```

### Example 3: Degraded Health Check

```json
{
  "check_id": "hc-2026-03-02-001",
  "service": "backend",
  "status": "degraded",
  "response_time_ms": 3500,
  "last_check": "2026-03-02T14:35:00Z",
  "consecutive_failures": 0,
  "error_message": null,
  "endpoint": "https://ai-native-book-backend.onrender.com/api/health"
}
```

---

## Summary

This data model provides a structured approach to tracking deployment state, configuration, and health. Key features:

- **Safety**: MigrationRecord tracks data integrity with rollback capability
- **Monitoring**: HealthCheck provides real-time service status
- **Recovery**: RollbackPoint enables fast recovery from failures
- **Validation**: Comprehensive validation rules prevent misconfigurations
- **Auditability**: Timestamps and state transitions create audit trail
