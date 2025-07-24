# 07: MCP Resources - Current State and Future

**MCP Resources**—a powerful feature that allows MCP servers to expose data and content that can be read by clients and used as context for LLM interactions. However, this is currently a **work-in-progress** feature in the OpenAI Agents SDK.

---

## Current State: Resources Support is Limited

### **What's Available Now**
- **MCP Resources specification** exists and is well-defined
- **Individual MCP servers** can implement resources
- **Manual resource handling** is possible with custom code

### **What's Missing**
- **Native integration** in the OpenAI Agents SDK
- **Automatic resource processing** in agent workflows
- **Built-in resource link parsing** from tool outputs

---

## [The GitHub PR: #1042](https://github.com/openai/openai-agents-python/pull/1042)

According to the [GitHub PR #1042](https://github.com/openai/openai-agents-python/pull/1042), there's an ongoing effort to add MCP Resources support to the SDK:

### **What the PR Adds**
- Three abstract methods to the base `MCPServer` class:
  - `list_resources()`
  - `list_resource_templates()`
  - `read_resource()`
- Implementation in `_MCPServerWithClientSession` (parent of all transport classes)
- Example MCP resources server with working demonstration
- Updated documentation with usage examples

### **What the PR Does NOT Include**
- `subscribe_resource` and `unsubscribe_resource` methods
- **Automatic integration** into agent workflows
- **Resource link parsing** from tool outputs

---

## Key Discussion Points from the PR

### **The Big Question: "Does this actually do anything?"**
As noted by [@artificial-aidan](https://github.com/openai/openai-agents-python/pull/1042#issuecomment-1984561234):
> "Does this actually do anything to integrate MCP resources into the agent flow? Or is it up to the implementer to retrieve resources. Seems not very useful? Tool calls can return links to resources, it seems like it would be more useful to parse tool outputs and use the resource link to return a resource to the LLM."

### **OpenAI's Response**
[@seratch](https://github.com/openai/openai-agents-python/pull/1042#issuecomment-1984561234) clarified:
> "At the moment, this SDK's agent mechanism does not have plans to directly utilize resources. The proposed resource support here is simply to add methods for using resources within the same code base, but it does not mean your agents can leverage them without additional code from your side."

---

## What This Means for You

### **Right Now (Current State)**
- You can **manually** work with MCP resources
- You need to **write custom code** to handle resource links
- Resources are **not automatically** integrated into agent workflows

### **Future (If PR #1042 is Merged)**
- You'll have **helper methods** to work with resources
- You'll still need **custom logic** to integrate resources into agent flows
- The SDK will provide **infrastructure** but not **automatic integration**

---

## Learning Takeaways

1. **MCP Resources** are a powerful concept for exposing data
2. **Current limitations** in the OpenAI Agents SDK
3. **Future possibilities** with ongoing development
4. **Manual implementation** requirements for now