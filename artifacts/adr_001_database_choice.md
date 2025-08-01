# Architectural Decision Record: Adoption of SQLite as Primary Embedded Database

- **Status:** Accepted
- **Date:** 2024-06-13
- **Decision ID:** ADR-001
- **Authors:** [Staff Engineer], [Technical Publications Expert]

## Context

Our application requires a reliable, lightweight, and easily embeddable database engine for use in desktop, mobile, and small-to-medium server environments. Key requirements include:
- Zero-configuration deployment (serverless operation)
- Public domain or permissive licensing for commercial use
- Broad language and framework compatibility
- Minimal operational overhead
- Strong documentation and community support

Alternatives considered included:
- **PostgreSQL:** Highly robust and scalable, but requires server infrastructure and is more complex to manage for embedded use cases.
- **MongoDB:** Offers schema flexibility and horizontal scalability, but licensing (SSPL) may restrict some commercial applications and it is less suited for purely embedded scenarios.
- **MySQL:** Mature and performant, but licensing (GPL or commercial) may impose constraints, and it requires server setup.
- **Microsoft SQL Server Express:** Free and reliable, but limited in database size (10GB) and optimized for Microsoft-centric ecosystems.

SQLite is widely adopted for embedded and lightweight scenarios, offering a zero-configuration, file-based approach with excellent documentation and a public domain license. The decision to select SQLite is driven by its fit for our target workload (moderate data, low-to-moderate concurrency), its ubiquity, and the absence of licensing barriers for commercial distribution.

## Decision

We will adopt **SQLite** as the primary embedded database for our application. SQLite will be used for all data storage and retrieval tasks that do not require distributed or high-concurrency database features.

## Consequences

### Positive Consequences

- **Zero-configuration:** Simplifies deployment with no server or setup required.
- **Lightweight:** Minimal binary size and resource requirements.
- **Public domain licensing:** No legal or commercial restrictions on usage or distribution.
- **Excellent documentation and community support:** Eases troubleshooting and onboarding.
- **Broad compatibility:** Integrates seamlessly with most programming languages and frameworks.
- **Portability:** Database is a single file, making backup, migration, and distribution trivial.

### Negative Consequences

- **Limited scalability:** Not suitable for very large datasets (>100GB) or high-concurrency, write-heavy environments.
- **No built-in horizontal scaling or replication:** Not a fit for distributed or cloud-native, multi-node architectures.
- **Single-writer limitation:** Write contention may occur under heavy concurrent write loads.

---

## References

- [Technical comparison of database frameworks (2024-06)](https://www.sqlite.org/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MongoDB Documentation](https://www.mongodb.com/docs/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Microsoft SQL Server Documentation](https://docs.microsoft.com/en-us/sql/sql-server/)