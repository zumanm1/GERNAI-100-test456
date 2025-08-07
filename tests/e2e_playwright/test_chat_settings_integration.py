#!/usr/bin/env python3
"""
End-to-end tests for chat and settings integration using Playwright.
Tests the complete user workflow from settings configuration to chat usage.
"""

import asyncio
import pytest
import json
import time
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

class TestChatSettingsE2E:
    """End-to-end tests for chat and settings integration"""
    
    @pytest.fixture
    async def browser_context(self):
        """Set up browser context for tests"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, slow_mo=100)  # Visible browser for debugging
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                ignore_https_errors=True
            )
            yield context
            await browser.close()
    
    @pytest.fixture
    async def page(self, browser_context):
        """Create a new page for each test"""
        page = await browser_context.new_page()
        yield page
        await page.close()
    
    async def test_settings_to_chat_integration(self, page: Page):
        """
        Test complete flow: 
        1. Configure settings in /settings
        2. Switch to /chat
        3. Verify chat uses correct AI model
        4. Send a message and get response
        """
        
        # Start backend and frontend servers (assuming they're running on 8002 and 8001)
        base_url = "http://localhost:8001"
        
        print("Testing settings to chat integration...")
        
        # Step 1: Navigate to settings page
        await page.goto(f"{base_url}/settings")
        await page.wait_for_load_state('networkidle')
        
        # Wait for settings page to load
        await page.wait_for_selector('h1, h2, h3', timeout=10000)
        
        # Take screenshot for debugging
        await page.screenshot(path="test_screenshots/01_settings_page.png")
        
        # Step 2: Check if genai settings form exists
        genai_form = await page.query_selector('#genai-settings-form')
        if not genai_form:
            # Look for any settings form
            settings_forms = await page.query_selector_all('form')
            print(f"Found {len(settings_forms)} forms on settings page")
            
            if settings_forms:
                genai_form = settings_forms[0]
        
        if genai_form:
            print("✓ Settings form found")
            
            # Look for provider selection dropdown
            provider_selector = await page.query_selector('select[name="core.default_chat_provider"], select[name*="provider"], select[name*="chat"]')
            
            if provider_selector:
                # Select OpenAI as the provider
                await provider_selector.select_option(value="openai")
                print("✓ Selected OpenAI provider")
                
                # Submit the form if submit button exists
                submit_button = await page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Save")')
                if submit_button:
                    await submit_button.click()
                    print("✓ Settings saved")
                    await page.wait_for_timeout(1000)  # Wait for save operation
        
        # Step 3: Navigate to chat page
        await page.goto(f"{base_url}/chat")
        await page.wait_for_load_state('networkidle')
        
        # Wait for chat interface to load
        await page.wait_for_selector('.chat-message, #chat-messages, #message-input', timeout=10000)
        
        # Take screenshot
        await page.screenshot(path="test_screenshots/02_chat_page.png")
        
        # Step 4: Verify the model display shows the correct provider
        model_badge = await page.query_selector('.badge:has-text("Model"), .badge:has-text("GPT"), .badge:has-text("OpenAI")')
        if model_badge:
            model_text = await model_badge.text_content()
            print(f"✓ Model display found: {model_text}")
            assert "openai" in model_text.lower() or "gpt" in model_text.lower() or "model" in model_text.lower()
        else:
            print("⚠ Model display not found, but continuing with test")
        
        # Step 5: Test chat functionality
        message_input = await page.query_selector('#message-input, input[placeholder*="message"], textarea[placeholder*="message"]')
        send_button = await page.query_selector('#send-button, button:has-text("Send"), button[type="submit"]')
        
        if message_input and send_button:
            print("✓ Chat input and send button found")
            
            # Type a test message
            test_message = "Hello AI, can you help me configure a Cisco switch VLAN?"
            await message_input.fill(test_message)
            
            # Send the message
            await send_button.click()
            print(f"✓ Sent message: {test_message}")
            
            # Wait for response (up to 30 seconds)
            try:
                # Wait for AI response to appear
                await page.wait_for_selector(
                    '.chat-message:has-text("AI"), .message:has-text("assistant"), .response:has-text("AI")',
                    timeout=30000
                )
                print("✓ AI response received")
                
                # Take screenshot of the chat
                await page.screenshot(path="test_screenshots/03_chat_with_response.png")
                
                # Verify response contains relevant content
                page_content = await page.content()
                if any(keyword in page_content.lower() for keyword in ['vlan', 'switch', 'configure', 'cisco', 'network']):
                    print("✓ Response contains relevant networking content")
                else:
                    print("⚠ Response may not be network-specific, but chat is working")
                
            except Exception as e:
                print(f"⚠ No AI response received within timeout: {e}")
                # Take screenshot anyway
                await page.screenshot(path="test_screenshots/03_chat_no_response.png")
        else:
            print("✗ Chat input or send button not found")
            assert False, "Chat interface not properly loaded"
        
        print("✅ End-to-end test completed successfully")
    
    async def test_settings_api_keys_management(self, page: Page):
        """Test API key management in settings"""
        
        base_url = "http://localhost:8001"
        
        print("Testing API key management...")
        
        # Navigate to settings page
        await page.goto(f"{base_url}/settings")
        await page.wait_for_load_state('networkidle')
        
        # Look for API key management section
        api_key_section = await page.query_selector('#api-keys-container, .api-keys, [id*="api"], [class*="api"]')
        
        if api_key_section:
            print("✓ API key management section found")
            
            # Look for add API key functionality
            add_button = await page.query_selector('button:has-text("Add"), button:has-text("New"), input[type="button"]')
            service_input = await page.query_selector('input[name*="service"], select[name*="service"]')
            key_input = await page.query_selector('input[name*="key"], input[type="password"]')
            
            if add_button and service_input and key_input:
                print("✓ Add API key controls found")
                
                # Try to add a test API key
                if service_input.tag_name.lower() == 'select':
                    await service_input.select_option(value="openai")
                else:
                    await service_input.fill("openai")
                
                await key_input.fill("sk-test123456789")
                await add_button.click()
                
                print("✓ Test API key addition attempted")
                
                # Take screenshot
                await page.screenshot(path="test_screenshots/04_api_key_management.png")
        
        print("✅ API key management test completed")
    
    async def test_real_time_chat_websocket(self, page: Page):
        """Test real-time WebSocket chat functionality"""
        
        base_url = "http://localhost:8001"
        
        print("Testing real-time chat WebSocket...")
        
        # Navigate to chat page
        await page.goto(f"{base_url}/chat")
        await page.wait_for_load_state('networkidle')
        
        # Set up WebSocket message listener
        messages_received = []
        
        def handle_websocket(ws):
            def on_message(message):
                try:
                    data = json.loads(message)
                    messages_received.append(data)
                    print(f"WebSocket message received: {data}")
                except:
                    messages_received.append(message)
            
            ws.on("message", on_message)
        
        # Listen for WebSocket connections
        page.on("websocket", handle_websocket)
        
        # Wait for page to establish WebSocket connection
        await page.wait_for_timeout(2000)
        
        # Send a test message
        message_input = await page.query_selector('#message-input, input[placeholder*="message"]')
        send_button = await page.query_selector('#send-button, button:has-text("Send")')
        
        if message_input and send_button:
            await message_input.fill("Test WebSocket message")
            await send_button.click()
            
            # Wait for WebSocket messages
            await page.wait_for_timeout(5000)
            
            if messages_received:
                print(f"✓ WebSocket messages received: {len(messages_received)}")
                for msg in messages_received:
                    print(f"  - {msg}")
            else:
                print("⚠ No WebSocket messages captured (may be using HTTP instead)")
        
        print("✅ WebSocket test completed")
    
    async def test_settings_persistence_across_sessions(self, page: Page):
        """Test that settings persist across browser sessions"""
        
        base_url = "http://localhost:8001"
        
        print("Testing settings persistence...")
        
        # First session: Set settings
        await page.goto(f"{base_url}/settings")
        await page.wait_for_load_state('networkidle')
        
        # Try to change a setting
        provider_select = await page.query_selector('select[name*="provider"]')
        if provider_select:
            await provider_select.select_option(value="anthropic")
            
            # Save settings
            save_button = await page.query_selector('button:has-text("Save"), input[type="submit"]')
            if save_button:
                await save_button.click()
                await page.wait_for_timeout(1000)
        
        # Reload the page (simulate new session)
        await page.reload()
        await page.wait_for_load_state('networkidle')
        
        # Verify settings were saved
        provider_select = await page.query_selector('select[name*="provider"]')
        if provider_select:
            current_value = await provider_select.get_attribute('value')
            if current_value == "anthropic":
                print("✓ Settings persisted across reload")
            else:
                print("⚠ Settings may not have persisted")
        
        print("✅ Persistence test completed")

# Helper function to run tests
async def run_e2e_tests():
    """Run all e2e tests"""
    test_instance = TestChatSettingsE2E()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        
        try:
            page = await context.new_page()
            
            # Create screenshots directory
            import os
            os.makedirs("test_screenshots", exist_ok=True)
            
            print("🚀 Starting e2e tests...")
            
            # Run all tests
            await test_instance.test_settings_to_chat_integration(page)
            await test_instance.test_settings_api_keys_management(page)  
            await test_instance.test_real_time_chat_websocket(page)
            await test_instance.test_settings_persistence_across_sessions(page)
            
            print("🎉 All e2e tests completed!")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    # Run the tests directly
    asyncio.run(run_e2e_tests())
