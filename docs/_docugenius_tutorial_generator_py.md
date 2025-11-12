# .docugenius/tutorial_generator.py

## Overview

This file contains 90 documented elements.

## Classes

### AgentResponse

Response from an AI agent

**Decorators**: dataclass

### AIAgent

Base class for specialized AI agents

#### Methods

##### __init__(self, name, role, ai_client, ai_provider, model, max_tokens)

##### generate(self, prompt, context)

Generate content using AI

### InterfaceExplainerAgent

Agent specialized in explaining UI interfaces step-by-step

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model, target_language)

##### explain_interface(self, interface_description, features, readme_content, project_overview)

Generate detailed interface explanation

### QuickStartAgent

Agent specialized in creating quick start guides

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model, target_language)

##### create_quick_start(self, project_info)

Generate quick start guide

### APIDocumentationAgent

Agent specialized in API documentation

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model, target_language)

##### document_api(self, classes, functions)

Generate comprehensive API documentation

### TutorialSeriesAgent

Agent specialized in creating tutorial series

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model, target_language)

##### create_tutorial(self, level, topic, project_context)

Generate a tutorial for specific level

### TroubleshootingAgent

Agent specialized in troubleshooting guides

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model, target_language)

##### create_troubleshooting_guide(self, common_issues)

Generate troubleshooting guide

### ExampleGeneratorAgent

Agent specialized in generating practical examples

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model, target_language)

##### generate_examples(self, use_cases, code_samples)

Generate practical examples

### LanguageValidatorAgent

Agent specialized in validating documentation language

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model)

##### validate_language(self, content, target_language)

Validate that content is in the target language

##### parse_validation_result(self, response)

Parse the validation response into structured data

### TutorialGenerator

Main tutorial generator using multi-agent system

#### Methods

##### __init__(self, project_path, elements, config, ai_client)

##### generate_complete_documentation(self, mode)

Generate tutorial documentation using AI agents

Args:
    mode: 'tutorials_only', 'api_only', or 'both' (default)

### AgentResponse

Response from an AI agent

**Decorators**: dataclass

### AIAgent

Base class for specialized AI agents

#### Methods

##### __init__(self, name, role, ai_client, ai_provider, model, max_tokens)

##### generate(self, prompt, context)

Generate content using AI

### InterfaceExplainerAgent

Agent specialized in explaining UI interfaces step-by-step

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model, target_language)

##### explain_interface(self, interface_description, features, readme_content, project_overview)

Generate detailed interface explanation

### QuickStartAgent

Agent specialized in creating quick start guides

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model, target_language)

##### create_quick_start(self, project_info)

Generate quick start guide

### APIDocumentationAgent

Agent specialized in API documentation

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model, target_language)

##### document_api(self, classes, functions)

Generate comprehensive API documentation

### TutorialSeriesAgent

Agent specialized in creating tutorial series

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model, target_language)

##### create_tutorial(self, level, topic, project_context)

Generate a tutorial for specific level

### TroubleshootingAgent

Agent specialized in troubleshooting guides

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model, target_language)

##### create_troubleshooting_guide(self, common_issues)

Generate troubleshooting guide

### ExampleGeneratorAgent

Agent specialized in generating practical examples

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model, target_language)

##### generate_examples(self, use_cases, code_samples)

Generate practical examples

### LanguageValidatorAgent

Agent specialized in validating documentation language

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model)

##### validate_language(self, content, target_language)

Validate that content is in the target language

##### parse_validation_result(self, response)

Parse the validation response into structured data

### TutorialGenerator

Main tutorial generator using multi-agent system

#### Methods

##### __init__(self, project_path, elements, config, ai_client)

##### generate_complete_documentation(self, mode)

Generate tutorial documentation using AI agents

Args:
    mode: 'tutorials_only', 'api_only', or 'both' (default)

### AgentResponse

Response from an AI agent

**Decorators**: dataclass

### AIAgent

Base class for specialized AI agents

#### Methods

##### __init__(self, name, role, ai_client, ai_provider, model, max_tokens)

##### generate(self, prompt, context)

Generate content using AI

### InterfaceExplainerAgent

Agent specialized in explaining UI interfaces step-by-step

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model, target_language)

##### explain_interface(self, interface_description, features, readme_content, project_overview)

Generate detailed interface explanation

### QuickStartAgent

Agent specialized in creating quick start guides

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model, target_language)

##### create_quick_start(self, project_info)

Generate quick start guide

### APIDocumentationAgent

Agent specialized in API documentation

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model, target_language)

##### document_api(self, classes, functions)

Generate comprehensive API documentation

### TutorialSeriesAgent

Agent specialized in creating tutorial series

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model, target_language)

##### create_tutorial(self, level, topic, project_context)

Generate a tutorial for specific level

### TroubleshootingAgent

Agent specialized in troubleshooting guides

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model, target_language)

##### create_troubleshooting_guide(self, common_issues)

Generate troubleshooting guide

### ExampleGeneratorAgent

Agent specialized in generating practical examples

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model, target_language)

##### generate_examples(self, use_cases, code_samples)

Generate practical examples

### LanguageValidatorAgent

Agent specialized in validating documentation language

**Inherits from**: AIAgent

#### Methods

##### __init__(self, ai_client, ai_provider, model)

##### validate_language(self, content, target_language)

Validate that content is in the target language

##### parse_validation_result(self, response)

Parse the validation response into structured data

### TutorialGenerator

Main tutorial generator using multi-agent system

#### Methods

##### __init__(self, project_path, elements, config, ai_client)

##### generate_complete_documentation(self, mode)

Generate tutorial documentation using AI agents

Args:
    mode: 'tutorials_only', 'api_only', or 'both' (default)

