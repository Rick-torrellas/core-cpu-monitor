# cc.StatusQ-cpu

> Efficient monitoring and management of CPU status.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Version](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Rick-torrellas/cc.StatusQ-cpu/badges/version.json)
[![CI CD](https://github.com/Rick-torrellas/cc.StatusQ-cpu/actions/workflows/main.yaml/badge.svg)](https://github.com/Rick-torrellas/cc.StatusQ-cpu/actions/workflows/main.yaml)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Download](https://img.shields.io/github/v/release/Rick-torrellas/cc.StatusQ-cpu?label=Download&color=orange)](https://github.com/Rick-torrellas/cc.StatusQ-cpu/releases)
[![docs](https://img.shields.io/badge/docs-read_now-blue?style=flat-square)](https://rick-torrellas.github.io/cc-book-kit/)
[![Ask DeepWiki](https://img.shields.io/badge/DeepWiki-Documentation-blue?logo=gitbook&logoColor=white)](https://deepwiki.com/Rick-torrellas/cc.StatusQ-cpu)

💊⚛️

---

## Installation

```bash
pip install cc.statusq-cpu
```

---

## Usage

```python
from cc_statusq_cpu.core import StatusqCPU, CPUEventBus
from cc_statusq_cpu.capsule import PsutilCPUProvider, ConsoleSubscriber

# 1. Initialize the Event Bus (The Communication Channel)
event_bus = CPUEventBus()

    # 2. Initialize the Infrastructure Provider (The Data Source)
provider = PsutilCPUProvider()

    # 3. Setup Subscribers (The Consumers)
    # The ConsoleSubscriber implements the CPUEventSubscriber contract
console_logger = ConsoleSubscriber()
console_logger.subscribe_to(event_bus)

    # 4. Initialize the Domain Controller
cpu_monitor = StatusqCPU(provider=provider, event_bus=event_bus)

    # 5. Run Monitoring
print("--- Single Check ---")
cpu_monitor.run_single_check()

print("\n--- Continuous Monitoring (3 iterations) ---")
cpu_monitor.run_continuous_monitoring(interval=1.0, iterations=3)

```

---

## Architecture Overview

* core: : Contains the business logic (StatusqCPU), Event definitions, and Interfaces (CPUProvider). It has zero dependencies on external libraries.

* capsule: Contains concrete implementations like PsutilCPUProvider (using psutil) and ConsoleSubscriber (using print).