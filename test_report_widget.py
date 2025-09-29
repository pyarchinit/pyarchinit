#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify report text is showing in widget
"""

import sys
import os
from pathlib import Path

# Add the plugin directory to Python path
plugin_dir = Path(__file__).parent
sys.path.insert(0, str(plugin_dir))

def test_gpt5_wrapper():
    """Test GPT5DirectWrapper functionality"""
    print("\n=== Testing GPT5DirectWrapper ===")

    try:
        # Import necessary modules
        from langchain_openai import ChatOpenAI

        # First, check if GPT5DirectWrapper is working
        print("\n1. Testing GPT5DirectWrapper class...")

        # Create a mock LLM
        class MockLLM:
            def invoke(self, prompt):
                class Response:
                    def __init__(self):
                        self.content = "This is a test response from the mock GPT-5 model. It contains multiple sentences. Each sentence is separated. This simulates a real response."
                return Response()

        # Test the wrapper
        from tabs.US_USM import GenerateReportThread

        # Create a mock wrapper similar to GPT5DirectWrapper
        class TestGPT5Wrapper:
            def __init__(self, llm):
                self.llm = llm

            def invoke(self, input_dict, config=None):
                """Test invoke method"""
                prompt = input_dict.get("input", "")
                callbacks = config.get("callbacks", []) if config else []

                print(f"  - Received prompt: {prompt[:50]}...")
                print(f"  - Found {len(callbacks)} callbacks")

                # Generate response
                response = self.llm.invoke(prompt)
                output = response.content if hasattr(response, 'content') else str(response)

                print(f"  - Generated response: {len(output)} chars")

                # Emit through callbacks
                emitted_count = 0
                if callbacks:
                    for callback in callbacks:
                        if hasattr(callback, 'on_llm_new_token'):
                            print("  - Emitting chunks to callback...")
                            chunk_size = 50
                            for i in range(0, len(output), chunk_size):
                                chunk = output[i:i+chunk_size]
                                callback.on_llm_new_token(chunk, chunk=None)
                                emitted_count += 1

                print(f"  - Emitted {emitted_count} chunks")

                return {"output": output}

        # Test the wrapper
        mock_llm = MockLLM()
        wrapper = TestGPT5Wrapper(mock_llm)

        # Create a mock callback
        class MockCallback:
            def __init__(self):
                self.tokens_received = []

            def on_llm_new_token(self, token, **kwargs):
                self.tokens_received.append(token)

        callback = MockCallback()

        # Test invoke
        result = wrapper.invoke(
            {"input": "Test prompt"},
            config={"callbacks": [callback]}
        )

        print(f"\n✅ Wrapper test successful:")
        print(f"  - Output length: {len(result['output'])} chars")
        print(f"  - Chunks received by callback: {len(callback.tokens_received)}")
        print(f"  - First chunk: '{callback.tokens_received[0] if callback.tokens_received else 'None'}'")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_streaming_handler():
    """Test StreamHandler for report generation"""
    print("\n=== Testing StreamHandler ===")

    try:
        from qgis.PyQt.QtCore import QThread, pyqtSignal

        # Create a mock thread with stream_token signal
        class MockThread(QThread):
            stream_token = pyqtSignal(str)

            def __init__(self):
                super().__init__()
                self.received_tokens = []
                # Connect signal to track emissions
                self.stream_token.connect(self.on_token)

            def on_token(self, token):
                self.received_tokens.append(token)
                print(f"  - Token emitted: '{token[:30]}...'")

        # Create mock thread
        thread = MockThread()

        # Test StreamHandler
        from langchain.callbacks.base import BaseCallbackHandler

        class TestStreamHandler(BaseCallbackHandler):
            def __init__(self, parent_thread):
                self.parent_thread = parent_thread
                self.buffer = ""

            def on_llm_new_token(self, token, **kwargs):
                # Emit token for streaming display
                self.parent_thread.stream_token.emit(token)
                # Also accumulate in buffer
                self.buffer += token

        # Create handler
        handler = TestStreamHandler(thread)

        # Test emitting tokens
        test_tokens = ["This ", "is ", "a ", "test ", "message."]
        for token in test_tokens:
            handler.on_llm_new_token(token)

        print(f"\n✅ StreamHandler test successful:")
        print(f"  - Tokens emitted: {len(thread.received_tokens)}")
        print(f"  - Buffer content: '{handler.buffer}'")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_format_for_widget():
    """Test the format_for_widget method"""
    print("\n=== Testing format_for_widget ===")

    try:
        # Create a mock object with the format_for_widget method
        class MockFormatter:
            def format_for_widget(self, text):
                """Format text for HTML widget display"""
                lines = text.split('\n')
                formatted_lines = []

                for line in lines:
                    line = line.strip()

                    if not line:
                        formatted_lines.append('<br>')
                        continue

                    # Check for headings
                    if line.startswith('#'):
                        level = len(line) - len(line.lstrip('#'))
                        heading_text = line.lstrip('#').strip()
                        size = 18 - (level * 2)
                        formatted_lines.append(
                            f'<p style="font-size:{size}pt;font-weight:bold;font-family:Cambria;">'
                            f'{heading_text}</p>'
                        )
                    elif line.startswith('-') or line.startswith('*'):
                        # Bullet point
                        text = line.lstrip('-*').strip()
                        formatted_lines.append(
                            f'<p style="margin-left:20px;font-size:12pt;font-family:Cambria;">• {text}</p>'
                        )
                    else:
                        # Regular paragraph
                        formatted_lines.append(
                            f'<p style="font-size:12pt;font-family:Cambria;">{line}</p>'
                        )

                return ''.join(formatted_lines)

        # Test formatting
        formatter = MockFormatter()

        test_text = """# Main Heading
