const puppeteer = require('puppeteer');

async function testFrontendBackend() {
    console.log('🚀 Starting E2E test of frontend and backend...');
    
    let browser;
    try {
        // Launch browser
        browser = await puppeteer.launch({
            headless: false, // Set to false to see the browser
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        const page = await browser.newPage();
        
        // Enable console logging
        page.on('console', (msg) => {
            console.log('🔍 Browser Console:', msg.text());
        });
        
        // Enable request/response logging
        page.on('request', (request) => {
            console.log('📤 Request:', request.method(), request.url());
        });
        
        page.on('response', (response) => {
            console.log('📥 Response:', response.status(), response.url());
        });
        
        // Enable error logging
        page.on('pageerror', (error) => {
            console.error('❌ Page Error:', error.message);
        });
        
        console.log('🌐 Navigating to chat page...');
        await page.goto('http://localhost:8001/chat', { 
            waitUntil: 'networkidle2',
            timeout: 10000
        });
        
        // Wait for the page to load
        await page.waitForSelector('#message-input', { timeout: 5000 });
        console.log('✅ Chat page loaded successfully');
        
        // Check connection status
        const connectionStatus = await page.evaluate(() => {
            const statusEl = document.getElementById('connection-status');
            const textEl = statusEl?.querySelector('span');
            return textEl?.textContent || 'Unknown';
        });
        
        console.log('🔌 Connection Status:', connectionStatus);
        
        // Check model status
        const modelStatus = await page.evaluate(() => {
            const modelEl = document.getElementById('model-status');
            return modelEl?.textContent || 'Unknown';
        });
        
        console.log('🤖 Model Status:', modelStatus);
        
        // Wait a bit for connection check
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Check connection status again
        const connectionStatusAfter = await page.evaluate(() => {
            const statusEl = document.getElementById('connection-status');
            const textEl = statusEl?.querySelector('span');
            return textEl?.textContent || 'Unknown';
        });
        
        console.log('🔌 Connection Status After Wait:', connectionStatusAfter);
        
        // Test sending a message
        console.log('💬 Testing message sending...');
        
        await page.type('#message-input', 'Hello, this is a test message from E2E test');
        await page.click('#send-button');
        
        // Wait for response
        console.log('⏳ Waiting for AI response...');
        
        // Wait for the typing indicator to appear and disappear
        try {
            await page.waitForSelector('[id^="typing-"]', { timeout: 5000 });
            console.log('✅ Typing indicator appeared');
            
            // Wait for typing indicator to disappear (response received)
            await page.waitForFunction(
                () => !document.querySelector('[id^="typing-"]'), 
                { timeout: 30000 }
            );
            console.log('✅ Response received');
            
            // Check if we got a response message
            const messageCount = await page.evaluate(() => {
                return document.querySelectorAll('.message-bubble').length;
            });
            
            console.log(`📨 Total messages on page: ${messageCount}`);
            
            if (messageCount >= 2) {
                console.log('✅ Test PASSED: Chat functionality working correctly');
            } else {
                console.log('❌ Test FAILED: Expected at least 2 messages (user + AI response)');
            }
            
        } catch (error) {
            console.error('❌ Error waiting for response:', error.message);
        }
        
        // Take a screenshot
        await page.screenshot({ path: 'chat-test-screenshot.png' });
        console.log('📸 Screenshot saved as chat-test-screenshot.png');
        
        // Keep browser open for 5 seconds to observe
        console.log('👀 Keeping browser open for observation...');
        await new Promise(resolve => setTimeout(resolve, 5000));
        
    } catch (error) {
        console.error('❌ E2E Test Error:', error);
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// Run the test
testFrontendBackend().catch(console.error);
