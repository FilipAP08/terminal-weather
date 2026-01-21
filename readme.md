# Terminal Weather

Terminal Weather is a lightweight, text-based weather client written in Python.
It is designed specifically for **slow, unreliable, or low-bandwidth connections**,
where graphical interfaces and heavy APIs are impractical.

The application consumes a JSON-based weather API and renders only plain text
output in the terminal, making it suitable for servers, rescue systems,
embedded devices, or remote SSH sessions.

## Key Features

- Minimal data usage – text-only output
- Fully configurable JSON-based output mapping
- Graceful operation on unstable network links
- No hardcoded weather fields – adapt to any API response
- Easy to extend or reduce displayed data without touching the code

## Philosophy

The project follows a simple rule:

> If a field exists in the API response, it can be added to the configuration.
> If it is not essential, it can be removed without breaking the program.

This makes the tool future-proof against API changes and flexible for
different use cases.

## Project Structure

```
.
├── main.py              # Application entry point
├── config.json          # Active configuration file
├── config_examples/     # Example configurations
├── backups/             # Automatically created backups
└── tz.txt               # Timezone mapping
```

## Configuration System

All displayed weather data is controlled via JSON configuration files.

The `config_examples` directory demonstrates how flexible the system is:

- **Extended configuration**
  - Example: `Gdansk_5days_ecmwf_sunbathing.json`
  - Shows how optional fields (e.g. `uv_index`) can be added when available in the API

- **Minimal configuration**
  - Example: `Berlin_3days_ecmwf_minimal.json`
  - Demonstrates removing non-essential fields without affecting correctness

As long as the field exists in the API response, it can be referenced in the config.
Missing or removed fields do not crash the application.

## Requirements

- Python 3.6+
- Internet access to the configured weather API

All required Python dependencies are installed automatically at runtime if missing.

## Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/FilipAP08/terminal-weather.git
   cd terminal-weather
   ```

2. Choose or create a configuration file:
   - Copy one of the files from `config_examples/`
   - Rename it to `config.json`

3. Run the application:
   ```bash
   python3 main.py
   ```

## Intended Use Cases

- SSH sessions over poor connections
- Emergency or fallback weather access
- Headless servers
- Embedded or low-power systems
- Users who prefer text over graphics

## License

This project is licensed under the MIT License.
See the LICENSE file for details.

---

Contributions and suggestions are welcome.
