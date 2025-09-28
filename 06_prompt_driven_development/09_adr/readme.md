# Module 09 – Architecture Decision Records (ADR)

**ADR** is a short, permanent note that captures a **significant technical decision**, the **context** in which you made it, the **options** you considered, the **choice** you made, and the **consequences** (trade-offs). Think of it as a timestamped “why we did it this way” so future you (and teammates) don’t have to reverse-engineer your thinking.

> **The strategic decision layer for SDD: How to capture and document major architectural choices that guide your feature development.**

## 🎯 **What ADR Actually Is**

**ADR is the strategic decision layer that works alongside SDD:**

- **ADR**: Captures major architectural decisions (frameworks, patterns, technology choices)
- **SDD**: Implements features using those architectural decisions

**ADR is NOT:**
- A replacement for SDD
- A detailed implementation process
- A way to document every small decision
- A competing methodology

## 🔄 **ADR vs SDD: Strategic vs Tactical**

### **ADR (Architecture Decision Records)**
**For:** Strategic architectural decisions
**Captures:** Framework choices, patterns, technology stack, security decisions
**Focus:** "Why did we choose this architecture?"

**Example:**
```markdown
# ADR-0001: Use FastAPI for API Development
- **Status:** Accepted
- **Context:** Need modern Python API with async support for AI workflows
- **Decision:** Choose FastAPI over Flask
- **Consequences:** Better type safety, auto-docs, async support
```

### **SDD (Spec-Driven Development)**
**For:** Feature development and implementation
**Captures:** Requirements, plans, tasks, implementation process
**Focus:** "How do we build features using our architecture?"

**Example:**
```markdown
# Spec: Build Chat Endpoint
- **Architecture Reference:** ADR-0001 (FastAPI)
- **Requirements:** Real-time chat with AI agents
- **Implementation:** Use FastAPI + WebSockets per ADR-0001
```

## 🤝 **How ADR and SDD Work Together**

**The Complete Workflow:**
```
ADR → Spec → Plan → Tasks → Implement → PHR
```

**1. ADR Phase**: Make strategic architectural decisions
**2. SDD Phase**: Implement features using those decisions
**3. Integration**: Reference ADRs in specs, link PHRs to ADRs

### **Why This Works**

**ADR provides the "why":**
- Why did we choose FastAPI?
- Why did we use microservices?
- Why did we pick this database?

**SDD provides the "how":**
- How do we build features with FastAPI?
- How do we implement microservice communication?
- How do we use this database effectively?

## 🎯 **When to Write an ADR**

**Write ADRs for strategic decisions:**
- Framework/SDK choices (FastAPI vs Flask, React vs Vue)
- Architecture patterns (microservices vs monolith)
- Technology stack decisions (PostgreSQL vs MongoDB)
- Security and compliance choices (OAuth vs JWT)
- Infrastructure decisions (AWS vs Azure, Docker vs Kubernetes)

**Don't write ADRs for:**
- Implementation details (use PHRs instead)
- Small feature decisions (use specs instead)
- Temporary choices (use comments instead)
- Code refactoring (use PHRs instead)

## 📝 **ADR Template**

**Keep it 1–2 pages and focused on strategic decisions:**

```markdown
# ADR-0001: Use FastAPI for API Development

- **Status:** Proposed | Accepted | Superseded | Deprecated
- **Date:** YYYY-MM-DD

## Context
What problem/constraints led to this decision?

## Options
- **A)** Option A (pros/cons)
- **B)** Option B (pros/cons)
- **C)** Option C (pros/cons)

## Decision
The chosen option and why

## Consequences
- **Positive:** Benefits and advantages
- **Negative:** Costs, trade-offs, and risks

## References
- Links to docs, issues, benchmarks, POCs
- Related ADRs: ADR-0002, ADR-0003
```

## 🎯 **Real-World Examples**

