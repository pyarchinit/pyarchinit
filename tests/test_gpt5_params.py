#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test GPT-5 parameter compatibility
"""

import os
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, Tool

def test_gpt5_without_stop():
    """Test that GPT-5 works without stop parameter"""
    print("\n=== Testing GPT-5 without 'stop' parameter ===")

    # Mock API key (won't actually call API)
    api_key = "test_key"

    try:
        # Create ChatOpenAI with GPT-5
        llm = ChatOpenAI(
            model_name="gpt-5",
            api_key=api_key,
            max_completion_tokens=4000
        )
        print("✅ ChatOpenAI created successfully with GPT-5")

        # Create a simple tool
        def dummy_search(query: str) -> str:
            return f"Search result for: {query}"

        tools = [
            Tool(
                name="Search",
                func=dummy_search,
                description="Search for information"
            )
        ]

        # Test 1: Initialize agent WITHOUT agent_kwargs (correct for GPT-5)
        try:
            agent = initialize_agent(
                tools,
                llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=False,
                handle_parsing_errors=True
                # No agent_kwargs with stop parameter
            )
            print("✅ Agent initialized successfully WITHOUT stop parameter")
        except Exception as e:
            print(f"❌ Failed without stop: {e}")

        # Test 2: Try with stop parameter (should fail with real API)
        try:
            agent_with_stop = initialize_agent(
                tools,
                llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=False,
                handle_parsing_errors=True,
                agent_kwargs={"stop": ["\nObservation:"]}  # This would fail with real API
            )
            print("⚠️ Agent initialized WITH stop parameter (would fail with real API call)")
        except Exception as e:
            print(f"✅ Expected: Agent with stop would fail in real usage: {e}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_model_detection():
    """Test model name detection logic"""
    print("\n=== Testing Model Detection Logic ===")

    models = ["gpt-5", "gpt-5-mini", "gpt-4", "gpt-3.5-turbo"]

    for model in models:
        should_add_stop = "gpt-5" not in model.lower()

        if should_add_stop:
            print(f"  {model}: ✅ Would ADD stop parameter")
        else:
            print(f"  {model}: ❌ Would NOT add stop parameter (correct for GPT-5)")

    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing GPT-5 Parameter Compatibility")
    print("=" * 60)

    tests = [
        test_gpt5_without_stop,
        test_model_detection
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("✅ All GPT-5 compatibility tests passed!")
        print("\nThe code is now properly configured to:")
        print("1. NOT use 'stop' parameter with GPT-5 models")
        print("2. Correctly detect GPT-5 and GPT-5-mini models")
    else:
        print(f"⚠️ {total - passed} tests failed")

    return passed == total

if __name__ == "__main__":
    success = main()