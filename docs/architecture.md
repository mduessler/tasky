# Architecture

- [Data Model](#data-model)
  - [TmsUser](#tmsuser)
  - [Task](#task)
  - [TaskMembership](#taskmembership)
  - [TaskNote](#tasknote)
  - [TaskStatus](#taskstatus)
  - [EmailVerificationToken](#emailverificationtoken)
- [Registration Flow](#registration-flow)
  - [1. Register](#1-register)
  - [2. Activate](#2-activate)
- [Authentication](#authentication)
  - [How it works](#how-it-works)
  - [Token Expiry](#token-expiry)
  - [Why JWT](#why-jwt)
- [Permissions](#permissions)
  - [Task Resources — Role-Based Access Control (RBAC)](#task-resources--role-based-access-control-rbac)
    - [Permission Matrices](#permission-matrices)
      - [Tasks](#tasks)
      - [Task Membership](#task-membership)
      - [Task Note](#task-note)
  - [User Resources — Relationship-Based Access Control (ReBAC)](#user-resources--relationship-based-access-control-rebac)
    - [Permission Matrices](#permission-matrices-1)
      - [User](#user)
- [Superuser](#superuser)
  - [Relationships](#relationships)
- [API Versioning](#api-versioning)
- [Exception Handling](#exception-handling)

## Data Model

### TmsUser

Custom user model extending Django's `AbstractUser`. Authentication is done via
email instead of username. Users are inactive by default and must verify their
email address before they can log in.

| Field          | Type         | Constraints                      |
| -------------- | ------------ | -------------------------------- |
| `id`           | BigInt       | PK, auto-generated               |
| `email`        | EmailField   | unique, required — used as login |
| `username`     | CharField    | max 128 chars, not unique        |
| `first_name`   | CharField    | max 150 chars, optional          |
| `last_name`    | CharField    | max 150 chars, optional          |
| `password`     | CharField    | hashed                           |
| `is_active`    | BooleanField | default `False`                  |
| `is_staff`     | BooleanField | default `False`                  |
| `is_superuser` | BooleanField | default `False`                  |
| `date_joined`  | DateTime     | time when user joined.           |

______________________________________________________________________

### Task

| Field         | Type      | Constraints                             |
| ------------- | --------- | --------------------------------------- |
| `id`          | BigInt    | PK, auto-generated                      |
| `title`       | CharField | max 255 chars, cannot be whitespace     |
| `description` | TextField |                                         |
| `status`      | CharField | choices: `todo`, `doing`, `done`        |
| `created_at`  | DateTime  | auto-set on creation                    |
| `members`     | M2M       | via [`TaskMembership`](#taskmembership) |

______________________________________________________________________

### TaskMembership

Join table between `TmsUser` and `Task`. Stores the role a user holds within
a specific task.

| Field       | Type      | Constraints                                   |
| ----------- | --------- | --------------------------------------------- |
| `id`        | BigInt    | PK, auto-generated                            |
| `user`      | FK        | → [`TmsUser`](#tmsuser), CASCADE delete       |
| `task`      | FK        | → [`Task`](#task), CASCADE delete             |
| `role`      | CharField | choices: `owner`, `admin`, `member`, `viewer` |
| `joined_at` | DateTime  | auto-set on creation                          |

**Constraints:**

- A user can only be member of a task once (`unique_user_task`)
- Each task can only have one `OWNER` (`unique_task_owner`)

______________________________________________________________________

### TaskNote

| Field        | Type      | Constraints                                 |
| ------------ | --------- | ------------------------------------------- |
| `id`         | BigInt    | PK, auto-generated                          |
| `note`       | TextField | required                                    |
| `author`     | FK        | → [`TmsUser`](#tmsuser), SET_NULL on delete |
| `task`       | FK        | → [`Task`](#task), CASCADE delete           |
| `created_at` | DateTime  | auto-set on creation                        |

**Constraints:**

- Author must be a member of the task at the time of creation
- If the author is deleted, the note is preserved with `author = null`

______________________________________________________________________

### TaskStatus

`TaskStatus` is not a model but a `TextChoices` enum used as the `status` field
on [`Task`](#task).

| Value   | Label |
| ------- | ----- |
| `todo`  | To Do |
| `doing` | Doing |
| `done`  | Done  |

______________________________________________________________________

### EmailVerificationToken

Generated on user registration. Used to activate the account via email.
Tokens are immutable — they cannot be updated, only created or deleted.

| Field        | Type      | Constraints                         |
| ------------ | --------- | ----------------------------------- |
| `id`         | BigInt    | PK, auto-generated                  |
| `token`      | CharField | 6-digit numeric, auto-generated     |
| `user`       | FK        | → `TmsUser`, CASCADE delete, unique |
| `created_at` | DateTime  | auto-set on creation                |
| `expires_at` | DateTime  | 15 minutes after creation           |

**Constraints:**

- Each user can only have one active token at a time (`unique_user_token`)
- Token cannot be updated after creation — any save with existing `pk` raises `ValidationError`
- Token is only valid if the user is not yet active

## Registration Flow

User registration is a two-step process: the user registers and receives a
verification email, then activates the account via the token in that email.

### 1. Register

The client sends credentials to `POST /api/register/`. The server creates
an inactive user (`is_active = False`) and generates an `EmailVerificationToken`
— a 6-digit numeric code that expires after 15 minutes. The token is immutable:
it cannot be updated after creation, only deleted. Sending the verification email
is delegated to [**Celery**](https://github.com/celery/django-celery) and executed
asynchronously after the transaction commits.

### 2. Activate

The client sends the token to `POST /api/activate/`. The server verifies that
the token exists, belongs to the user, and has not expired. On success, the user
is set to active (`is_active = True`) and the token is deleted.

> A user cannot log in until the account is activated.

## Authentication

This API uses **JSON Web Tokens (JWT)** for stateless authentication. Therefore
the plugin **[djangorestframework-simplejwt](https://github.com/jazzband/djangorestframework-simplejwt)**
is used.

### How it works

1. The client sends credentials to `POST /api/auth/login/`. The body needs
   to include a JSON dict in which the keys `email` and `password` need to be
   set.
2. The server returns an **access token** (short-lived) and a **refresh token**
   (long-lived).
3. The client includes the access token in every subsequent request via the
   `Authorization: Bearer <access_token>` header.
4. Once the access token expires, the client sends the refresh token to
   `POST /api/auth/refresh/`. The body must include the refresh token. The server
   returns a new access token and a new refresh token — without re-entering credentials.
5. The user can logout by sending a request to `POST /api/auth/logout/`.
   The body must include the refresh token, which is then blacklisted and can no
   longer be used.

### Token Expiry

| Token         | Lifetime |
| ------------- | -------- |
| Access Token  | 15 min   |
| Refresh Token | 1 day    |

Refresh tokens are rotated on every use (with the previous token blacklisted),
giving a sliding-window session: daily-active users stay authenticated indefinitely,
inactive sessions expire after 24 hours.

### Why JWT

JWT is stateless — the server does not store sessions. All required information
is encoded inside the token itself and verified via signature on each request.
This makes the API horizontally scalable by default.

## Permissions

The system uses two distinct access control paradigms depending on the resource
type.

### Task Resources — Role-Based Access Control (RBAC)

Access to tasks, memberships, and notes is governed by the role a user holds within
a specific task, stored in the `TaskMembership` model. Roles are task-scoped —
a user may have different roles across different tasks.

> Task creation is not governed by the membership role system — any authenticated
> user may create a task and becomes its OWNER automatically.

| Role       | Description                                                |
| ---------- | ---------------------------------------------------------- |
| **OWNER**  | Full control over the task and all its resources.          |
| **ADMIN**  | Elevated access; can manage memberships and notes.         |
| **MEMBER** | Standard access; can create notes but not manage the task. |
| **VIEWER** | Read-only access across all task resources.                |

#### Permission Matrices

##### Tasks

| Role   | View | Create | Delete | Update Fields                    |
| ------ | ---- | ------ | ------ | -------------------------------- |
| OWNER  | ✔️   | ✔️     | ✔️     | `title`, `description`, `status` |
| ADMIN  | ✔️   | ✔️     | ❌     | `status`                         |
| MEMBER | ✔️   | ✔️     | ❌     | —                                |
| VIEWER | ✔️   | ✔️     | ❌     | —                                |

##### Task Membership

| Role   | View | Create | Delete | Update Fields |
| ------ | ---- | ------ | ------ | ------------- |
| OWNER  | ✔️   | ✔️     | ✔️     | `role`        |
| ADMIN  | ✔️   | ✔️     | ✔️     | `role`        |
| MEMBER | ✔️   | ❌     | ❌¹    | —             |
| VIEWER | ✔️   | ❌     | ❌¹    | —             |

> ¹ Every member can delete its own membership.

##### Task Note

| Role   | View | Create | Delete | Update Fields |
| ------ | ---- | ------ | ------ | ------------- |
| OWNER  | ✔️   | ✔️     | ✔️     | `note`        |
| ADMIN  | ✔️   | ✔️     | ✔️     | `note`        |
| MEMBER | ✔️   | ✔️     | ❌²    | — ³           |
| VIEWER | ✔️   | ❌     | ❌     | —             |

> ² An author can delete its own note in a time frame of 2 hours after creation.

> ³ An author can update its own note within of 2 hours after creation.

______________________________________________________________________

### User Resources — Relationship-Based Access Control (ReBAC)

Access to user resources is not role-based but resolved at request time based on
the relationship between the actor and the target user. No role is stored — the
system evaluates who is asking and in what context.

| Relationship     | Description                                              |
| ---------------- | -------------------------------------------------------- |
| **SELF**         | The actor is the target user.                            |
| **SUPERUSER**    | The actor has superuser privileges.                      |
| **GROUP_MEMBER** | The actor shares at least one task with the target user. |
| **OTHER**        | No relationship between actor and target user.           |

#### Permission Matrices

##### User

| Relationship | View | Create | Delete | Update Fields                                                     |
| ------------ | ---- | ------ | ------ | ----------------------------------------------------------------- |
| SELF         | ✔️   | ❌     | ✔️     | `email`, `username`, `first_name`, `last_name`, `password`        |
| SUPERUSER    | ✔️   | ❌     | ✔️     | `username`, `first_name`, `last_name`, `is_superuser`, `is_staff` |
| GROUP_MEMBER | ✔️   | ❌     | ❌     | —                                                                 |
| OTHER        | ❌   | ❌     | ❌     | —                                                                 |

## Superuser

A superuser bypasses all permission checks — both RBAC and ReBAC — across all
resources. The superuser role is not part of the permission matrices and is
resolved before any matrix lookup occurs.

| Resource       | Behavior                                                                                                   |
| -------------- | ---------------------------------------------------------------------------------------------------------- |
| Task           | Full access to all tasks regardless of membership                                                          |
| TaskMembership | Full access to all memberships                                                                             |
| TaskNote       | Full access to all notes                                                                                   |
| User           | Can view and delete any user, can update `username`, `first_name`, `last_name`, `is_superuser`, `is_staff` |

### Relationships

```shell
TmsUser ──< TaskMembership >── Task
TmsUser ──< TaskNote
Task    ──< TaskNote
TmsUser ──< EmailVerificationToken
```

## API Versioning

The API uses URL path versioning via Django REST Framework's `URLPathVersioning`.
The current version is `v1` and is the only supported version.

All business resource endpoints are prefixed with `/api/v1/`:

```shell
/api/v1/tasks/
/api/v1/users/
...
```

Authentication endpoints are not versioned as they are infrastructure and not
subject to API contract changes:

```shell
/api/auth/login/
/api/auth/refresh/
/api/auth/logout/
```

## Exception Handling

The API uses a custom exception handler that extends Django REST Framework's
default handler. It ensures consistent error responses across the entire API.

| Exception                             | Status Code | Response                               |
| ------------------------------------- | ----------- | -------------------------------------- |
| `Throttled`                           | `429`       | `{"detail": "Request was throttled."}` |
| `PermissionDenied`                    | `403`       | `{"detail": "<reason>"}`               |
| `ValidationError` (Django)            | `400`       | `{"detail": "<message>"}`              |
| `TmsUser.DoesNotExist`                | `404`       | `{"detail": "<message>"}`              |
| `Task.DoesNotExist`                   | `404`       | `{"detail": "<message>"}`              |
| `TaskMembership.DoesNotExist`         | `404`       | `{"detail": "<message>"}`              |
| `TaskNote.DoesNotExist`               | `404`       | `{"detail": "<message>"}`              |
| `EmailVerificationToken.DoesNotExist` | `404`       | `{"detail": "<message>"}`              |
| Unhandled                             | `500`       | `{"detail": "Internal server error"}`  |

All unhandled exceptions are logged at `ERROR` level. All handled exceptions
are logged at `DEBUG` or `WARNING` level depending on severity.