### **ADR-0001: Use FastAPI for API Development**
- **Status:** Accepted — 2025-01-15
- **Context:** Need modern Python API with async support for AI workflows
- **Options:**
  - **A)** FastAPI: Type safety, auto-docs, async support, modern
  - **B)** Flask: Simple, familiar, but limited async support
  - **C)** Django REST: Full-featured but heavyweight for our needs
- **Decision:** Choose **FastAPI** for modern async support and type safety
- **Consequences:**
  - ✅ Better performance, auto-documentation, type safety
  - ⚠️ Learning curve for team, more complex than Flask

### **ADR-0002: Use PostgreSQL for Primary Database**
- **Status:** Accepted — 2025-01-15
- **Context:** Need reliable, ACID-compliant database for financial data
- **Options:**
  - **A)** PostgreSQL: ACID, JSON support, mature ecosystem
  - **B)** MongoDB: Document-based, but eventual consistency
  - **C)** SQLite: Simple, but not suitable for production
- **Decision:** Choose **PostgreSQL** for ACID compliance and reliability
- **Consequences:**
  - ✅ ACID compliance, mature ecosystem, JSON support
  - ⚠️ More complex than NoSQL, requires schema management

## 🔗 **Integration with SDD**

### **Reference ADRs in Specs**
```markdown
# Spec: Build Chat Endpoint

## Architecture References
- ADR-0001: FastAPI framework choice
- ADR-0002: PostgreSQL database choice
- ADR-0003: WebSocket for real-time communication

## Requirements
- Real-time chat with AI agents
- Use FastAPI per ADR-0001
- Store chat history in PostgreSQL per ADR-0002
```

### **Link PHRs to ADRs**
```markdown
# PHR-0005: Implement Chat Endpoint

links:
  adr: docs/adr/0001-fastapi-choice.md
```

## 💡 **Best Practices**

**Do:**
- Keep ADRs **small and specific** (one decision per ADR)
- Use **numbered files** like `docs/adr/0001-*.md`
- Update **Status** when decisions change
- Reference ADR IDs in specs and PHRs
- Link related ADRs together

**Don't:**
- Write ADRs for implementation details
- Mix multiple decisions in one ADR
- Forget to update status when superseded
- Write ADRs for temporary choices

## 🚀 **Integration with SDD Workflow**

### **Complete Development Process**

**1. ADR Phase** - Strategic Decisions
```bash
# Create ADR for major architectural choices
/adr --title "Choose FastAPI for API Development"
```

**2. SDD Phase** - Feature Development
```bash
# Use ADRs to guide feature development
/spec --feature chat --adr 0001
/plan --feature chat
/tasks --feature chat
/edd --feature chat
/phr --feature chat
```

### **Cross-Reference Everything**

**ADRs inform Specs:**
```markdown
# Spec: Build Chat Endpoint
## Architecture References
- ADR-0001: FastAPI framework choice
- ADR-0002: PostgreSQL database choice
```

**PHRs link to ADRs:**
```markdown
# PHR-0005: Implement Chat Endpoint
links:
  adr: docs/adr/0001-fastapi-choice.md
  previous_prompt: 0004
  next_prompt: 0006
```

## 🎯 **Summary**

**ADR is the strategic decision layer that works alongside SDD:**

- **ADR**: Captures major architectural decisions (frameworks, patterns, technology choices)
- **SDD**: Implements features using those architectural decisions
- **Integration**: ADRs inform specs, PHRs reference ADRs

**Key principles:**
- Write ADRs for strategic decisions, not implementation details
- Reference ADRs in specs to guide feature development
- Link PHRs to ADRs for complete traceability
- Keep ADRs focused and specific (one decision per ADR)

**The complete workflow:**
```
ADR → Spec → Plan → Tasks → Implement → PHR
```

**Remember: ADR provides the "why" (strategic decisions), SDD provides the "how" (feature implementation). Both are essential for building reliable, well-architected applications.**


