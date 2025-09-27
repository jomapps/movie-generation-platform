# Movie Generation Platform — System Architecture Diagram

The diagram below visualizes how the platform's core app, agents, processing services, data stores, media delivery, and observability components fit together across local/dev/prod environments.

```mermaid
flowchart LR
  %% Layout
  classDef group fill:#0b2239,stroke:#0b2239,color:#fff;
  classDef node fill:#e8f1fb,stroke:#3a6ea5,color:#102a43;
  classDef db fill:#fdebd2,stroke:#c28a3b,color:#513c06;
  classDef svc fill:#eaf7ef,stroke:#3e8e54,color:#163b24;
  classDef obs fill:#fff3cd,stroke:#b19700,color:#3d2e00;
  classDef ext fill:#f3e8fd,stroke:#6f42c1,color:#2d0a57;

  %% Client
  subgraph CLIENT[Client]
    U[User Browser]:::node
  end
  class CLIENT group;

  %% Core App
  subgraph CORE[Core App]
    AM[Auto‑Movie App\n(3010)\nPayloadCMS + UI]:::node
  end
  class CORE group;

  %% Orchestrator
  subgraph ORCH[Orchestration]
    LG[LangGraph Orchestrator\n(8003)]:::svc
  end
  class ORCH group;

  %% AI & Agents
  subgraph AI[AI & Domain Agents]
    MCP[MCP Brain Service\n(8002)\nJina v4 + Neo4j ctx]:::svc
    ST[Story MCP\n(8010)]:::svc
    CH[Character MCP\n(8011)]:::svc
    VI[Visual MCP\n(8012)]:::svc
    AU[Audio MCP\n(8013)]:::svc
    AS[Asset MCP\n(8014)]:::svc
    CEL[Celery Task Service\n(8001)\nGPU Workers]:::svc
  end
  class AI group;

  %% Data Stores
  subgraph DATA[Data Stores]
    NEO[Neo4j\n7474/7687]:::db
    RED[Redis\n6379]:::db
    MONGO[MongoDB\n27017]:::db
  end
  class DATA group;

  %% Media Delivery
  subgraph MEDIA[Media & Delivery]
    UP[Upload Proxy\n(8200)]:::svc
    CDN[Media CDN\n(Cloudflare R2)]:::ext
  end
  class MEDIA group;

  %% Observability
  subgraph OBS[Observability]
    PR[Prometheus\n(9090)]:::obs
    GR[Grafana\n(3001)]:::obs
    HL[System Health API\n(8100)]:::obs
  end
  class OBS group;

  %% Dev & Docs
  subgraph DEV[Dev & Docs]
    DOCS[API Docs\n(8300)]:::ext
    TEST[Test Env\n(3011)]:::ext
  end
  class DEV group;

  %% Edges — User to Core
  U --> AM

  %% Core <-> Orchestration & Agents
  AM <--> LG
  LG <--> MCP
  LG <--> ST
  LG <--> CH
  LG <--> VI
  LG <--> AU
  LG <--> AS

  %% Core -> Processing
  AM --> CEL

  %% MCP / Processing -> Data Stores
  MCP <--> NEO
  AM <--> MONGO
  CEL <--> RED

  %% Media pipeline
  AM --> UP
  CEL --> CDN
  UP --> CDN

  %% Observability & Health
  AM --> PR
  MCP --> PR
  CEL --> PR
  PR --> GR
  HL --> GR
  AM --> HL

  %% Docs & Test
  AM --> DOCS
  AM --> TEST

  %% Notes
  %% - Local/Dev/Prod domain mappings defined in Domain-configs.md
  %% - LangGraph coordinates cross-domain MCP agents
  %% - Celery uses Redis as broker/results; GPU workers execute heavy AI tasks
  %% - MCP Brain leverages Jina v4 embeddings and queries Neo4j for retrieval
```

References:
- See `docs/thoughts/Domain-configs.md` for ports, domains, and environment mappings.
- See `docs/thoughts/movie-platform-idea.md` for agent roles and workflow details.


