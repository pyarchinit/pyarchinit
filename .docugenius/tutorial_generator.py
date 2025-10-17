#!/usr/bin/env python3
"""
AI-Powered Tutorial Generator with Multi-Agent System
Generates comprehensive, fluid tutorials using specialized AI agents
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

# Import ProjectContextAnalyzer
from project_context_analyzer import ProjectContextAnalyzer, ProjectContext


@dataclass
class AgentResponse:
    """Response from an AI agent"""
    content: str
    agent_name: str
    success: bool
    error: Optional[str] = None


class AIAgent:
    """Base class for specialized AI agents"""

    def __init__(self, name: str, role: str, ai_client, ai_provider: str, model: str, max_tokens: int = 2000):
        self.name = name
        self.role = role
        self.ai_client = ai_client
        self.ai_provider = ai_provider
        self.model = model
        self.max_tokens = max_tokens

    def generate(self, prompt: str, context: str = "") -> AgentResponse:
        """Generate content using AI"""
        import sys

        if not self.ai_client:
            return AgentResponse(
                content="",
                agent_name=self.name,
                success=False,
                error="AI client not available"
            )

        try:
            # Log start of agent call
            print(f"\n{'='*60}")
            print(f"🤖 AGENT START: {self.name}")
            print(f"   Role: {self.role}")
            print(f"   Provider: {self.ai_provider}")
            print(f"   Model: {self.model}")
            print(f"   Max Tokens: {self.max_tokens}")
            print(f"{'='*60}")
            sys.stdout.flush()

            full_prompt = f"""You are a {self.role}.

{prompt}

Context:
{context}

Generate professional, clear, and engaging content. Use reStructuredText (RST) formatting.
Be conversational and include practical examples with input/output demonstrations.

RST Formatting Rules:
- Titles: Use underlines with =, -, ~, ^ (hierarchical)
- Code blocks: Use .. code-block:: python directive
- Lists: Use * or - for bullets, numbers for ordered
- Bold: **text**, Italic: *text*
- Links: `Link text <url>`_
- Sections: Underline with characters matching title length
"""

            if self.ai_provider == 'openai':
                response = self.ai_client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": full_prompt}],
                    max_tokens=self.max_tokens,
                    temperature=0.7,
                    timeout=120.0  # 2 minutes timeout
                )
                content = response.choices[0].message.content.strip()

            elif self.ai_provider == 'claude':
                response = self.ai_client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=0.7,
                    timeout=120.0,  # 2 minutes timeout
                    messages=[{"role": "user", "content": full_prompt}]
                )
                content = response.content[0].text.strip()
            else:
                print(f"❌ AGENT ERROR: Unsupported AI provider: {self.ai_provider}")
                sys.stdout.flush()
                return AgentResponse(
                    content="",
                    agent_name=self.name,
                    success=False,
                    error=f"Unsupported AI provider: {self.ai_provider}"
                )

            # Log end of agent call
            print(f"\n{'='*60}")
            print(f"✅ AGENT END: {self.name}")
            print(f"   Status: SUCCESS")
            print(f"   Content Length: {len(content)} characters")
            print(f"{'='*60}\n")
            sys.stdout.flush()

            return AgentResponse(
                content=content,
                agent_name=self.name,
                success=True
            )

        except Exception as e:
            # Log error in agent call
            print(f"\n{'='*60}")
            print(f"❌ AGENT END: {self.name}")
            print(f"   Status: FAILED")
            print(f"   Error: {str(e)}")
            print(f"{'='*60}\n")
            sys.stdout.flush()

            return AgentResponse(
                content="",
                agent_name=self.name,
                success=False,
                error=str(e)
            )


class InterfaceExplainerAgent(AIAgent):
    """Agent specialized in explaining UI interfaces step-by-step"""

    def __init__(self, ai_client, ai_provider: str, model: str, target_language: str = "English"):
        super().__init__(
            name="InterfaceExplainer",
            role="technical writer specialized in UI/UX documentation",
            ai_client=ai_client,
            ai_provider=ai_provider,
            model=model,
            max_tokens=8000  # Increased for comprehensive tutorials
        )
        self.target_language = target_language

    def explain_interface(self, interface_description: str, features: List[str], readme_content: str = "", project_overview: str = "") -> AgentResponse:
        """Generate detailed interface explanation"""

        # Build context section with README and project overview
        context_section = ""
        if readme_content:
            context_section += f"""
PROJECT README CONTENT (READ THIS CAREFULLY - this explains what the project is and how it works):
{readme_content}

"""

        if project_overview:
            context_section += f"""
PROJECT OVERVIEW:
{project_overview}

"""

        prompt = f"""Create a comprehensive, step-by-step tutorial/manual for THIS SPECIFIC PROJECT.

