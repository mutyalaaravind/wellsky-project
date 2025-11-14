# Contributing guide

## VIKI architecture

This project follows the **NG Ops** conventions [as described here](https://wellsky.atlassian.net/wiki/spaces/PAYER/pages/153779553/NG+Ops+and+Development).

Before your start developing VIKI, please make sure to read the following documents first:
- [Hexagonal Architecture](https://wellsky.atlassian.net/wiki/spaces/PAYER/pages/153804576/Hexagonal+Architecture)
- [GitOps](https://wellsky.atlassian.net/wiki/spaces/PAYER/pages/153779661/GitOps)
- [Terraform Enterprise](https://wellsky.atlassian.net/wiki/spaces/PAYER/pages/153779568/Terraform+Enterprise)
- [Concurrency with AsyncIO](https://wellsky.atlassian.net/wiki/spaces/PAYER/pages/153822452/Concurrency+with+AsyncIO)

We also created a [sample production-ready application](https://github.com/mediwareinc/wscc-multivac) that demonstrates all of these patterns.

VIKI consists of several loosely coupled applications.

An application consists of a microfrontend which uses its own backend microservice (see [README](./README.md) for a list.)

## Developing VIKI

### Rule 1

> *Developer's environment is a first-class citizen.*

This rule means that all code should be fully operative when running in local environments.

For that purpose, we run emulators for proprietary dependencies, such as Firebase Tools which is a set of GCP emulators for Firestore DB, Pub/Sub, Cloud Functions, etc.

We use Docker as a primary runtime for running all our applications, so this process is made very easy.

### Rule 2

> *A quick start should be trivial for new engineers.*

Always include a `Makefile` with predefined rules for common operations, such as running tests (`test`) & linters (`lint`), fixing (`fix`) & generating code (`generate`), etc.

Every `Makefile` should have a `run` rule which starts your application in Docker. See [AutoScribe's Makefile](./autoscribe/Makefile) for example.

Additionally, always make sure to provide a `docker-compose.yml` for your application which defines backend/frontend/dependencies for your application. This will also make it easier for other engineers to write Terraform definitions to deploy your application.

TL;DR: `Makefile` and `docker-compose.yml` are a **MUST**.

### Rule 3

> *README is important, or "Explain-Like-I'm-Five" principle.*

Always include details & important unobvious notes about your application.

You don't need to write a huge README with all the technical details. Instead, simply imagine that you're explaining what your application does and why it is needed to a 5-year-old, and then write this down as a first paragraph.
Then, optionally add more details about how your application works.
