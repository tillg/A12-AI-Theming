# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This is an AI theming experiment for A12 Project Template. The goal is to have an AI iteratively modify A12 theme files to match a target look and feel described by screenshots. The cycle involves:
1. Compile the code
2. Run the code
3. Make screenshots of the UI
4. Compare to target screenshots
5. Modify the A12 theme file
6. Repeat until the UI closely resembles the target

## Module Architecture

This is a Gradle multi-module project based on the A12 Project Template framework. The modules are organized as follows:

### Module Structure
- **buildSrc**: Custom Gradle build utilities, tasks, and properties management. Contains the build-time logic used by all other modules.
- **server**: Spring Boot backend application (split into `server:app` and `server:init` submodules)
  - `server:app`: Main server application with REST APIs, theming capabilities, and version management
  - `server:init`: Initialization and data migration application (locks database during execution)
- **client**: React-based frontend application using webpack and npm
- **import**: Module for importing and processing project templates
- **compose**: Docker Compose configuration for PostgreSQL and Keycloak containers

### Module Dependencies
- buildSrc → all modules (provides build utilities)
- server → client (server provides APIs and models for the client)
- import → server (uses server's core classes and models)
- compose → runtime infrastructure (provides database and authentication)

### Key Technologies
- **Backend**: Java 21, Spring Boot 3.5.5, PostgreSQL
- **Frontend**: React, Node.js 22, npm 10.7+, Webpack
- **Build**: Gradle 8.5+ (but < 9.0), Groovy/Kotlin DSL
- **Infrastructure**: Docker 20+, Docker Compose 2.20.3+
- **A12 Platform**: Uses A12 Base (29.1.0), Kernel (30.3.0), UAA (9.1.0), Data Services (38.1.0)

## Build Commands

### Full Project Build
```bash
gradle build
```

### Module-Specific Builds
```bash
gradle :server:app:build       # Build server application only
gradle :client:build           # Build client only
gradle :server:init:build      # Build init application
```

### Running Tests
```bash
gradle test                    # Run all tests
gradle :server:app:test        # Run server tests only
gradle :client:test            # Run client tests only
```

### Version Checking
```bash
gradle generateVersions        # Check tool versions and generate reports in build/reports/tools
```

## Running the Application

### Development Workflow

**Important**: The init application locks the PostgreSQL database. Always stop the server application before running init to prevent database inconsistencies.

1. **Start Keycloak (required for authentication)**:
   ```bash
   gradle keycloakComposeUp
   ```
   Note: This Keycloak setup is for development only and requires significant security enhancements for production.

2. **Run the server application**:
   ```bash
   gradle :server:app:bootrun --args='--spring.profiles.active=dev-env'
   ```
   Note: Server startup progress may not reach 100% in terminal output. Once it reaches ~80% without errors, the server is running properly.

3. **Run the client** (in a separate terminal):
   ```bash
   cd client
   npm start
   ```
   Keep webpack running while developing.

4. **Access the application**:
   - Frontend: http://localhost:8081
   - Server: http://localhost:8082
   - PostgreSQL: localhost:8083
   - Keycloak: http://localhost:8089

### Test Credentials (Development Only)
- Admin: `admin` / `A12PT-admintest`
- User1: `user1` / `A12PT-user1test`
- User2: `user2` / `A12PT-user2test`

### Running the Init Application

Stop the server first, then run:
```bash
gradle :server:init:bootrun --args='--spring.profiles.active=dev-env'
```

To initialize documents from `import/data/request` folder:
```bash
gradle :server:init:bootrun --args='--spring.profiles.active=dev-env,init-data'
```

## Configuration Management

### Version Catalogs (settings.gradle)
The project uses Gradle version catalogs for dependency management:
- `gradlePluginLibs`: Gradle plugins (Spring Boot, Docker, SonarQube, etc.)
- `a12Libs`: A12 platform libraries (base, kernel, uaa, dataservices)
- `libs`: Third-party libraries (logback, logstash)
- `testCatalogLibs`: Testing libraries

### Spring Profiles
- `dev-env`: Default development profile
- `init-data`: Additional profile for data initialization

### Tool Versions
Required tool versions are maintained in `tool-versions.json` (follows npm semver):
- JDK: 21
- Gradle: >=8.5.x <9
- Node: 22.x.x
- npm: >=10.7.x
- Docker: >=20.x
- Docker Compose: >=2.20.3

Tools marked with superscript "1" require Artifactory configuration.

## Theming Architecture

The project includes theme management capabilities:
- Client-side theme context: `client/src/app/themeContext.tsx`
- Theme chooser component: `client/src/components/ThemeChooser.tsx`
- Server-side theming APIs in the server:app module

For the AI theming experiment, focus on modifying theme files to match target screenshots. The theme changes should be applied through the A12 theming system.

## Important Development Notes

### Build System
- The buildSrc module contains custom Gradle tasks and utilities used throughout the build process
- Custom tasks include version checking, resource loading, property management, and Docker configuration
- Build properties and tool properties are managed through dedicated classes in buildSrc

### Server Architecture
- The server uses Spring Boot with PostgreSQL for persistence
- RESTful APIs are provided for client consumption
- The init application must be run separately for data initialization and should never run concurrently with the server app

### Client Architecture
- React-based SPA with webpack dev server
- Uses npm for package management
- Communicates with server via REST APIs

### Docker Compose
- Used only for infrastructure (Keycloak and PostgreSQL)
- Not used for running the application itself during development
- Configuration in `compose/docker-compose.yml`

## Common Pitfalls

1. **Don't run server:init and server:app concurrently** - This will cause database locking issues
2. **Server startup progress indicator** - Don't expect 100% completion; ~80% is normal
3. **Keycloak dependency** - The application requires Keycloak to be running for authentication
4. **Artifactory access** - Gradle, npm, and Docker need proper Artifactory configuration (see external documentation)
5. **JDK version** - This project requires JDK 21 specifically

## Repository Structure

```
.
├── buildSrc/          # Build utilities and custom tasks
├── client/            # React frontend application
├── compose/           # Docker Compose for infrastructure
├── import/            # Template import module
├── server/
│   ├── app/          # Main server application
│   └── init/         # Initialization application
├── quality/          # Code quality configuration
├── resources/        # Project resources
├── build.gradle      # Root build configuration
├── settings.gradle   # Multi-module configuration
└── tool-versions.json # Required tool versions
```

## External Documentation

Comprehensive documentation is available at https://docs.geta12.com/docs/ covering:
- Environment and tools setup
- Artifactory configuration
- Build variants and profiles
- Security considerations
- Deployment pipelines
- Enhancement possibilities
