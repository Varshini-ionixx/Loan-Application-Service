# ADR 0001: JWT vs. Server-Side Session Authentication

- **Status:** Accepted
- **Date:** 2026-10-16

## Context

The Loan Application Service is a FastAPI REST API with protected endpoints for customers and officers. It needs to authenticate users and enforce role-based access control. JWT authentication and server-side sessions are both viable approaches.

## Decision

Use JWT bearer tokens for API authentication. After a successful login, the API issues an access token that the client sends in the `Authorization: Bearer` header on subsequent requests. Protected endpoints validate the token and identify the current user.

## Alternatives considered

- **Server-side sessions:** The server stores session state and typically identifies the session through a cookie. This supports centralized session invalidation but requires session storage and management.
- **JWT bearer tokens:** The token carries signed claims that the API validates. This suits stateless API authentication and avoids requiring a server-side session record for every authenticated request.

## Consequences

JWT authentication keeps the API integration straightforward for clients such as Postman and other API consumers. It can also simplify scaling because each request can be authenticated without retrieving a server-side session.

However, a signed JWT is not automatically encrypted, and a token generally remains usable until it expires unless additional revocation mechanisms are implemented. The application must protect its signing secret, use appropriate token expiration, and validate tokens on protected requests. Clients must also store tokens securely.

Server-side sessions would make centralized invalidation easier but would introduce session storage and lifecycle management.

## Follow-up

Review token expiration, secret management, and token revocation requirements as the service evolves.