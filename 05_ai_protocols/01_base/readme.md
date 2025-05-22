# Foundational Protocols for Agentic and Multi-Modal AI Systems

This module provides a future-proofed, pedagogically ordered learning path through the foundational protocols that underpin modern, scalable, and multi-modal agentic AI systems. Each protocol is presented in a sequence that builds conceptual understanding from the network layer up to advanced real-time and multi-modal communication, serialization, and emerging research.

## Prerequisites

- Introduction to FastAPI. Watch this [video for quick recap](https://www.youtube.com/watch?v=hpE9NlZ1X0A&list=PL0vKVrkG4hWrlP5uLUAr47uvSq1D7NCmc&index=2) if you are unfamiliar with FastAPI.
- Modern Python ([including Asyncio](https://docs.python.org/3/library/asyncio.html))

## Why This Structure?

- **Agentic AI systems** require robust, interoperable, and efficient communication at every layer.
- **Multi-modal agents** (processing text, audio, video, sensor data, etc.) need protocols that support diverse, high-throughput, and low-latency data flows.
- **Future-proofing**: The field is evolving rapidly. This structure is designed to be extensible, with a dedicated section for emerging and experimental protocols.

## Learning Path Overview

| Order | Directory              | Description/Focus                           |
| ----- | ---------------------- | ------------------------------------------- |
| 01    | 01_IP                  | Network addressing/routing                  |
| 02    | 02_TCP                 | Reliable transport                          |
| 03    | 03_UDP                 | Fast, connectionless transport              |
| 04    | 04_QUIC                | Modern UDP-based transport (HTTP/3)         |
| 05    | 05_HTTP_Theory         | HTTP/1.1 essentials                         |
| 06    | 06_HTTP2               | Multiplexing, server push                   |
| 07    | 07_HTTP3               | HTTP over QUIC                              |
| 08    | 08_REST                | Resource-oriented APIs                      |
| 09    | 10_Streamable_HTTP     | Streaming over HTTP                         |
| 10    | 09_SSE                 | Server-sent events                          |
| 11    | 11_JSON_RPC            | JSON-based RPC                              |
| 12    | 12_gRPC                | High-performance RPC (HTTP/2, Protobuf)     |
| 13    | 13_WebRTC              | Real-time, P2P, multi-modal                 |
| 14    | 14_WebTransport        | Modern real-time transport (HTTP/3, QUIC)   |
| 15    | 15_WebCodecs           | Low-level media encoding/decoding           |
| 16    | 16_WebSockets          | Bidirectional, persistent connections       |
| 17    | 17_MQTT                | Lightweight pub/sub                         |
| 19    | 19_Future_AI_Protocols | Research, proposals, and emerging standards |

## How to Use This Directory

- **Start at the top** and work your way down for a solid foundation in network and application protocols.
- **19_Future_AI_Protocols** is a living area for tracking and contributing to the next generation of AI communication standards.

## Protocol Summaries

- **IP, TCP, UDP, QUIC**: The backbone of all networked communication, from addressing to reliable and fast data transfer.
- **HTTP (1.1/2/3), REST**: The web's lingua franca, powering APIs and agent-to-agent/service communication.
- **Streamable_HTTP, SSE**: Techniques for real-time and event-driven data flows over HTTP.
- **JSON_RPC, gRPC**: The two most important RPC paradigms for agent-to-agent and agent-to-service calls, with gRPC leveraging Protobuf for efficiency.
- **WebRTC, WebTransport, WebCodecs**: Advanced protocols for real-time, peer-to-peer, and multi-modal streaming, essential for next-gen agentic and immersive systems.
- **WebSockets, MQTT**: Event-driven, persistent, and lightweight communication for distributed and IoT-style agentic systems.
- **20_Future_AI_Protocols**: A space for research, proposals, and tracking the evolution of AI-native communication standards.

---

**This structure is designed to support both current best practices and the ongoing evolution of agentic, multi-modal, and AI-first systems.**

For each protocol, see its directory for a detailed README covering:

- Core concepts and protocol summary
- Key characteristics, strengths, and weaknesses
- Hands on in Python
- Typical and future-facing use cases (AI, multi-modal, agentic, MCP/A2A, etc.)
- How it fits into the overall stack and interacts with other protocols
- Open research questions and future directions
