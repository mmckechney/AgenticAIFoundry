# stins.py Documentation Index

## Insurance Quote Assistant Multi-Agent System Documentation

This documentation covers the Insurance Quote Assistant (`stins.py`), a sophisticated multi-agent orchestration system built on Azure AI Foundry that demonstrates Connected Agent patterns for real-world insurance services.

### 📚 Documentation Structure

| Document | Purpose | Audience |
|----------|---------|----------|
| **[stins-README.md](./stins-README.md)** | Quick start guide and user documentation | Developers, Users |
| **[stins-insurance-assistant.md](./stins-insurance-assistant.md)** | Comprehensive technical documentation | Developers, Architects |
| **[stins-mermaid-diagrams.md](./stins-mermaid-diagrams.md)** | Visual architecture diagrams | Architects, Technical Teams |
| **[stins-technical-architecture.md](./stins-technical-architecture.md)** | Deep technical architecture details | Senior Developers, Architects |

### 🏗️ Architecture Overview

The Insurance Quote Assistant implements a **Connected Agent Pattern** with three specialized agents:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Insurance      │    │   Document      │    │     Email       │
│  Price Agent    │    │  Search Agent   │    │    Agent        │
│                 │    │                 │    │                 │
│ • Info Collection│    │ • Vector Search │    │ • Quote Format  │
│ • Quote Generation│   │ • Terms Extract │    │ • Email Delivery│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────▼─────────────────────────┐
         │         Main Orchestrator Agent                   │
         │      (InsuranceQuoteAssistant)                   │
         └─────────────────────────┬─────────────────────────┘
                                   │
         ┌─────────────────────────▼─────────────────────────┐
         │          Azure AI Foundry Platform               │
         │     (Connected Agent Tools & Services)           │
         └───────────────────────────────────────────────────┘
```

### 🚀 Quick Navigation

#### For Users
- **Getting Started**: [stins-README.md](./stins-README.md#quick-start)
- **Usage Guide**: [stins-insurance-assistant.md](./stins-insurance-assistant.md#usage-guide)
- **Troubleshooting**: [stins-README.md](./stins-README.md#troubleshooting)

#### For Developers
- **Technical Overview**: [stins-insurance-assistant.md](./stins-insurance-assistant.md#architecture)
- **API Integration**: [stins-insurance-assistant.md](./stins-insurance-assistant.md#api-integration)
- **Development Guide**: [stins-README.md](./stins-README.md#development)

#### For Architects
- **Connected Agent Pattern**: [stins-technical-architecture.md](./stins-technical-architecture.md#connected-agent-pattern)
- **Multi-Agent Orchestration**: [stins-technical-architecture.md](./stins-technical-architecture.md#multi-agent-orchestration-design)
- **Visual Architecture**: [stins-mermaid-diagrams.md](./stins-mermaid-diagrams.md)

### 🎯 Key Features Documented

1. **Multi-Agent Coordination** - How three specialized agents work together
2. **Azure AI Foundry Integration** - Connected Agent Tools implementation
3. **Vector Store Search** - Document search and retrieval capabilities
4. **Email Automation** - Automated quote delivery system
5. **Resource Management** - Dynamic agent lifecycle and cleanup
6. **Security & Compliance** - Authentication, authorization, and privacy
7. **Performance & Scalability** - Optimization strategies and scaling patterns

### 📊 Documentation Metrics

- **Total Documentation**: 75KB across 4 comprehensive documents
- **Mermaid Diagrams**: 7 detailed architectural diagrams
- **Code Examples**: 50+ implementation examples
- **Architecture Patterns**: Connected Agent, Event-Driven, Microservices
- **Integration Points**: Azure AI Foundry, Azure OpenAI, Vector Store, Email Services

### 🔗 Related Documentation

- **[Main Architecture Blueprint](./architecture-blueprint.md)** - Overall AgenticAIFoundry system design
- **[Mermaid Architecture Diagrams](./mermaid-architecture-diagram.md)** - Complete system visual architecture
- **[Implementation Guide](./implementation-guide.md)** - General implementation patterns
- **[Technical Diagrams](./technical-diagrams.md)** - System-wide technical diagrams

---

**📝 Note**: This documentation demonstrates Azure AI Foundry Connected Agent capabilities through a real-world insurance use case, providing both practical implementation guidance and architectural best practices for multi-agent systems.