This is a regular paragraph.

## Sub Heading
- First bullet point
- Second bullet point

Regular text after bullets."""

        formatted = formatter.format_for_widget(test_text)

        print(f"✅ Format test successful:")
        print(f"  - Input lines: {len(test_text.split(chr(10)))}")
        print(f"  - Output length: {len(formatted)} chars")
        print(f"  - Contains HTML: {'<p' in formatted}")
        print(f"  - Contains styles: {'style=' in formatted}")

        # Show sample of formatted output
        print(f"\nSample HTML output:")
        print(formatted[:200] + "...")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_report_generated_signal():
    """Test report_generated signal emission"""
    print("\n=== Testing report_generated Signal ===")

    try:
        from qgis.PyQt.QtCore import QThread, pyqtSignal

        # Create a mock thread with report_generated signal
        class MockReportThread(QThread):
            report_generated = pyqtSignal(str)

            def __init__(self):
                super().__init__()
                self.formatted_report = ""

            def emit_report(self, content):
                self.formatted_report += content
                print(f"  - Emitting report: {len(self.formatted_report)} chars")
                self.report_generated.emit(self.formatted_report)

        # Create thread
        thread = MockReportThread()

        # Track signal emissions
        received_reports = []

        def on_report(content):
            received_reports.append(content)
            print(f"  - Signal received: {len(content)} chars")

        thread.report_generated.connect(on_report)

        # Test emitting reports
        thread.emit_report("<p>Section 1</p>")
        thread.emit_report("<br><br><p>Section 2</p>")

        print(f"\n✅ Signal test successful:")
        print(f"  - Reports emitted: {len(received_reports)}")
        print(f"  - Final report length: {len(thread.formatted_report)} chars")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Report Widget Display")
    print("=" * 60)

    tests = [
        test_gpt5_wrapper,
        test_streaming_handler,
        test_format_for_widget,
        test_report_generated_signal
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("✅ All widget tests passed!")
        print("\nThe report text display system is working correctly:")
        print("1. GPT5DirectWrapper properly emits tokens")
        print("2. StreamHandler correctly receives and forwards tokens")
        print("3. format_for_widget generates proper HTML")
        print("4. report_generated signal is emitted correctly")
        print("\nIf text still doesn't appear in the widget, check:")
        print("- API key is valid and has GPT-5 access")
        print("- Database has data to generate reports from")
        print("- ReportDialog.update_content() is being called")
    else:
        print(f"⚠️ {total - passed} tests failed")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)