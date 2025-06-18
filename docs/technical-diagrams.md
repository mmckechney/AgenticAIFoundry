# AgenticAIFoundry - Technical Component Diagrams

## Table of Contents
1. [Agent Architecture Diagrams](#agent-architecture-diagrams)
2. [Multi-Agent Team Framework](#multi-agent-team-framework)
3. [Evaluation Framework Diagrams](#evaluation-framework-diagrams)
4. [Security Testing Diagrams](#security-testing-diagrams)
5. [Integration Patterns](#integration-patterns)
6. [Data Processing Flows](#data-processing-flows)
7. [Error Handling & Recovery](#error-handling--recovery)

## Agent Architecture Diagrams

### Complete Agent Ecosystem Overview

```
                        ┌─────────────────────────────────────────────────────────┐
                        │                AgenticAIFoundry                         │
                        │                 Agent Ecosystem                         │
                        └─────────────────────┬───────────────────────────────────┘
                                              │
                        ┌─────────────────────▼───────────────────────────────────┐
                        │              Main Controller                            │
                        │                (agenticai.py)                          │
                        │                                                         │
                        │  ┌─────────────────────────────────────────────────────┐ │
                        │  │            Function Dispatcher                      │ │
                        │  │                                                     │ │
                        │  │  main() → selects agent based on configuration     │ │
                        │  └─────────────────────────────────────────────────────┘ │
                        └─────────────────────┬───────────────────────────────────┘
                                              │
        ┌─────────────────────────────────────┼─────────────────────────────────────┐
        │                                     │                                     │
        │                                     │                                     │
┌───────▼─────────┐              ┌─────────────▼──────────┐              ┌─────────▼─────────┐
│  Core Agents    │              │   Evaluation Agents    │              │  Security Agents  │
│                 │              │                        │              │                   │
├─────────────────┤              ├────────────────────────┤              ├───────────────────┤
│┌───────────────┐│              │┌──────────────────────┐│              │┌─────────────────┐│
││Code Interpreter││              ││ Agent Evaluator      ││              ││Red Team Agent   ││
││Agent           ││              ││                      ││              ││                 ││
│└───────────────┘│              │└──────────────────────┘│              │└─────────────────┘│
│┌───────────────┐│              │┌──────────────────────┐│              │┌─────────────────┐│
││Search Agent    ││              ││ Quality Evaluator    ││              ││Security Scanner ││
││               ││              ││                      ││              ││                 ││
│└───────────────┘│              │└──────────────────────┘│              │└─────────────────┘│
│┌───────────────┐│              │┌──────────────────────┐│              │┌─────────────────┐│
││Connected Agent ││              ││ Safety Evaluator     ││              ││Vulnerability    ││
││               ││              ││                      ││              ││Assessor         ││
│└───────────────┘│              │└──────────────────────┘│              │└─────────────────┘│
│┌───────────────┐│              │                        │              │                   │
││Reasoning Agent ││              │                        │              │                   │
││(O1 Series)     ││              │                        │              │                   │
│└───────────────┘│              │                        │              │                   │
└─────────────────┘              └────────────────────────┘              └───────────────────┘
        │                                     │                                     │
        └─────────────────────────────────────┼─────────────────────────────────────┘
                                              │
                        ┌─────────────────────▼───────────────────────────────────┐
                        │              Azure AI Foundry                           │
                        │               Core Platform                             │
                        │                                                         │
                        │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
                        │  │ Agent        │  │ Thread       │  │ Message      │  │
                        │  │ Management   │  │ Management   │  │ Processing   │  │
                        │  └──────────────┘  └──────────────┘  └──────────────┘  │
                        └─────────────────────────────────────────────────────────┘
```

### Individual Agent Internal Architecture

#### Code Interpreter Agent

```
                     ┌─────────────────────────────────────────┐
                     │       Code Interpreter Agent            │
                     └─────────────────┬───────────────────────┘
                                       │
                     ┌─────────────────▼───────────────────────┐
                     │            Agent Controller             │
                     │                                         │
                     │  • Receives user code requests         │
                     │  • Validates Python syntax             │
                     │  • Manages execution context           │
                     └─────────────────┬───────────────────────┘
                                       │
                     ┌─────────────────▼───────────────────────┐
                     │        Code Interpreter Tool            │
                     │                                         │
                     │  ┌─────────────────────────────────────┐ │
                     │  │        Execution Engine             │ │
                     │  │                                     │ │
                     │  │  • Secure Python environment       │ │
                     │  │  • Data analysis capabilities       │ │
                     │  │  │  • Pandas, NumPy, Matplotlib    │ │
                     │  │  │  • Statistical functions        │ │
                     │  │  │  • Visualization tools           │ │
                     │  │  • Code validation & sanitization  │ │
                     │  └─────────────────────────────────────┘ │
                     │                                         │
                     │  ┌─────────────────────────────────────┐ │
                     │  │         Output Handler              │ │
                     │  │                                     │ │
                     │  │  • Result formatting               │ │
                     │  │  • Error handling                  │ │
                     │  │  • File output management          │ │
                     │  └─────────────────────────────────────┘ │
                     └─────────────────┬───────────────────────┘
                                       │
                     ┌─────────────────▼───────────────────────┐
                     │           Response Formatter            │
                     │                                         │
                     │  • Code execution results              │
                     │  • Generated visualizations            │
                     │  • Error messages and debugging        │
                     └─────────────────────────────────────────┘
```

#### Connected Agent Architecture

```
                     ┌─────────────────────────────────────────┐
                     │         Connected Agent                  │
                     └─────────────────┬───────────────────────┘
                                       │
                     ┌─────────────────▼───────────────────────┐
                     │         Agent Orchestrator              │
                     │                                         │
                     │  • Multi-tool coordination             │
                     │  • Service integration management      │
                     │  • Workflow orchestration              │
                     └─────────────────┬───────────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        │                              │                              │
┌───────▼─────────┐         ┌─────────▼──────────┐         ┌─────────▼─────────┐
│   Stock Price   │         │     Email          │         │   Search          │
│     Agent       │         │    Service         │         │   Agent           │
│                 │         │                    │         │                   │
├─────────────────┤         ├────────────────────┤         ├───────────────────┤
│┌───────────────┐│         │┌──────────────────┐│         │┌─────────────────┐│
││External API   ││         ││Gmail SMTP        ││         ││Azure AI Search  ││
││Integration    ││         ││Integration       ││         ││Integration      ││
│└───────────────┘│         │└──────────────────┘│         │└─────────────────┘│
│┌───────────────┐│         │┌──────────────────┐│         │┌─────────────────┐│
││Data Fetching  ││         ││Email Composition ││         ││Knowledge        ││
││& Processing   ││         ││& Delivery        ││         ││Retrieval        ││
│└───────────────┘│         │└──────────────────┘│         │└─────────────────┘│
│┌───────────────┐│         │┌──────────────────┐│         │┌─────────────────┐│
││Response       ││         ││Multi-recipient   ││         ││Document         ││
││Formatting     ││         ││Support           ││         ││Processing       ││
│└───────────────┘│         │└──────────────────┘│         │└─────────────────┘│
└─────────────────┘         └────────────────────┘         └───────────────────┘
        │                              │                              │
        └──────────────────────────────┼──────────────────────────────┘
                                       │
                     ┌─────────────────▼───────────────────────┐
                     │         Response Aggregator             │
                     │                                         │
                     │  • Combines results from all tools     │
                     │  • Maintains context across services   │
                     │  • Generates comprehensive responses   │
                     └─────────────────────────────────────────┘
```

#### Reasoning Agent (O1 Series) Architecture

```
                     ┌─────────────────────────────────────────┐
                     │         Reasoning Agent (O1)            │
                     └─────────────────┬───────────────────────┘
                                       │
                     ┌─────────────────▼───────────────────────┐
                     │        Request Preprocessor             │
                     │                                         │
                     │  • Query analysis and categorization   │
                     │  • Complexity assessment               │
                     │  • Reasoning effort determination      │
                     └─────────────────┬───────────────────────┘
                                       │
                     ┌─────────────────▼───────────────────────┐
                     │      Azure OpenAI O1 Integration       │
                     │                                         │
                     │  ┌─────────────────────────────────────┐ │
                     │  │         Model Configuration         │ │
                     │  │                                     │ │
                     │  │  • Model: o4-mini / o3              │ │
                     │  │  • API Version: 2024-12-01-preview  │ │
                     │  │  • Reasoning Effort: high           │ │
                     │  │  • Max Tokens: 4000                 │ │
                     │  └─────────────────────────────────────┘ │
                     │                                         │
                     │  ┌─────────────────────────────────────┐ │
                     │  │        Reasoning Engine             │ │
                     │  │                                     │ │
                     │  │  • Complex problem decomposition   │ │
                     │  │  • Multi-step logical reasoning    │ │
                     │  │  • Chain-of-thought processing     │ │
                     │  │  • Professional output formatting  │ │
                     │  └─────────────────────────────────────┘ │
                     └─────────────────┬───────────────────────┘
                                       │
                     ┌─────────────────▼───────────────────────┐
                     │        Response Processor               │
                     │                                         │
                     │  • Professional formatting             │
                     │  • Enterprise-ready presentation       │
                     │  • Quality assurance validation        │
                     └─────────────────────────────────────────┘
```

#### Agent Management System Architecture

```
                     ┌─────────────────────────────────────────┐
                     │        Agent Management System          │
                     └─────────────────┬───────────────────────┘
                                       │
                     ┌─────────────────▼───────────────────────┐
                     │         Lifecycle Controller            │
                     │                                         │
                     │  • Agent creation & configuration      │
                     │  • Thread management & monitoring      │
                     │  • Resource allocation & cleanup       │
                     └─────────────────┬───────────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        │                              │                              │
┌───────▼─────────┐         ┌─────────▼──────────┐         ┌─────────▼─────────┐
│   Agent         │         │   Thread           │         │   Resource        │
│   Registry      │         │   Manager          │         │   Monitor         │
│                 │         │                    │         │                   │
├─────────────────┤         ├────────────────────┤         ├───────────────────┤
│┌───────────────┐│         │┌──────────────────┐│         │┌─────────────────┐│
││Active Agents  ││         ││Conversation      ││         ││Memory Usage     ││
││Tracking       ││         ││State Management  ││         ││Monitoring       ││
│└───────────────┘│         │└──────────────────┘│         │└─────────────────┘│
│┌───────────────┐│         │┌──────────────────┐│         │┌─────────────────┐│
││Configuration  ││         ││Session           ││         ││Performance      ││
││Management     ││         ││Persistence       ││         ││Analytics        ││
│└───────────────┘│         │└──────────────────┘│         │└─────────────────┘│
│┌───────────────┐│         │┌──────────────────┐│         │┌─────────────────┐│
││Cleanup        ││         ││Thread            ││         ││Alert            ││
││Automation     ││         ││Cleanup           ││         ││Management       ││
│└───────────────┘│         │└──────────────────┘│         │└─────────────────┘│
└─────────────────┘         └────────────────────┘         └───────────────────┘
```

## Multi-Agent Team Framework

### AgentTeam Architecture Overview

```
                           ┌─────────────────────────────────────────────────────┐
                           │                AgentTeam Framework                  │
                           │              (agent_team.py)                       │
                           └─────────────────────┬───────────────────────────────┘
                                                 │
                           ┌─────────────────────▼───────────────────────────────┐
                           │             Team Controller                         │
                           │                                                     │
                           │  ┌─────────────────────────────────────────────┐   │
                           │  │         Team Management                     │   │
                           │  │                                             │   │
                           │  │  • Team Assembly & Configuration           │   │
                           │  │  • Agent Registration & Lifecycle          │   │
                           │  │  • Task Queue & Distribution               │   │
                           │  │  • Coordination & Communication            │   │
                           │  └─────────────────────────────────────────────┘   │
                           └─────────────────────┬───────────────────────────────┘
                                                 │
                 ┌───────────────────────────────┼───────────────────────────────┐
                 │                               │                               │
                 │                               │                               │
       ┌─────────▼──────────┐          ┌────────▼────────┐          ┌─────────▼──────────┐
       │   Team Leader      │          │  Team Members  │          │  Task Management   │
       │     Agent          │          │    Framework   │          │     System        │
       │                    │          │                │          │                    │
       ├────────────────────┤          ├─────────────────┤          ├────────────────────┤
       │┌──────────────────┐│          │┌───────────────┐│          │┌──────────────────┐│
       ││Request Analysis  ││          ││TimeWeather    ││          ││Task Queue        ││
       ││& Orchestration   ││          ││Agent          ││          ││Management        ││
       │└──────────────────┘│          │└───────────────┘│          │└──────────────────┘│
       │┌──────────────────┐│          │┌───────────────┐│          │┌──────────────────┐│
       ││Task Creation     ││          ││SendEmail      ││          ││Agent Selection   ││
       ││& Delegation      ││          ││Agent          ││          ││& Assignment      ││
       │└──────────────────┘│          │└───────────────┘│          │└──────────────────┘│
       │┌──────────────────┐│          │┌───────────────┐│          │┌──────────────────┐│
       ││Workflow          ││          ││Temperature    ││          ││Result            ││
       ││Monitoring        ││          ││Agent          ││          ││Aggregation       ││
       │└──────────────────┘│          │└───────────────┘│          │└──────────────────┘│
       │┌──────────────────┐│          │┌───────────────┐│          │┌──────────────────┐│
       ││Quality           ││          ││Custom Agent   ││          ││Status            ││
       ││Assurance         ││          ││Support        ││          ││Tracking          ││
       │└──────────────────┘│          │└───────────────┘│          │└──────────────────┘│
       └────────────────────┘          └─────────────────┘          └────────────────────┘
```

### Task Delegation Flow Architecture

```
                           ┌─────────────────────────────────────────────────────┐
                           │              User Request                           │
                           │         "Complex Multi-Step Task"                  │
                           └─────────────────────┬───────────────────────────────┘
                                                 │
                           ┌─────────────────────▼───────────────────────────────┐
                           │              Team Leader Agent                     │
                           │                                                     │
                           │  ┌─────────────────────────────────────────────┐   │
                           │  │            Request Analysis                 │   │
                           │  │                                             │   │
                           │  │  1. Parse complex request                   │   │
                           │  │  2. Identify required capabilities          │   │
                           │  │  3. Plan task breakdown strategy            │   │
                           │  │  4. Determine execution sequence            │   │
                           │  └─────────────────────┬───────────────────────┘   │
                           └─────────────────────────┼───────────────────────────┘
                                                     │
                           ┌─────────────────────────▼───────────────────────────┐
                           │              Task Creation Engine                   │
                           │                                                     │
                           │  ┌─────────────────────────────────────────────┐   │
                           │  │         _create_task() Function             │   │
                           │  │                                             │   │
                           │  │  • Task description formulation            │   │
                           │  │  • Agent capability matching              │   │
                           │  │  • Priority and dependency analysis       │   │
                           │  │  • Queue placement strategy               │   │
                           │  └─────────────────────┬───────────────────────┘   │
                           └─────────────────────────┼───────────────────────────┘
                                                     │
                           ┌─────────────────────────▼───────────────────────────┐
                           │                Task Queue                           │
                           │              (FIFO Processing)                     │
                           │                                                     │
                           │  ┌─────────────────┐  ┌─────────────────┐  ┌────── │
                           │  │   Task 1:       │  │   Task 2:       │  │ Task  │
                           │  │ Get Time &      │  │ Convert Temp    │  │  3:   │
                           │  │ Weather         │  │ to Fahrenheit   │  │ Send  │
                           │  │                 │  │                 │  │ Email │
                           │  │ → TimeWeather   │  │ → Temperature   │  │ → Em  │
                           │  │   Agent         │  │   Agent         │  │   Age │
                           │  └─────────────────┘  └─────────────────┘  └────── │
                           └─────────────────────────┬───────────────────────────┘
                                                     │
        ┌────────────────────────────────────────────┼─────────────────────────────────────┐
        │                                            │                                     │
        │                                            │                                     │
┌───────▼──────────┐                   ┌─────────────▼──────────┐                ┌───────▼──────────┐
│  TimeWeather     │                   │  Temperature Agent     │                │  SendEmail       │
│  Agent           │                   │                        │                │  Agent           │
│                  │                   │                        │                │                  │
├──────────────────┤                   ├────────────────────────┤                ├──────────────────┤
│┌────────────────┐│                   │┌──────────────────────┐│                │┌────────────────┐│
││fetch_current   ││                   ││convert_temperature() ││                ││send_email_     ││
││_datetime()     ││                   ││                      ││                ││using_recipient ││
│└────────────────┘│                   │└──────────────────────┘│                ││_name()         ││
│┌────────────────┐│                   │┌──────────────────────┐│                │└────────────────┘│
││fetch_weather() ││                   ││Celsius → Fahrenheit  ││                │┌────────────────┐│
││                ││                   ││Conversion Logic      ││                ││Email Template  ││
│└────────────────┘│                   │└──────────────────────┘│                ││Processing      ││
│┌────────────────┐│                   │┌──────────────────────┐│                │└────────────────┘│
││OpenTelemetry   ││                   ││Result Formatting     ││                │┌────────────────┐│
││Tracing         ││                   ││                      ││                ││SMTP Integration││
│└────────────────┘│                   │└──────────────────────┘│                │└────────────────┘│
└──────────────────┘                   └────────────────────────┘                └──────────────────┘
        │                                            │                                     │
        │                                            │                                     │
        └─────────────────┬──────────────────────────┼─────────────────────────────────────┘
                          │                          │
                          ▼                          ▼
                    ┌─────────────────────────────────────────────────────┐
                    │              Result Aggregation                     │
                    │                                                     │
                    │  ┌─────────────────────────────────────────────┐   │
                    │  │         Team Leader Coordination           │   │
                    │  │                                             │   │
                    │  │  • Collect individual task results         │   │
                    │  │  • Validate task completion                │   │
                    │  │  • Check workflow completeness             │   │
                    │  │  • Generate comprehensive response         │   │
                    │  └─────────────────────┬───────────────────────┘   │
                    └─────────────────────────┼───────────────────────────┘
                                              │
                    ┌─────────────────────────▼───────────────────────────┐
                    │                Final Response                       │
                    │            to User Request                          │
                    └─────────────────────────────────────────────────────┘
```

### OpenTelemetry Tracing Architecture

```
                           ┌─────────────────────────────────────────────────────┐
                           │           AgentTraceConfigurator                   │
                           │          (agent_trace_configurator.py)             │
                           └─────────────────────┬───────────────────────────────┘
                                                 │
                           ┌─────────────────────▼───────────────────────────────┐
                           │           Tracing Configuration                     │
                           │               Selection                             │
                           │                                                     │
                           │  ┌─────────────────────────────────────────────┐   │
                           │  │          Configuration Menu                 │   │
                           │  │                                             │   │
                           │  │  1. Azure Monitor (Production)              │   │
                           │  │  2. Console Tracing (Development)          │   │
                           │  │  3. Console + Agent Instrumentation        │   │
                           │  │  4. No Tracing (Disabled)                  │   │
                           │  └─────────────────────┬───────────────────────┘   │
                           └─────────────────────────┼───────────────────────────┘
                                                     │
        ┌────────────────────────────────────────────┼─────────────────────────────────────┐
        │                                            │                                     │
        │                                            │                                     │
┌───────▼─────────┐                    ┌─────────────▼──────────┐                ┌───────▼──────────┐
│  Azure Monitor  │                    │   Console Tracing      │                │  Agent Traces    │
│  Integration    │                    │                        │                │                  │
│                 │                    │                        │                │                  │
├─────────────────┤                    ├────────────────────────┤                ├──────────────────┤
│┌───────────────┐│                    │┌──────────────────────┐│                │┌────────────────┐│
││Application    ││                    ││ConsoleSpanExporter   ││                ││AIAgents        ││
││Insights       ││                    ││                      ││                ││Instrumentor   ││
│└───────────────┘│                    │└──────────────────────┘│                │└────────────────┘│
│┌───────────────┐│                    │┌──────────────────────┐│                │┌────────────────┐│
││Cloud Telemetry││                    ││TracerProvider        ││                ││Span Processing ││
││Dashboard      ││                    ││Configuration         ││                ││Enhancement     ││
│└───────────────┘│                    │└──────────────────────┘│                │└────────────────┘│
│┌───────────────┐│                    │┌──────────────────────┐│                │┌────────────────┐│
││Production     ││                    ││SimpleSpanProcessor   ││                ││Custom Span     ││
││Analytics      ││                    ││                      ││                ││Creation        ││
│└───────────────┘│                    │└──────────────────────┘│                │└────────────────┘│
└─────────────────┘                    └────────────────────────┘                └──────────────────┘
        │                                            │                                     │
        └─────────────────┬──────────────────────────┼─────────────────────────────────────┘
                          │                          │
                          ▼                          ▼
                    ┌─────────────────────────────────────────────────────┐
                    │              Trace Collection                       │
                    │                                                     │
                    │  ┌─────────────────────────────────────────────┐   │
                    │  │         User Function Tracing              │   │
                    │  │                                             │   │
                    │  │  @tracer.start_as_current_span("func")     │   │
                    │  │  • fetch_current_datetime                  │   │
                    │  │  • fetch_weather                           │   │
                    │  │  • send_email_using_recipient_name         │   │
                    │  │  • convert_temperature                     │   │
                    │  └─────────────────────┬───────────────────────┘   │
                    └─────────────────────────┼───────────────────────────┘
                                              │
                    ┌─────────────────────────▼───────────────────────────┐
                    │            Comprehensive Observability             │
                    │          • Request-level tracing                   │
                    │          • Task-level span creation                │
                    │          • Agent interaction monitoring            │
                    │          • Performance metrics collection          │
                    └─────────────────────────────────────────────────────┘
```

## Evaluation Framework Diagrams

### Complete Evaluation Pipeline

```
                        ┌─────────────────────────────────────────┐
                        │           Evaluation Controller         │
                        └─────────────────┬───────────────────────┘
                                          │
                        ┌─────────────────▼───────────────────────┐
                        │         Input Data Processing           │
                        │                                         │
                        │  ┌─────────────────────────────────────┐ │
                        │  │       Data Loader                   │ │
                        │  │                                     │ │
                        │  │  • JSONL file parsing               │ │
                        │  │  • Data validation                  │ │
                        │  │  • Schema verification              │ │
                        │  └─────────────────────────────────────┘ │
                        └─────────────────┬───────────────────────┘
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        │                                 │                                 │
        │                                 │                                 │
┌───────▼─────────┐            ┌─────────▼──────────┐            ┌─────────▼─────────┐
│  Quality        │            │   Safety           │            │  Agentic          │
│  Evaluators     │            │   Evaluators       │            │  Evaluators       │
│                 │            │                    │            │                   │
├─────────────────┤            ├────────────────────┤            ├───────────────────┤
│┌───────────────┐│            │┌──────────────────┐│            │┌─────────────────┐│
││Relevance      ││            ││Content Safety    ││            ││Intent Resolution││
││Evaluator      ││            ││Evaluator         ││            ││Evaluator        ││
│└───────────────┘│            │└──────────────────┘│            │└─────────────────┘│
│┌───────────────┐│            │┌──────────────────┐│            │┌─────────────────┐│
││Coherence      ││            ││Violence          ││            ││Task Adherence   ││
││Evaluator      ││            ││Evaluator         ││            ││Evaluator        ││
│└───────────────┘│            │└──────────────────┘│            │└─────────────────┘│
│┌───────────────┐│            │┌──────────────────┐│            │┌─────────────────┐│
││Groundedness   ││            ││Hate/Unfairness   ││            ││Tool Call        ││
││Evaluator      ││            ││Evaluator         ││            ││Accuracy         ││
│└───────────────┘│            │└──────────────────┘│            │└─────────────────┘│
│┌───────────────┐│            │┌──────────────────┐│            │                   │
││Fluency        ││            ││Sexual Content    ││            │                   │
││Evaluator      ││            ││Evaluator         ││            │                   │
│└───────────────┘│            │└──────────────────┘│            │                   │
└─────────────────┘            └────────────────────┘            └───────────────────┘
        │                                 │                                 │
        └─────────────────────────────────┼─────────────────────────────────┘
                                          │
                        ┌─────────────────▼───────────────────────┐
                        │        Results Aggregator               │
                        │                                         │
                        │  ┌─────────────────────────────────────┐ │
                        │  │        Score Calculator             │ │
                        │  │                                     │ │
                        │  │  • Metric normalization            │ │
                        │  │  • Weighted scoring                │ │
                        │  │  • Statistical analysis            │ │
                        │  └─────────────────────────────────────┘ │
                        │                                         │
                        │  ┌─────────────────────────────────────┐ │
                        │  │         Report Generator            │ │
                        │  │                                     │ │
                        │  │  • JSON output formatting          │ │
                        │  │  • Comprehensive metrics           │ │
                        │  │  • Trend analysis                  │ │
                        │  └─────────────────────────────────────┘ │
                        └─────────────────────────────────────────┘
```

### Evaluation Data Flow

```
Input Data ──┐
             │
             ▼
    ┌─────────────────┐
    │   Data Parser   │
    │                 │
    │  • JSONL reader │
    │  • Validation   │
    │  • Schema check │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │  Data Splitter  │
    │                 │
    │  • Record       │
    │    extraction   │
    │  • Context      │
    │    separation   │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │ Evaluator Queue │
    │                 │
    │  • Parallel     │
    │    processing   │
    │  • Load         │
    │    balancing    │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │ Metric          │
    │ Calculation     │
    │                 │
    │  • Individual   │
    │    evaluations  │
    │  • Score        │
    │    aggregation  │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │ Results         │
    │ Formatting      │
    │                 │
    │  • JSON export  │
    │  • Report       │
    │    generation   │
    └─────────────────┘
```

## Security Testing Diagrams

### Red Team Testing Framework

```
                        ┌─────────────────────────────────────────┐
                        │       Red Team Controller               │
                        └─────────────────┬───────────────────────┘
                                          │
                        ┌─────────────────▼───────────────────────┐
                        │        Test Configuration               │
                        │                                         │
                        │  ┌─────────────────────────────────────┐ │
                        │  │       Risk Categories               │ │
                        │  │                                     │ │
                        │  │  • Violence Detection               │ │
                        │  │  • Hate/Unfairness                 │ │
                        │  │  • Sexual Content                  │ │
                        │  │  • Self-Harm                       │ │
                        │  └─────────────────────────────────────┘ │
                        │                                         │
                        │  ┌─────────────────────────────────────┐ │
                        │  │      Attack Strategies              │ │
                        │  │                                     │ │
                        │  │  • Easy Complexity                 │ │
                        │  │  • Moderate Complexity             │ │
                        │  │  • Character Manipulation          │ │
                        │  │  • Encoding Attacks               │ │
                        │  └─────────────────────────────────────┘ │
                        └─────────────────┬───────────────────────┘
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        │                                 │                                 │
        │                                 │                                 │
┌───────▼─────────┐            ┌─────────▼──────────┐            ┌─────────▼─────────┐
│   Target        │            │   Scan Executor    │            │   Results         │
│   Systems       │            │                    │            │   Processor       │
│                 │            │                    │            │                   │
├─────────────────┤            ├────────────────────┤            ├───────────────────┤
│┌───────────────┐│            │┌──────────────────┐│            │┌─────────────────┐│
││Callback       ││            ││Attack Generation ││            ││Vulnerability    ││
││Targets        ││            ││                  ││            ││Assessment       ││
│└───────────────┘│            │└──────────────────┘│            │└─────────────────┘│
│┌───────────────┐│            │┌──────────────────┐│            │┌─────────────────┐│
││Model          ││            ││Prompt Injection  ││            ││Risk Scoring     ││
││Configurations ││            ││Testing           ││            ││                 ││
│└───────────────┘│            │└──────────────────┘│            │└─────────────────┘│
│┌───────────────┐│            │┌──────────────────┐│            │┌─────────────────┐│
││Live           ││            ││Response Analysis ││            ││Compliance       ││
││Endpoints      ││            ││                  ││            ││Reporting        ││
│└───────────────┘│            │└──────────────────┘│            │└─────────────────┘│
└─────────────────┘            └────────────────────┘            └───────────────────┘
        │                                 │                                 │
        └─────────────────────────────────┼─────────────────────────────────┘
                                          │
                        ┌─────────────────▼───────────────────────┐
                        │         Output Generator                │
                        │                                         │
                        │  • JSON scan results                   │
                        │  • Security assessment reports         │
                        │  • Remediation recommendations         │
                        │  • Compliance documentation            │
                        └─────────────────────────────────────────┘
```

### Attack Strategy Implementation

```
                     ┌─────────────────────────────────────────┐
                     │        Attack Strategy Engine           │
                     └─────────────────┬───────────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        │                              │                              │
┌───────▼─────────┐         ┌─────────▼──────────┐         ┌─────────▼─────────┐
│   Character     │         │    Encoding        │         │   Complexity      │
│ Manipulation    │         │    Attacks         │         │   Strategies      │
│                 │         │                    │         │                   │
├─────────────────┤         ├────────────────────┤         ├───────────────────┤
│┌───────────────┐│         │┌──────────────────┐│         │┌─────────────────┐│
││Character      ││         ││ROT13 Encoding    ││         ││Easy Attack      ││
││Spaces         ││         ││                  ││         ││Patterns         ││
│└───────────────┘│         │└──────────────────┘│         │└─────────────────┘│
│┌───────────────┐│         │┌──────────────────┐│         │┌─────────────────┐│
││Character      ││         ││Base64 Encoding   ││         ││Moderate Attack  ││
││Swapping       ││         ││                  ││         ││Patterns         ││
│└───────────────┘│         │└──────────────────┘│         │└─────────────────┘│
│┌───────────────┐│         │┌──────────────────┐│         │┌─────────────────┐│
││Unicode        ││         ││Binary Encoding   ││         ││Advanced Attack  ││
││Confusables    ││         ││                  ││         ││Combinations     ││
│└───────────────┘│         │└──────────────────┘│         │└─────────────────┘│
│┌───────────────┐│         │┌──────────────────┐│         │                   │
││Leetspeak      ││         ││Morse Code        ││         │                   │
││Conversion     ││         ││                  ││         │                   │
│└───────────────┘│         │└──────────────────┘│         │                   │
└─────────────────┘         └────────────────────┘         └───────────────────┘
        │                              │                              │
        └──────────────────────────────┼──────────────────────────────┘
                                       │
                     ┌─────────────────▼───────────────────────┐
                     │         Attack Executor                 │
                     │                                         │
                     │  • Prompt generation and injection     │
                     │  • Response collection and analysis    │
                     │  • Success/failure determination       │
                     └─────────────────────────────────────────┘
```

## Integration Patterns

### Azure Services Integration

```
                     ┌─────────────────────────────────────────┐
                     │     AgenticAIFoundry Application       │
                     └─────────────────┬───────────────────────┘
                                       │
                     ┌─────────────────▼───────────────────────┐
                     │        Azure Identity Layer             │
                     │                                         │
                     │  • DefaultAzureCredential               │
                     │  • Service Principal Authentication     │
                     │  • Managed Identity Support            │
                     └─────────────────┬───────────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        │                              │                              │
┌───────▼─────────┐         ┌─────────▼──────────┐         ┌─────────▼─────────┐
│  Azure AI       │         │  Azure OpenAI      │         │  Azure AI         │
│  Foundry        │         │  Services          │         │  Search           │
│                 │         │                    │         │                   │
├─────────────────┤         ├────────────────────┤         ├───────────────────┤
│┌───────────────┐│         │┌──────────────────┐│         │┌─────────────────┐│
││Project        ││         ││GPT-4o Models     ││         ││Knowledge        ││
││Management     ││         ││                  ││         ││Retrieval        ││
│└───────────────┘│         │└──────────────────┘│         │└─────────────────┘│
│┌───────────────┐│         │┌──────────────────┐│         │┌─────────────────┐│
││Agent          ││         ││O1 Series Models  ││         ││Document         ││
││Orchestration  ││         ││                  ││         ││Indexing         ││
│└───────────────┘│         │└──────────────────┘│         │└─────────────────┘│
│┌───────────────┐│         │┌──────────────────┐│         │┌─────────────────┐│
││Evaluation     ││         ││Embeddings        ││         ││Semantic         ││
││Services       ││         ││                  ││         ││Search           ││
│└───────────────┘│         │└──────────────────┘│         │└─────────────────┘│
└─────────────────┘         └────────────────────┘         └───────────────────┘
        │                              │                              │
        └──────────────────────────────┼──────────────────────────────┘
                                       │
                     ┌─────────────────▼───────────────────────┐
                     │         Response Coordinator            │
                     │                                         │
                     │  • Service response aggregation        │
                     │  • Error handling and retries          │
                     │  • Performance optimization            │
                     └─────────────────────────────────────────┘
```

### External Services Integration

```
                     ┌─────────────────────────────────────────┐
                     │        Connected Agent Core             │
                     └─────────────────┬───────────────────────┘
                                       │
                     ┌─────────────────▼───────────────────────┐
                     │        Service Router                   │
                     │                                         │
                     │  • Service discovery                   │
                     │  • Load balancing                      │
                     │  • Circuit breaker pattern             │
                     └─────────────────┬───────────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        │                              │                              │
┌───────▼─────────┐         ┌─────────▼──────────┐         ┌─────────▼─────────┐
│   Email         │         │   Financial        │         │   Custom API      │
│   Services      │         │   Services         │         │   Integration     │
│                 │         │                    │         │                   │
├─────────────────┤         ├────────────────────┤         ├───────────────────┤
│┌───────────────┐│         │┌──────────────────┐│         │┌─────────────────┐│
││Gmail SMTP     ││         ││Stock Price APIs  ││         ││REST API         ││
││Integration    ││         ││                  ││         ││Client           ││
│└───────────────┘│         │└──────────────────┘│         │└─────────────────┘│
│┌───────────────┐│         │┌──────────────────┐│         │┌─────────────────┐│
││Multi-recipient││         ││Financial Data    ││         ││GraphQL          ││
││Support        ││         ││Processing        ││         ││Integration      ││
│└───────────────┘│         │└──────────────────┘│         │└─────────────────┘│
│┌───────────────┐│         │┌──────────────────┐│         │┌─────────────────┐│
││Authentication ││         ││Rate Limiting     ││         ││WebSocket        ││
││Management     ││         ││                  ││         ││Support          ││
│└───────────────┘│         │└──────────────────┘│         │└─────────────────┘│
└─────────────────┘         └────────────────────┘         └───────────────────┘
        │                              │                              │
        └──────────────────────────────┼──────────────────────────────┘
                                       │
                     ┌─────────────────▼───────────────────────┐
                     │        Response Aggregator              │
                     │                                         │
                     │  • Multi-service result combination    │
                     │  • Context preservation                │
                     │  • Error handling and fallbacks        │
                     └─────────────────────────────────────────┘
```

## Data Processing Flows

### Evaluation Data Processing Pipeline

```
Input JSONL ──┐
              │
              ▼
    ┌─────────────────┐
    │  File Validator │
    │                 │
    │  • Format check │
    │  • Schema valid │
    │  • Size limits  │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │   Data Parser   │
    │                 │
    │  • Line by line │
    │  • JSON decode  │
    │  • Field extract│
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │  Record Queue   │
    │                 │
    │  • Batch        │
    │    processing   │
    │  • Memory mgmt  │
    └─────────┬───────┘
              │
    ┌─────────▼───────┐
    │   Evaluator     │
    │   Dispatcher    │
    │                 │
    │  ┌─────────────┐│
    │  │ Quality     ││
    │  │ Evaluators  ││
    │  └─────────────┘│
    │  ┌─────────────┐│
    │  │ Safety      ││
    │  │ Evaluators  ││
    │  └─────────────┘│
    │  ┌─────────────┐│
    │  │ Agentic     ││
    │  │ Evaluators  ││
    │  └─────────────┘│
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │  Score Calc.    │
    │                 │
    │  • Normalize    │
    │  • Aggregate    │
    │  • Statistics   │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │  Results Export │
    │                 │
    │  • JSON format  │
    │  • Report gen   │
    │  • Metrics      │
    └─────────────────┘
```

### Red Team Scan Processing

```
Scan Config ──┐
              │
              ▼
    ┌─────────────────┐
    │ Target Analysis │
    │                 │
    │  • Type detect  │
    │  • Capability   │
    │    assessment   │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │ Attack Planning │
    │                 │
    │  • Strategy     │
    │    selection    │
    │  • Risk mapping │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │ Prompt          │
    │ Generation      │
    │                 │
    │  • Attack       │
    │    vectors      │
    │  • Encoding     │
    │    variations   │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │ Test Execution  │
    │                 │
    │  • Parallel     │
    │    testing      │
    │  • Response     │
    │    collection   │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │ Response        │
    │ Analysis        │
    │                 │
    │  • Safety       │
    │    violations   │
    │  • Risk scoring │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │ Report          │
    │ Generation      │
    │                 │
    │  • Findings     │
    │  • Recommend.   │
    │  • Compliance   │
    └─────────────────┘
```

## Error Handling & Recovery

### Global Error Handling Architecture

```
                     ┌─────────────────────────────────────────┐
                     │         Application Layer               │
                     └─────────────────┬───────────────────────┘
                                       │
                     ┌─────────────────▼───────────────────────┐
                     │        Error Detection Layer            │
                     │                                         │
                     │  ┌─────────────────────────────────────┐ │
                     │  │        Exception Handlers           │ │
                     │  │                                     │ │
                     │  │  • Azure service exceptions        │ │
                     │  │  • Network connectivity errors     │ │
                     │  │  • Authentication failures         │ │
                     │  │  • Rate limiting responses          │ │
                     │  │  • Data validation errors          │ │
                     │  └─────────────────────────────────────┘ │
                     └─────────────────┬───────────────────────┘
                                       │
                     ┌─────────────────▼───────────────────────┐
                     │        Error Classification             │
                     │                                         │
                     │  ┌─────────────────────────────────────┐ │
                     │  │         Error Types                 │ │
                     │  │                                     │ │
                     │  │  • Transient (retryable)           │ │
                     │  │  • Permanent (non-retryable)       │ │
                     │  │  • Authentication (credential)     │ │
                     │  │  • Configuration (setup)           │ │
                     │  └─────────────────────────────────────┘ │
                     └─────────────────┬───────────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        │                              │                              │
┌───────▼─────────┐         ┌─────────▼──────────┐         ┌─────────▼─────────┐
│   Retry         │         │   Fallback         │         │   Logging &       │
│   Logic         │         │   Mechanisms       │         │   Monitoring      │
│                 │         │                    │         │                   │
├─────────────────┤         ├────────────────────┤         ├───────────────────┤
│┌───────────────┐│         │┌──────────────────┐│         │┌─────────────────┐│
││Exponential    ││         ││Cached Responses  ││         ││Structured       ││
││Backoff        ││         ││                  ││         ││Logging          ││
│└───────────────┘│         │└──────────────────┘│         │└─────────────────┘│
│┌───────────────┐│         │┌──────────────────┐│         │┌─────────────────┐│
││Circuit        ││         ││Default Values    ││         ││Metrics          ││
││Breaker        ││         ││                  ││         ││Collection       ││
│└───────────────┘│         │└──────────────────┘│         │└─────────────────┘│
│┌───────────────┐│         │┌──────────────────┐│         │┌─────────────────┐│
││Rate Limiting  ││         ││Alternative       ││         ││Alert            ││
││               ││         ││Services          ││         ││Generation       ││
│└───────────────┘│         │└──────────────────┘│         │└─────────────────┘│
└─────────────────┘         └────────────────────┘         └───────────────────┘
        │                              │                              │
        └──────────────────────────────┼──────────────────────────────┘
                                       │
                     ┌─────────────────▼───────────────────────┐
                     │         Recovery Coordinator            │
                     │                                         │
                     │  • Error recovery orchestration        │
                     │  • State restoration                   │
                     │  • User notification                   │
                     └─────────────────────────────────────────┘
```

### Service-Specific Error Handling

```
                     ┌─────────────────────────────────────────┐
                     │         Service Error Router            │
                     └─────────────────┬───────────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        │                              │                              │
┌───────▼─────────┐         ┌─────────▼──────────┐         ┌─────────▼─────────┐
│  Azure AI       │         │  Azure OpenAI      │         │  External         │
│  Errors         │         │  Errors            │         │  Service Errors   │
│                 │         │                    │         │                   │
├─────────────────┤         ├────────────────────┤         ├───────────────────┤
│┌───────────────┐│         │┌──────────────────┐│         │┌─────────────────┐│
││401 Unauthorized││         ││429 Rate Limited  ││         ││SMTP Failures    ││
││→ Refresh token││         ││→ Exponential     ││         ││→ Fallback       ││
│└───────────────┘│         ││   backoff        ││         ││  providers      ││
│┌───────────────┐│         │└──────────────────┘│         │└─────────────────┘│
││403 Forbidden  ││         │┌──────────────────┐│         │┌─────────────────┐│
││→ Check perms  ││         ││500 Server Error  ││         ││API Timeouts     ││
│└───────────────┘│         ││→ Retry with      ││         ││→ Circuit        ││
│┌───────────────┐│         ││   backoff        ││         ││  breaker        ││
││404 Not Found  ││         │└──────────────────┘│         │└─────────────────┘│
││→ Resource     ││         │┌──────────────────┐│         │┌─────────────────┐│
││  validation   ││         ││Model Not Found   ││         ││Network Issues   ││
│└───────────────┘│         ││→ Fallback model  ││         ││→ Retry with     ││
└─────────────────┘         │└──────────────────┘│         ││  jitter         ││
                            └────────────────────┘         │└─────────────────┘│
                                                          └───────────────────┘
```

---

*These technical diagrams complement the main Architecture Blueprint document, providing detailed visual representations of the AgenticAIFoundry platform's internal structures and data flows.*