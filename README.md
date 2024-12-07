# SkyArcLog

A modular, cloud-agnostic logging framework with plugin support for various logging destinations and data transformations.

## Features

- Modular plugin architecture
- Dynamic loading of listeners and transformers
- Multiple logging destinations (Console, File, Azure, SQL)
- Flexible data transformations (JSON, SQL, Protobuf)
- Cloud-agnostic design
- Configurable through JSON

## Installation

```bash
# Minimal install (console + file logging)
pip install skyarclog

# Azure logging
pip install skyarclog[azure]

# SQL logging
pip install skyarclog[sql]

# Protobuf support
pip install skyarclog[protobuf]

# Full installation
pip install skyarclog[all]
```

## Usage

See the examples directory for detailed usage examples.
