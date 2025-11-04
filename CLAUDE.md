# Repository Guardrails for AI Self-Improvement

This document outlines the guardrails and best practices for AI-assisted development in the DSPy Self-Discover Framework repository.

## Core Principles

1. **Safety First**: All code changes must maintain or improve the security posture of the application
2. **Test Coverage**: New features should include appropriate tests
3. **Code Quality**: Follow Python best practices and maintain consistency with existing code style
4. **Documentation**: Update documentation when adding or modifying functionality

## Allowed Modifications

### ✅ Encouraged Changes

- **Bug Fixes**: Fix identified bugs in the codebase
- **Performance Improvements**: Optimize code execution and API response times
- **Test Coverage**: Add or improve unit tests and integration tests
- **Documentation**: Enhance README, add docstrings, improve code comments
- **Type Hints**: Add or improve Python type annotations
- **Error Handling**: Improve error messages and exception handling
- **Code Organization**: Refactor for better maintainability
- **Dependency Updates**: Update dependencies to secure, stable versions
- **API Enhancements**: Improve FastAPI endpoints with better validation and error handling
- **DSPy Integration**: Enhance DSPy framework integration and capabilities

### ⚠️ Requires Review

- **New Dependencies**: Must be justified and from trusted sources
- **API Changes**: Breaking changes to public API endpoints
- **Configuration Changes**: Modifications to core application settings
- **Security-Related Code**: Changes to authentication, authorization, or data validation
- **Code Execution Logic**: Changes to the code execution sandbox or safety mechanisms

### ❌ Prohibited Changes

- **Remove Safety Checks**: Never remove code execution safety mechanisms
- **Expose Secrets**: Never commit API keys, tokens, or credentials
- **Disable Security**: Never weaken security measures or input validation
- **Break Compatibility**: Avoid breaking changes without major version bump
- **Introduce Vulnerabilities**: No code that introduces known security issues

## Specific Repository Guidelines

### Code Execution Safety

- All code execution must remain properly sandboxed
- Input validation must be maintained for all user-provided code
- Never allow arbitrary file system access from executed code
- Maintain timeout mechanisms to prevent infinite loops

### DSPy and AI Integration

- Keep DSPy framework usage consistent with best practices
- Document any changes to AI model configurations
- Ensure Groq API integration remains secure
- Test AI-generated code outputs for safety

### API Development

- Follow RESTful conventions for new endpoints
- Maintain backward compatibility for existing endpoints
- Include proper request/response validation
- Document all endpoints with OpenAPI/Swagger annotations

### Testing Requirements

- Unit tests for new functions and methods
- Integration tests for new API endpoints
- Test code execution with various inputs
- Verify error handling and edge cases

## Code Review Checklist

Before submitting changes, ensure:

- [ ] Code follows existing style and conventions
- [ ] All tests pass successfully
- [ ] Documentation is updated
- [ ] No secrets or credentials are committed
- [ ] Security considerations are addressed
- [ ] Type hints are included where applicable
- [ ] Error handling is comprehensive
- [ ] Breaking changes are clearly documented

## AI Self-Improvement Process

1. **Identify**: Detect areas for improvement through static analysis, tests, or issues
2. **Propose**: Create detailed proposal for changes with rationale
3. **Implement**: Make changes following these guardrails
4. **Validate**: Run tests and verify functionality
5. **Document**: Update relevant documentation
6. **Review**: Create pull request for human review

## Contact

For questions about these guardrails or to propose changes, please open an issue in the repository.
