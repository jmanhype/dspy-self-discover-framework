
# FastAPI Application with DSPy Integration

This repository contains a FastAPI application designed to solve complex tasks through intelligent reasoning and automated code generation. Leveraging DSPy for deep learning and AI capabilities, alongside the Groq platform for enhanced computational power, this application offers a robust solution for processing natural language task descriptions, executing code, and dynamically generating code solutions.

## Features

- **Natural Language Task Solving**: Processes tasks described in natural language to generate actionable solutions.
- **Code Execution**: Executes arbitrary Python code dynamically through an API endpoint.
- **Automated Code Generation**: Generates executable code from structured reasoning about tasks, offering end-to-end automation from description to execution.
- **Integration with DSPy and Groq**: Utilizes the DSPy framework for AI and machine learning operations, powered by Groq's computational capabilities.

## Installation

Ensure you have Python 3.8+ installed. Clone this repository, then install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

The application provides several endpoints for interacting with its capabilities:

### Solving Tasks with Natural Language Descriptions

```bash
curl -X 'POST' \
  'http://0.0.0.0:8008/solve-task/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{ "description": "Explain photosynthesis", "task_type": "science" }'
```

### Executing Arbitrary Code

⚠️ **SECURITY WARNING**: The `/execute-code/` endpoint executes arbitrary Python code. This should **NEVER** be exposed on a public network or production environment without proper authentication, authorization, and sandboxing. Use only in trusted, isolated development environments.

```bash
curl -X 'POST' \
  'http://0.0.0.0:8008/execute-code/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d @payload.json
```

`payload.json` should contain your Python code in the format:

```json
{
  "code": "print('Hello, world!')"
}
```

### Generating and Executing Code from Task Descriptions

```bash
curl -X 'POST' \
  'http://0.0.0.0:8008/generate-and-execute/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{ "description": "Generate a Python function to add two numbers", "task_type": "programming" }'
```

### Running the Server

Start the FastAPI server using Uvicorn:

```bash
uvicorn self_discover_dspy_api:app --host 0.0.0.0 --port 8008 --reload
```

## Security Considerations

⚠️ **IMPORTANT**: This application includes endpoints that execute arbitrary code. Please be aware of the following security considerations:

1. **Code Execution Endpoints**: The `/execute-code/` and `/generate-and-execute/` endpoints execute Python code dynamically. These endpoints:
   - Should **NEVER** be exposed to the public internet
   - Must only be used in isolated, trusted development environments
   - Require proper authentication and authorization in any multi-user scenario
   - Should be disabled or protected in production deployments

2. **API Key Security**: Ensure the `GROQ_API_KEY` environment variable is properly secured and never committed to version control.

3. **Input Validation**: While the application validates request schemas, additional input sanitization may be needed for production use.

4. **Network Security**: Always run this application behind a firewall or VPN when needed.

## Contributing

Contributions are welcome! Feel free to submit pull requests or open issues to suggest improvements or add new features.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