{context_section}
Interface Description:
{interface_description}

Features:
{chr(10).join(f"- {f}" for f in features)}

CRITICAL REQUIREMENTS:
1. READ THE README CONTENT ABOVE - Use it to understand what this project is, what it does, and its purpose
2. Write about THIS SPECIFIC PROJECT (use the project name from the README), NOT generic software
3. Start with a welcoming introduction in {self.target_language} that explains WHAT THIS PROJECT IS and WHAT IT DOES (based on README)
4. Explain EACH UI element found in the Interface Description (dialogs, buttons, fields, toolbars, icons, dropdowns, checkboxes, tabs) with:
   - What it does in the context of THIS PROJECT
   - How to use it for THIS PROJECT's specific tasks
   - Practical example relevant to THIS PROJECT
   - Screenshots descriptions if applicable
5. Use conversational, fluid language in {self.target_language}
6. Include practical scenarios SPECIFIC to THIS PROJECT's use cases (from README)
7. Add emojis for visual appeal
8. Format with clear sections and sub-sections
9. If icons are mentioned in the Interface Description, reference them in your explanations
10. Focus on the PROJECT as a whole, not individual classes or internal components

IMPORTANT: Write the ENTIRE tutorial in {self.target_language}. ALL text, headings, descriptions, and content MUST be in {self.target_language}.

Structure (adapt section titles to {self.target_language}):
# 📚 Complete Manual - [PROJECT NAME from README]

