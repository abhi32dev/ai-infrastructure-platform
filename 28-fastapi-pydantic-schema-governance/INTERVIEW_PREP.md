# Interview Preparation Guide: Project 28

### 1. How to describe this project in an interview:
> "At Comcast, our FastAPI microservices handle millions of polymorphic webhook events from external vendor partners like Google SAS, Nokia, and Samsung. I implemented a strict schema governance architecture using **Pydantic v2 (leveraging the Rust core)** with discriminated unions (`Union[GoogleSAS, Nokia, Samsung]`) and custom validation rules (`@field_validator`, `@model_validator`). This eliminated unhandled runtime `KeyError` and `TypeError` exceptions across our entire ECS/Fargate fleet while cutting payload deserialization CPU overhead by over 65%."

### 2. Deep-Dive Q&A:
* **What is the advantage of Pydantic v2 over v1 in high-concurrency systems?**
  * Core validation was rewritten in Rust (`pydantic-core`), resulting in a 5x to 20x performance speedup.
  * Memory footprint per model instance is significantly lower due to optimized C-level structs.
  * Native support for JSON serialization without intermediate Python dictionary allocations (`model_dump_json()`).
