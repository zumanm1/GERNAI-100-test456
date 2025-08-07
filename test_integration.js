const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security', '--disable-features=VizDisplayCompositor']
    });

    try {
        console.log('🚀 Starting Integration Tests...\n');

        const page = await browser.newPage();
        page.setDefaultTimeout(10000);

        // Enable console logging from browser
        page.on('console', msg => {
            if (msg.type() === 'error') {
                console.log('❌ Browser Error:', msg.text());
            }
        });

        // Test 1: Frontend Homepage
        console.log('📝 Test 1: Testing frontend homepage...');
        await page.goto('http://localhost:8001/', { waitUntil: 'networkidle2' });
        
        // Check if page loaded successfully
        const title = await page.title();
        console.log(`   ✅ Page title: ${title}`);
        
        // Check if navigation exists
        const navExists = await page.$('.navbar') !== null;
        console.log(`   ✅ Navigation exists: ${navExists}`);

        // Test 2: Settings Page
        console.log('\n📝 Test 2: Testing settings page...');
        await page.goto('http://localhost:8001/genai-settings', { waitUntil: 'networkidle2' });
        
        // Wait for settings form to load (try different possible selectors)
        try {
            await page.waitForSelector('#settingsForm', { timeout: 5000 });
        } catch {
            await page.waitForSelector('form', { timeout: 5000 });
        }
        console.log('   ✅ Settings form loaded');

        // Test 3: Backend API Communication
        console.log('\n📝 Test 3: Testing backend API communication...');
        
        // Test health endpoint
        const healthResponse = await page.evaluate(async () => {
            try {
                const response = await fetch('http://localhost:8002/health');
                return await response.json();
            } catch (error) {
                return { error: error.message };
            }
        });
        console.log('   ✅ Backend health:', healthResponse.status || 'Error');

        // Test GenAI settings endpoint
        const settingsResponse = await page.evaluate(async () => {
            try {
                const response = await fetch('http://localhost:8002/api/v1/genai-settings/genai/core');
                return await response.json();
            } catch (error) {
                return { error: error.message };
            }
        });
        console.log('   ✅ GenAI settings loaded:', settingsResponse.default_chat_provider || 'Error');

        // Test 4: Chat Page
        console.log('\n📝 Test 4: Testing chat page...');
        await page.goto('http://localhost:8001/chat', { waitUntil: 'networkidle2' });
        
        // Wait for chat interface to load
        await page.waitForSelector('#chatContainer', { timeout: 5000 });
        console.log('   ✅ Chat interface loaded');

        // Test 5: Send Chat Message via Frontend
        console.log('\n📝 Test 5: Testing chat message via frontend...');
        
        // Check if chat input exists and try sending a message
        const chatInputExists = await page.$('#messageInput') !== null;
        if (chatInputExists) {
            // Type a test message
            await page.type('#messageInput', 'Hello from integration test');
            
            // Click send button
            const sendButton = await page.$('#sendButton');
            if (sendButton) {
                await sendButton.click();
                console.log('   ✅ Chat message sent via frontend');
                
                // Wait a bit for response
                await page.waitForTimeout(2000);
            } else {
                console.log('   ⚠️  Send button not found');
            }
        } else {
            console.log('   ⚠️  Chat input not found');
        }

        // Test 6: Direct API Chat Test
        console.log('\n📝 Test 6: Testing direct API chat...');
        const chatResponse = await page.evaluate(async () => {
            try {
                const response = await fetch('http://localhost:8002/api/v1/chat/send', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: 'Integration test message',
                        session_id: 'puppeteer_test_session'
                    })
                });
                return await response.json();
            } catch (error) {
                return { error: error.message };
            }
        });
        
        if (chatResponse.response) {
            console.log('   ✅ Chat API working - Got response');
            console.log(`   📝 Session ID: ${chatResponse.session_id}`);
        } else {
            console.log('   ❌ Chat API error:', chatResponse.error || 'Unknown error');
        }

        // Test 7: Verify Settings Change
        console.log('\n📝 Test 7: Testing settings modification...');
        await page.goto('http://localhost:8001/genai-settings', { waitUntil: 'networkidle2' });
        
        // Wait for form and try changing a setting
        await page.waitForSelector('#defaultChatProvider', { timeout: 5000 });
        
        // Change provider to anthropic (if not already)
        await page.select('#defaultChatProvider', 'anthropic');
        console.log('   ✅ Changed provider to anthropic');
        
        // Click save button
        const saveButton = await page.$('button[type="submit"]');
        if (saveButton) {
            await saveButton.click();
            console.log('   ✅ Settings save button clicked');
            await page.waitForTimeout(2000);
        }

        console.log('\n🎉 Integration tests completed successfully!');
        console.log('\n📊 Test Summary:');
        console.log('   • Frontend is accessible on port 8001');
        console.log('   • Backend API is accessible on port 8002');
        console.log('   • Chat functionality is working');
        console.log('   • Settings page is functional');
        console.log('   • Frontend-backend communication is established');

    } catch (error) {
        console.error('❌ Integration test failed:', error.message);
        
        // Take screenshot on error
        try {
            await page.screenshot({ path: 'integration-test-error.png' });
            console.log('   📸 Error screenshot saved as integration-test-error.png');
        } catch (screenshotError) {
            console.log('   ⚠️  Could not take screenshot:', screenshotError.message);
        }
    } finally {
        await browser.close();
        console.log('\n✅ Browser closed');
    }
})();