## 🚀 Welcome
[Welcoming introduction in {self.target_language} that explains WHAT THIS PROJECT IS, WHAT IT DOES, and WHO IT'S FOR - based on README content]

## 📖 Project Overview
[Overview in {self.target_language} of the project purpose, main goals, and target users - from README]

## 🎯 Main Interface
[Explain the main interface, dialogs, windows in {self.target_language}]

### Dialog/Window: [Dialog Name from Interface Description]
[Overview in {self.target_language} of what this dialog/window is for in the context of THIS PROJECT]

#### Button/Field: "[Element Name]"
- **Description**: [What it does in THIS PROJECT - in {self.target_language}]
- **How to use it**: [How to use it for THIS PROJECT's tasks - in {self.target_language}]
- **Practical Example**:
  ```
  Input:  [example relevant to THIS PROJECT]
  Output: [result in THIS PROJECT]
  ```
- **Icon**: [If icon mentioned, describe it in {self.target_language}]

[Continue for all UI elements mentioned in Interface Description]

## 🔧 Toolbars and Buttons
[Explain toolbars and buttons found in Interface Description - in {self.target_language}]

## 💡 Complete Practical Examples
### Scenario 1: [Use case specific to THIS PROJECT from README]
[Step by step in {self.target_language} with screenshots descriptions using UI elements from Interface Description]

### Scenario 2: [Another use case from THIS PROJECT]
[Step by step in {self.target_language}]

## ❓ Frequently Asked Questions
[FAQ in {self.target_language} relevant to THIS PROJECT's purpose and usage]

## 🔧 Troubleshooting
[Troubleshooting in {self.target_language} for THIS PROJECT]

CRITICAL: Write EVERYTHING in {self.target_language}. Do NOT use any other language. The tutorial must be about the SPECIFIC PROJECT described in the README and Interface Description, NOT generic software. Use the project name, reference its specific features, dialogs, and UI elements.
"""
        return self.generate(prompt)


class QuickStartAgent(AIAgent):
    """Agent specialized in creating quick start guides"""

    def __init__(self, ai_client, ai_provider: str, model: str, target_language: str = "English"):
        super().__init__(
            name="QuickStart",
            role="developer advocate creating getting-started guides",
            ai_client=ai_client,
            ai_provider=ai_provider,
            model=model,
            max_tokens=4000  # Sufficient for detailed quick start
        )
        self.target_language = target_language

    def create_quick_start(self, project_info: Dict[str, Any]) -> AgentResponse:
        """Generate quick start guide"""
        # Extract information from project_info
        name = project_info.get('name', 'Software')
        ptype = project_info.get('type', 'Application')
        description = project_info.get('description', '')
        features = project_info.get('features', [])
        installation = project_info.get('installation', '')
        dependencies = project_info.get('dependencies', [])
        readme_excerpt = project_info.get('readme_excerpt', '')

        prompt = f"""Create an engaging quick start guide for this REAL project.

Project: {name}
Type: {ptype}
Description: {description}

Features:
{chr(10).join(f'- {f}' for f in features[:10])}

Installation Instructions (from README):
{installation}

Dependencies:
{chr(10).join(f'- {d}' for d in dependencies[:10])}

IMPORTANT REQUIREMENTS:
1. Write in {self.target_language} with conversational tone
2. Use ACTUAL installation steps from above (not generic examples)
3. Reference ACTUAL project name and type
4. Create realistic first example based on project type
5. DO NOT invent features - use only those listed above
6. Show expected output that matches project functionality
7. Use emojis and code blocks

Structure:
# 🚀 Quick Start - {name}

## 📖 What is {name}?
[Brief explanation based on description and type]

## 💿 Installation
[Use ACTUAL installation instructions provided above]

## ⚡ First Example
[Create realistic example based on project type: {ptype}]

### Input:
```
[realistic example for this specific project]
```

### Output:
```
[realistic output]
```

## 🎯 What's Next?
[Links to other tutorials]
"""

        # Build rich context
        context = f"""README Excerpt:
{readme_excerpt}

Project Information:
{json.dumps(project_info, indent=2)}
"""

        return self.generate(prompt, context)


class APIDocumentationAgent(AIAgent):
    """Agent specialized in API documentation"""

    def __init__(self, ai_client, ai_provider: str, model: str, target_language: str = "English"):
        super().__init__(
            name="APIDocumenter",
            role="API documentation specialist",
            ai_client=ai_client,
            ai_provider=ai_provider,
            model=model,
            max_tokens=6000  # Comprehensive API docs need more tokens
        )
        self.target_language = target_language

    def document_api(self, classes: List[Any], functions: List[Any]) -> AgentResponse:
        """Generate comprehensive API documentation"""

        # Prepare context
        context = "Classs:\n"
        for cls in classes[:10]:  # Limit to top 10
            context += f"- {cls.name}: {getattr(cls, 'docstring', 'No description')}\n"
            methods = getattr(cls, 'children', [])
            for method in methods[:3]:
                context += f"  - {method.name}()\n"

        context += "\nFunctions:\n"
        for func in functions[:10]:
            context += f"- {func.name}()\n"

        prompt = f"""Create detailed API reference documentation in {self.target_language}.

For EACH class and function:
1. Clear description
2. Parameters with types and examples
3. Return value with type
4. Code example showing usage
5. Common use cases

Use this format:

## Class `ClassName`

**Description**: [What it does]

**Constructor**:
```python
ClassName(param1: type, param2: type)
```

**Parameters**:
- `param1` (type): Description con esempio: `"valore"`
- `param2` (type): Description con esempio: `123`

**Methods**:

### `method_name(param: type) -> return_type`

**Description**: [What it does]

**Practical Example**:
```python
# Input
obj = ClassName()
result = obj.method_name("example")

# Output
>>> result
{{'key': 'value'}}
```

**When to Use It**: [Use case]
"""
        return self.generate(prompt, context)


class TutorialSeriesAgent(AIAgent):
    """Agent specialized in creating tutorial series"""

    def __init__(self, ai_client, ai_provider: str, model: str, target_language: str = "English"):
        super().__init__(
            name="TutorialSeries",
            role="educational content creator for technical tutorials",
            ai_client=ai_client,
            ai_provider=ai_provider,
            model=model,
            max_tokens=3000
        )
        self.target_language = target_language

    def create_tutorial(self, level: str, topic: str, project_context: str) -> AgentResponse:
        """Generate a tutorial for specific level"""
        prompt = f"""Create a {level}-level tutorial about: {topic}

Level: {level} (Beginner/Intermediate/Advanced)
Topic: {topic}

Requirements:
1. Write in {self.target_language} with friendly, conversational tone
2. Progressive learning - build on previous concepts
3. Hands-on examples users can type and run
4. Show actual output/results
5. Common pitfalls and how to avoid them
6. Practice exercises with solutions

Structure:

# Tutorial {level.title()}: {topic}

## 🎯 Goals
[What you'll learn]

## 📋 Prerequisites
[What you need to know]

## 📖 Key Concepts
[Core concepts explained simply]

## 💻 Practical Example
[Step-by-step walkthrough]

### Step 1: [Action]
```python
# Code here
```

**Output**:
```
[What you see]
```

**Explanation**: [Why this works]

### Step 2-N: [Continue]

## 🎓 Exercises
1. [Exercise with solution]
2. [Exercise with solution]

## 💡 Tips
[Tips and tricks]

## ⚠️ Common Errors
[Common mistakes]

## 🔗 Additional Resources
[Links to related topics]
"""
        return self.generate(prompt, project_context)


class TroubleshootingAgent(AIAgent):
    """Agent specialized in troubleshooting guides"""

    def __init__(self, ai_client, ai_provider: str, model: str, target_language: str = "English"):
        super().__init__(
            name="Troubleshooter",
            role="technical support specialist",
            ai_client=ai_client,
            ai_provider=ai_provider,
            model=model,
            max_tokens=2000
        )
        self.target_language = target_language

    def create_troubleshooting_guide(self, common_issues: List[str]) -> AgentResponse:
        """Generate troubleshooting guide"""
        prompt = f"""Create a comprehensive troubleshooting guide in {self.target_language}.

Common Issue Categories: {', '.join(common_issues)}

For each issue:
1. Clear problem description
2. Symptoms (what user sees)
3. Multiple solutions (from simple to complex)
4. How to verify it's fixed
5. Prevention tips

Structure:

# 🔧 Troubleshooting

## 🚨 Common Issues

### Problem: [Issue Name]

**Symptoms**:
- [What the user experiences]
```
[Error message or behavior]
```

**Possible Causes**:
1. [Cause 1]
2. [Cause 2]

**Solution 1** (Simple):
```bash
[Command or action]
```

**Verification**:
```bash
[How to test]
```

**Solution 2** (Advanced):
[If simple solution doesn't work]

**Prevention**:
[How to avoid this in future]

---

[Continue for all issues]

## 📞 Getting Help
[Where to get support]
"""
        issues_context = "\n".join(f"- {issue}" for issue in common_issues)
        return self.generate(prompt, issues_context)


class ExampleGeneratorAgent(AIAgent):
    """Agent specialized in generating practical examples"""

    def __init__(self, ai_client, ai_provider: str, model: str, target_language: str = "English"):
        super().__init__(
            name="ExampleGenerator",
            role="developer creating practical code examples",
            ai_client=ai_client,
            ai_provider=ai_provider,
            model=model,
            max_tokens=2000
        )
        self.target_language = target_language

    def generate_examples(self, use_cases: List[str], code_samples: List[Any]) -> AgentResponse:
        """Generate practical examples"""
        prompt = f"""Create practical, runnable code examples in {self.target_language}.

Use Cases:
{chr(10).join(f"- {uc}" for uc in use_cases)}

For EACH use case:
1. Real-world scenario
2. Complete working code
3. Input data example
4. Expected output
5. Variations and alternatives

Structure:

# 💡 Practical Examples

## Example 1: [Use Case Title]

**Scenario**: [Real-world situation]

**Complete Code**:
```python
# File: example_1.py
[Complete, runnable code]
```

**Input Data**:
```python
input_data = {{
    "key": "value"
}}
```

**Execution**:
```bash
$ python example_1.py
```

**Expected Output**:
```
[Exact output]
```

**Explanation**:
[Line-by-line explanation]

**Variants**:
- [Alternative approach 1]
- [Alternative approach 2]

---

[Continue for all use cases]

## 🎯 Combined Use Cases
[How to combine examples]
"""
        samples_context = "\n".join(str(s) for s in code_samples[:5])
        return self.generate(prompt, samples_context)


class LanguageValidatorAgent(AIAgent):
    """Agent specialized in validating documentation language"""

    def __init__(self, ai_client, ai_provider: str, model: str):
        super().__init__(
            name="LanguageValidator",
            role="language quality assurance specialist",
            ai_client=ai_client,
            ai_provider=ai_provider,
            model=model,
            max_tokens=1000  # Short responses for validation
        )

    def validate_language(self, content: str, target_language: str) -> AgentResponse:
        """Validate that content is in the target language"""
        prompt = f"""Analyze the following documentation content and verify it is written in {target_language}.

Content to analyze (first 1000 characters):
{content[:1000]}

Requirements:
1. Identify the primary language used in the content
2. Check if it matches the target language: {target_language}
3. If there's a mismatch, identify which sections are in the wrong language
4. Provide a confidence score (0-100%)

Respond in this exact format:

DETECTED_LANGUAGE: [language name]
MATCHES_TARGET: [YES/NO]
CONFIDENCE: [0-100]%
ISSUES: [list any language mismatches found, or "None" if correct]

Example response:
DETECTED_LANGUAGE: Italian
MATCHES_TARGET: NO
CONFIDENCE: 95%
ISSUES: Content is in Italian but target language is English. Sections with Italian: headers, field descriptions, examples.
"""
        return self.generate(prompt, "")

    def parse_validation_result(self, response: AgentResponse) -> Dict[str, Any]:
        """Parse the validation response into structured data"""
        if not response.success:
            return {
                'valid': False,
                'detected_language': 'unknown',
                'matches_target': False,
                'confidence': 0,
                'issues': response.error
            }

        content = response.content
        result = {
            'valid': True,
            'detected_language': 'unknown',
            'matches_target': False,
            'confidence': 0,
            'issues': 'None'
        }

        # Parse the response
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('DETECTED_LANGUAGE:'):
                result['detected_language'] = line.split(':', 1)[1].strip()
            elif line.startswith('MATCHES_TARGET:'):
                result['matches_target'] = 'YES' in line.upper()
            elif line.startswith('CONFIDENCE:'):
                try:
                    conf_str = line.split(':', 1)[1].strip().replace('%', '')
                    result['confidence'] = int(conf_str)
                except:
                    result['confidence'] = 0
            elif line.startswith('ISSUES:'):
                result['issues'] = line.split(':', 1)[1].strip()

        return result


class TutorialGenerator:
    """Main tutorial generator using multi-agent system"""

    def __init__(self, project_path: Path, elements: List[Any], config: Dict[str, Any], ai_client=None):
        self.project_path = project_path
        self.elements = elements
        self.config = config
        self.ai_client = ai_client
        self.ai_provider = config.get('ai_provider', 'none')
        self.ai_model = config.get('ai_model', 'gpt-4.1')

        # Get target language from config (default to English)
        self.target_language = config.get('target_language', 'en')

        # Map language codes to full names for prompts
        self.language_names = {
            'en': 'English',
            'it': 'Italian',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German'
        }
        self.language_name = self.language_names.get(self.target_language, 'English')

        # ANALYZE PROJECT CONTEXT BEFORE GENERATING TUTORIALS
        print("\n🔍 Analyzing project context...")
        import sys
        sys.stdout.flush()

        analyzer = ProjectContextAnalyzer(project_path)
        self.project_context = analyzer.analyze()

        print(f"✅ Project context ready: {self.project_context.project_name}")
        print(f"   Type: {self.project_context.project_type}")
        print(f"   UI Elements: {len(self.project_context.ui_elements)} dialogs")
        print(f"   Features: {len(self.project_context.main_features)}")
        sys.stdout.flush()

        # Initialize specialized agents
        self.agents = {
            'interface': InterfaceExplainerAgent(ai_client, self.ai_provider, self.ai_model, self.language_name),
            'quickstart': QuickStartAgent(ai_client, self.ai_provider, self.ai_model, self.language_name),
            'api': APIDocumentationAgent(ai_client, self.ai_provider, self.ai_model, self.language_name),
            'tutorial': TutorialSeriesAgent(ai_client, self.ai_provider, self.ai_model, self.language_name),
            'troubleshoot': TroubleshootingAgent(ai_client, self.ai_provider, self.ai_model, self.language_name),
            'examples': ExampleGeneratorAgent(ai_client, self.ai_provider, self.ai_model, self.language_name),
            'validator': LanguageValidatorAgent(ai_client, self.ai_provider, self.ai_model)
        }

    def generate_complete_documentation(self, mode: str = 'both') -> Dict[str, str]:
        """Generate tutorial documentation using AI agents

        Args:
            mode: 'tutorials_only', 'api_only', or 'both' (default)
        """
        docs = {}
        import sys

        print(f"🤖 Starting multi-agent documentation generation (mode: {mode})...")
        sys.stdout.flush()

        # Extract common data
        features = self._extract_features()
        classes = [e for e in self.elements if e.type == 'class']
        functions = [e for e in self.elements if e.type == 'function']

        # TUTORIALS MODE (or both)
        if mode in ['tutorials_only', 'both']:
            print("\n📚 GENERATING TUTORIALS...")
            sys.stdout.flush()

            # 1. Interface Tutorial (MAIN - most important)
            print("📱 Agent 1/6: Generating interface tutorial...")
            sys.stdout.flush()
            interface_desc = self._build_interface_description()

            # Build comprehensive project overview from README and context
            project_overview = f"""
Project Name: {self.project_context.project_name}
Type: {self.project_context.project_type}
Description: {self.project_context.description}

Installation: {self.project_context.installation_method}

Dependencies: {', '.join(self.project_context.dependencies[:20])}

Main Features:
{chr(10).join(f'- {f}' for f in self.project_context.main_features[:20])}

Entry Points: {', '.join(self.project_context.entry_points[:10])}
"""

            # Pass README content and project overview to agent
            response = self.agents['interface'].explain_interface(
                interface_desc,
                features,
                readme_content=self.project_context.readme_content[:4000],  # Limit to avoid token overflow
                project_overview=project_overview
            )
            if response.success:
                docs['TUTORIAL.rst'] = response.content
                print("✅ Interface tutorial generated")
                sys.stdout.flush()
            else:
                print(f"❌ Interface tutorial failed: {response.error}")
                sys.stdout.flush()
                docs['TUTORIAL.rst'] = self._generate_fallback_tutorial()

            # 2. Quick Start Guide
            print("🚀 Agent 2/6: Generating quick start guide...")
            sys.stdout.flush()
            ctx = self.project_context
            project_info = {
                'name': ctx.project_name,
                'type': ctx.project_type,
                'description': ctx.description,
                'features': features,
                'installation': ctx.installation_method,
                'dependencies': ctx.dependencies[:10],
                'readme_excerpt': ctx.readme_content[:1500]
            }
            response = self.agents['quickstart'].create_quick_start(project_info)
            if response.success:
                docs['QUICK_START.rst'] = response.content
                print("✅ Quick start generated")
                sys.stdout.flush()

            # 3. Tutorial Series
            print("🎓 Agent 3/6: Generating tutorial series...")
            sys.stdout.flush()
            tutorials = {}
            for level, topic in [
                ('Beginner', 'Getting Started and Configuration'),
                ('Intermediate', 'Advanced Features'),
                ('Advanced', 'Optimization and Best Practices')
            ]:
                print(f"  - {level}: {topic}")
                sys.stdout.flush()
                response = self.agents['tutorial'].create_tutorial(
                    level, topic, self._build_project_context()
                )
                if response.success:
                    filename = f"tutorial_{level.lower()}.rst"
                    tutorials[filename] = response.content
                    print(f"    ✓ {level} tutorial complete")
                    sys.stdout.flush()

            if tutorials:
                docs.update(tutorials)
                print("✅ Tutorial series generated")
                sys.stdout.flush()

            # 4. Troubleshooting Guide
            print("🔧 Agent 4/6: Generating troubleshooting guide...")
            sys.stdout.flush()
            common_issues = [
                'Installation',
                'Configuration',
                'Runtime Errors',
                'Performance',
                'Integration'
            ]
            response = self.agents['troubleshoot'].create_troubleshooting_guide(common_issues)
            if response.success:
                docs['TROUBLESHOOTING.rst'] = response.content
                print("✅ Troubleshooting guide generated")
                sys.stdout.flush()

            # 5. Practical Examples
            print("💡 Agent 5/6: Generating practical examples...")
            sys.stdout.flush()
            use_cases = self._identify_use_cases()
            code_samples = classes[:5]  # Sample classes
            response = self.agents['examples'].generate_examples(use_cases, code_samples)
            if response.success:
                docs['EXAMPLES.rst'] = response.content
                print("✅ Examples generated")
                sys.stdout.flush()

        # API MODE (or both)
        if mode in ['api_only', 'both']:
            print("\n📖 GENERATING API DOCUMENTATION...")
            sys.stdout.flush()

            # API Documentation
            print("📚 Agent 6/6: Generating API documentation...")
            sys.stdout.flush()
            response = self.agents['api'].document_api(classes, functions)
            if response.success:
                docs['API_REFERENCE.rst'] = response.content
                print("✅ API documentation generated")
                sys.stdout.flush()

        # 7. Language Validation (validate first generated document)
        if docs and self.ai_client:
            print("\n🔍 Validating documentation language...")
            sys.stdout.flush()

            # Validate the main tutorial (TUTORIAL.rst)
            if 'TUTORIAL.rst' in docs:
                response = self.agents['validator'].validate_language(
                    docs['TUTORIAL.rst'],
                    self.language_name
                )
                if response.success:
                    result = self.agents['validator'].parse_validation_result(response)
                    if result['matches_target']:
                        print(f"✅ Language validation passed: {result['detected_language']} (confidence: {result['confidence']}%)")
                    else:
                        print(f"⚠️  Language mismatch detected!")
                        print(f"   Expected: {self.language_name}")
                        print(f"   Detected: {result['detected_language']} (confidence: {result['confidence']}%)")
                        print(f"   Issues: {result['issues']}")
                    sys.stdout.flush()

        # 8. Process icon markers and copy icon files
        print("\n🎨 Processing icons for documentation...")
        sys.stdout.flush()
        docs = self._process_icons_in_docs(docs)

        print("\n🎉 Multi-agent tutorial generation complete!")
        sys.stdout.flush()
        return docs

    def _build_interface_description(self) -> str:
        """Build description of the software interface from analyzed project context"""
        ctx = self.project_context

        # Build description from UI elements found in the project
        interface_desc = f"""PROJECT: {ctx.project_name}

DESCRIPTION: {ctx.description}

PROJECT TYPE: {ctx.project_type}

"""

        # Add UI elements (dialogs, buttons, tabs) found during analysis
        if ctx.ui_elements:
            interface_desc += "**USER INTERFACE ELEMENTS (Dialogs, Windows, Forms):**\n\n"
            interface_desc += f"Total dialogs/windows: {len(ctx.ui_elements)}\n\n"

            # Group UI elements by type
            buttons_count = 0
            tabs_count = 0
            fields_count = 0

            for dialog_name, elements in list(ctx.ui_elements.items())[:15]:  # Limit to 15 dialogs
                interface_desc += f"### Dialog/Window: **{dialog_name}**\n"
                interface_desc += f"Number of elements: {len(elements)}\n\n"

                # Categorize elements
                buttons = [e for e in elements if 'Button' in e or 'Btn' in e or 'button' in e.lower()]
                tabs = [e for e in elements if 'Tab' in e or 'tab' in e.lower()]
                fields = [e for e in elements if any(x in e for x in ['LineEdit', 'TextEdit', 'ComboBox', 'SpinBox', 'CheckBox', 'RadioButton'])]
                other = [e for e in elements if e not in buttons + tabs + fields]

                if buttons:
                    interface_desc += f"**Buttons ({len(buttons)}):**\n"
                    for btn in buttons[:10]:
                        interface_desc += f"  - {btn}\n"
                    buttons_count += len(buttons)
                    interface_desc += "\n"

                if tabs:
                    interface_desc += f"**Tabs ({len(tabs)}):**\n"
                    for tab in tabs[:10]:
                        interface_desc += f"  - {tab}\n"
                    tabs_count += len(tabs)
                    interface_desc += "\n"

                if fields:
                    interface_desc += f"**Input Fields ({len(fields)}):**\n"
                    for field in fields[:10]:
                        interface_desc += f"  - {field}\n"
                    fields_count += len(fields)
                    interface_desc += "\n"

                if other:
                    interface_desc += f"**Other Elements ({len(other)}):**\n"
                    for elem in other[:10]:
                        interface_desc += f"  - {elem}\n"
                    interface_desc += "\n"

                interface_desc += "\n"

            # Add summary
            interface_desc += f"""
**UI ELEMENTS SUMMARY:**
- Total Buttons: {buttons_count}
- Total Tabs: {tabs_count}
- Total Input Fields: {fields_count}
- Total Dialogs/Windows: {len(ctx.ui_elements)}

"""
        else:
            # Fallback if no UI elements found
            interface_desc += "**Command-line or library project** (no graphical interface detected)\n\n"

        # Add icon information
        if ctx.icon_files:
            interface_desc += f"**ICONS AVAILABLE ({len(ctx.icon_files)}):**\n"
            for icon_name, icon_path in list(ctx.icon_files.items())[:20]:
                interface_desc += f"- {icon_name}: {icon_path}\n"
            interface_desc += "\n"

        # Add README installation instructions
        if ctx.installation_method and len(ctx.installation_method) > 10:
            interface_desc += f"**INSTALLATION:**\n{ctx.installation_method}\n\n"

        return interface_desc

    def _extract_features(self) -> List[str]:
        """Extract main features from project context (README)"""
        ctx = self.project_context

        # Use features extracted from README
        if ctx.main_features:
            return ctx.main_features[:15]  # Limit to 15 features

        # Fallback: generate features from project structure
        features = []
        if ctx.dependencies:
            features.append(f"Uses {len(ctx.dependencies)} dependencies: {', '.join(ctx.dependencies[:5])}")

        if ctx.ui_elements:
            features.append(f"Graphical user interface with {len(ctx.ui_elements)} dialogs/windows")

        if ctx.code_structure.get('main_classes'):
            features.append(f"Core classes: {', '.join(ctx.code_structure['main_classes'][:5])}")

        return features if features else ["Feature documentation available in README"]

    def _detect_project_type(self) -> str:
        """Detect type of project from analyzed context"""
        return self.project_context.project_type

    def _build_project_context(self) -> str:
        """Build context about the project from analyzed data"""
        ctx = self.project_context
        classes = [e for e in self.elements if e.type == 'class']
        functions = [e for e in self.elements if e.type == 'function']

        context = f"""Project Name: {ctx.project_name}
Type: {ctx.project_type}
Description: {ctx.description}

Code Structure:
- Total Python Files: {ctx.code_structure.get('total_python_files', 0)}
- Classes: {len(classes)}
- Functions: {len(functions)}
- Main Components: {', '.join(c.name for c in classes[:10])}

Dependencies ({len(ctx.dependencies)}):
{chr(10).join(f'- {dep}' for dep in ctx.dependencies[:10])}

Installation Method:
{ctx.installation_method}

README Content (excerpt):
{ctx.readme_content[:1000]}
"""

        return context

    def _identify_use_cases(self) -> List[str]:
        """Identify common use cases from project type and features"""
        ctx = self.project_context
        use_cases = []

        # Generate use cases based on project type
        if ctx.project_type == 'qgis_plugin':
            use_cases = [
                'Install and activate the QGIS plugin',
                'Configure plugin settings and database connection',
                'Use main dialogs and data entry forms',
                'Generate reports and export data',
                'Integrate with QGIS layers and maps'
            ]
        elif ctx.project_type == 'plugin':
            use_cases = [
                'Install the plugin in the host application',
                'Configure plugin preferences',
                'Use main features through the UI',
                'Export and share results'
            ]
        elif ctx.project_type == 'library':
            use_cases = [
                'Install the library via pip/npm',
                'Import and use core classes',
                'Common API usage patterns',
                'Error handling and best practices',
                'Integration with other libraries'
            ]
        elif ctx.project_type == 'cli':
            use_cases = [
                'Install command-line tool',
                'Basic command usage',
                'Common command combinations',
                'Configuration and customization',
                'Troubleshooting common issues'
            ]
        else:
            # Generic use cases
            use_cases = [
                'Installation and setup',
                'Basic usage example',
                'Advanced features',
                'Configuration options',
                'Troubleshooting'
            ]

        return use_cases[:10]  # Limit to 10

    def _process_icons_in_docs(self, docs: Dict[str, str]) -> Dict[str, str]:
        """Process [ICON:...] markers in documentation and replace with actual icons or emoji"""
        import re
        from pathlib import Path
        import shutil

        processed_docs = {}
        ctx = self.project_context

        # Create icons directory in output (will be created by main generator)
        # For now, just replace markers with appropriate syntax

        for filename, content in docs.items():
            # Find all [ICON:...] markers
            icon_markers = re.findall(r'\[ICON:([^\]]+)\]', content)

            if icon_markers:
                for icon_marker in icon_markers:
                    if icon_marker.startswith('EMOJI:'):
                        # Use emoji
                        emoji = icon_marker.replace('EMOJI:', '')
                        content = content.replace(f'[ICON:{icon_marker}]', emoji)
                    else:
                        # Use actual icon file
                        # For RST format: .. image:: icons/icon_name.png
                        # For Markdown format: ![icon](icons/icon_name.png)
                        icon_path = icon_marker

                        # Determine if this is RST or Markdown
                        if filename.endswith('.rst'):
                            # RST format with inline image
                            icon_ref = f'|icon| '
                            # We'll add the directive at the end, but for now use emoji fallback
                            # Find emoji from icon name
                            icon_name = Path(icon_path).stem
                            emoji = self._get_emoji_for_icon(icon_name)
                            content = content.replace(f'[ICON:{icon_marker}]', emoji)
                        else:
                            # Markdown format
                            icon_filename = Path(icon_path).name
                            content = content.replace(f'[ICON:{icon_marker}]', f'![icon](icons/{icon_filename})')

            processed_docs[filename] = content

        return processed_docs

    def _get_emoji_for_icon(self, icon_name: str) -> str:
        """Get emoji for icon name (fallback when icons can't be embedded)"""
        icon_name = icon_name.lower()

        emoji_map = {
            'save': '💾', 'open': '📂', 'folder': '📁', 'new': '✨',
            'delete': '🗑️', 'remove': '❌', 'add': '➕', 'edit': '✏️',
            'search': '🔍', 'filter': '🔎', 'zoom': '🔍', 'print': '🖨️',
            'pdf': '📄', 'export': '📤', 'import': '📥', 'upload': '⬆️',
            'download': '⬇️', 'left': '⬅️', 'right': '➡️', 'up': '⬆️',
            'down': '⬇️', 'arrow': '→', 'info': 'ℹ️', 'help': '❓',
            'settings': '⚙️', 'config': '⚙️', 'database': '🗄️',
            'table': '📊', 'chart': '📈', 'map': '🗺️', 'gis': '🗺️',
            'excel': '📊', 'doc': '📄', 'image': '🖼️', 'camera': '📷',
            'close': '✖️', 'cancel': '🚫', 'ok': '✅', 'warning': '⚠️',
        }

        for keyword, emoji in emoji_map.items():
            if keyword in icon_name:
                return emoji

        return '🔘'

    def _generate_fallback_tutorial(self) -> str:
        """Generate fallback tutorial if AI fails"""
        return f"""# 📚 Tutorial - {self.project_path.name}

## 🚀 Welcome

Welcome to the tutorial for {self.project_path.name}!

**Nota**: This is a basic automatically generated tutorial.
For more detailed tutorials, enable AI in the tab "AI Settings".

## 📋 Requirements

Before starting, make sure you have:
- Python 3.8+
- pip (package manager)

## 💿 Installation

```bash
pip install -r requirements.txt
```

## ⚡ First Use

```python
# Example base
from {self.project_path.name.lower()} import main

result = main()
print(result)
```

## 📚 Complete Documentation

See the complete API documentation in `API_REFERENCE.md`.

---

*Generated with DocuGenius - {datetime.now().strftime('%Y-%m-%d')}*
*For more detailed tutorials, enable AI in settings*
"""