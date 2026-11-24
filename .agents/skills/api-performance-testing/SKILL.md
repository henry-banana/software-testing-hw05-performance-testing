---
name: api-performance-testing
description: Design and validate repeatable HTTP API Load, Stress, Spike, or endurance tests on an authorized environment. Use when selecting a shared workflow, preparing fixtures, running JMeter, or auditing raw performance metrics and regressions.
---

# API Performance Testing

1. Identify the authorized environment, exact SUT version, workflow, test accounts, side effects, and runner capacity. Use an isolated test database. Agree on an endpoint contract before choosing the load.
2. Compose one end to end workflow with response assertions and correlated identifiers. Keep a fixture identity exclusive to each active virtual user when carts, sessions, locks, or writes share state. Check generated CSV values against the actual fixture. Seed and warm up outside the measured interval.
3. Set a Load plateau, increasing Stress stages, a short Spike with recovery, and a sustained endurance point informed by the Stress result. State wait times, ramp, sample windows, stop limits, and thresholds before measurement. Verify the client runtime, plugins, and actual thread behavior with a smoke run.
4. Run one scenario at a time through the ordinary CLI and preserve the original samples, report, resource timestamps, commit, profile, and executor identity. Correlate p95 and errors with active users, virtual-user headroom, and process CPU and memory. Reset only the intended fixture between runs.
5. Compute latency percentiles from elapsed response times in explicitly bounded windows. Measure HTTP requests and completed workflows separately. Check sampler counts and assertion failures against the dashboard. Distinguish a confirmed limit from the highest stable point tested, and a hypothesis about the bottleneck from a controlled comparison.
6. When reviewing AI analysis, retain the original claim and the source sample or window that supports or corrects it. Verify proposed optimizations against the owning code and measure before claiming a benefit.

For a concrete instance with CSV identities, API assertions, and JTL cross-checks, read [the order workflow example](references/order-workflow.md).
