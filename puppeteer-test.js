#!/usr/bin/env node

const puppeteer = require('puppeteer');

class WebAppTester {
    constructor() {
        this.browser = null;
        this.page = null;
    }

    async initialize() {
        console.log('🚀 Initializing Puppeteer...');
        this.browser = await puppeteer.launch({
            headless: true, // Change to false to see browser in action
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        this.page = await this.browser.newPage();
        await this.page.setViewport({ width: 1280, height: 720 });
        console.log('✅ Puppeteer initialized successfully');
    }

    async testFrontendApp(url = 'http://localhost:8001') {
        console.log(`\n🔍 Testing Frontend Application at ${url}`);
        
        try {
            // Navigate to the application
            await this.page.goto(url, { waitUntil: 'networkidle0' });
            
            // Get page title and URL
            const title = await this.page.title();
            const currentUrl = this.page.url();
            console.log(`📄 Page Title: ${title}`);
            console.log(`🔗 Current URL: ${currentUrl}`);
            
            // Check if dashboard is loaded (looking for dashboard-specific elements)
            const dashboardElements = await this.page.evaluate(() => {
                const elements = {
                    hasNavbar: !!document.querySelector('.navbar'),
                    hasDashboardTitle: !!document.querySelector('h1, h2')?.textContent?.includes('Dashboard'),
                    hasStatsCards: document.querySelectorAll('.card').length,
                    hasNavLinks: document.querySelectorAll('.nav-link').length
                };
                return elements;
            });
            
            console.log('🏠 Dashboard Elements Check:');
            console.log(`   ✅ Navbar: ${dashboardElements.hasNavbar}`);
            console.log(`   ✅ Dashboard Title: ${dashboardElements.hasDashboardTitle}`);
            console.log(`   📊 Stats Cards: ${dashboardElements.hasStatsCards}`);
            console.log(`   🔗 Navigation Links: ${dashboardElements.hasNavLinks}`);
            
            // Test navigation to different routes
            const routes = ['/dashboard', '/automation', '/operations', '/devices', '/chat', '/settings'];
            
            for (const route of routes) {
                try {
                    await this.page.goto(`${url}${route}`, { waitUntil: 'networkidle0' });
                    const routeTitle = await this.page.title();
                    console.log(`   ✅ Route ${route}: ${routeTitle}`);
                } catch (error) {
                    console.log(`   ❌ Route ${route}: Failed - ${error.message}`);
                }
            }
            
            return true;
        } catch (error) {
            console.error(`❌ Frontend test failed: ${error.message}`);
            return false;
        }
    }

    async testBackendAPI(baseUrl = 'http://localhost:5000') {
        console.log(`\n🔍 Testing Backend API at ${baseUrl}`);
        
        try {
            // Test health endpoint
            const healthResponse = await this.page.evaluate(async (url) => {
                const response = await fetch(`${url}/health`);
                return {
                    status: response.status,
                    data: await response.json()
                };
            }, baseUrl);
            
            console.log(`🏥 Health Check: ${healthResponse.status === 200 ? '✅' : '❌'}`);
            console.log(`   Status: ${healthResponse.data.status}`);
            console.log(`   Service: ${healthResponse.data.service}`);
            
            return healthResponse.status === 200;
        } catch (error) {
            console.error(`❌ Backend API test failed: ${error.message}`);
            return false;
        }
    }

    async takeScreenshot(filename = 'test-screenshot.png') {
        console.log(`\n📸 Taking screenshot: ${filename}`);
        await this.page.screenshot({ 
            path: filename, 
            fullPage: true 
        });
        console.log(`✅ Screenshot saved: ${filename}`);
    }

    async runPerformanceTest(url = 'http://localhost:8001') {
        console.log(`\n⚡ Running Performance Test on ${url}`);
        
        await this.page.goto(url, { waitUntil: 'networkidle0' });
        
        const metrics = await this.page.metrics();
        console.log('📊 Performance Metrics:');
        console.log(`   🕒 Script Duration: ${Math.round(metrics.ScriptDuration * 1000)}ms`);
        console.log(`   📜 Documents: ${metrics.Documents}`);
        console.log(`   🌐 Frames: ${metrics.Frames}`);
        console.log(`   📡 JS Event Listeners: ${metrics.JSEventListeners}`);
        
        return metrics;
    }

    async cleanup() {
        if (this.browser) {
            await this.browser.close();
            console.log('🧹 Browser closed successfully');
        }
    }
}

// MCP Server-like Interface
class PuppeteerMCPServer {
    constructor() {
        this.tester = new WebAppTester();
        this.initialized = false;
    }

    async initialize() {
        if (!this.initialized) {
            await this.tester.initialize();
            this.initialized = true;
        }
    }

    async handleRequest(command, params = {}) {
        await this.initialize();
        
        switch (command) {
            case 'test_frontend':
                return await this.tester.testFrontendApp(params.url);
            
            case 'test_backend':
                return await this.tester.testBackendAPI(params.url);
            
            case 'screenshot':
                await this.tester.takeScreenshot(params.filename);
                return { success: true, filename: params.filename };
            
            case 'performance':
                return await this.tester.runPerformanceTest(params.url);
            
            case 'full_test':
                const results = {
                    frontend: await this.tester.testFrontendApp(params.frontendUrl),
                    backend: await this.tester.testBackendAPI(params.backendUrl)
                };
                await this.tester.takeScreenshot('full-test-screenshot.png');
                return results;
            
            default:
                throw new Error(`Unknown command: ${command}`);
        }
    }

    async shutdown() {
        await this.tester.cleanup();
        this.initialized = false;
    }
}

// Main execution
async function main() {
    const args = process.argv.slice(2);
    const command = args[0] || 'full_test';
    
    console.log('🎭 Puppeteer Web Application Tester');
    console.log('=====================================');
    
    const server = new PuppeteerMCPServer();
    
    try {
        switch (command) {
            case 'frontend':
                await server.handleRequest('test_frontend', { url: 'http://localhost:8001' });
                break;
            
            case 'backend':
                await server.handleRequest('test_backend', { url: 'http://localhost:5000' });
                break;
            
            case 'screenshot':
                await server.handleRequest('screenshot', { filename: 'app-screenshot.png' });
                break;
            
            case 'performance':
                await server.handleRequest('performance', { url: 'http://localhost:8001' });
                break;
            
            case 'full_test':
            default:
                const results = await server.handleRequest('full_test', {
                    frontendUrl: 'http://localhost:8001',
                    backendUrl: 'http://localhost:5000'
                });
                console.log('\n📋 Test Results Summary:');
                console.log(`   Frontend: ${results.frontend ? '✅ PASS' : '❌ FAIL'}`);
                console.log(`   Backend: ${results.backend ? '✅ PASS' : '❌ FAIL'}`);
                break;
        }
    } catch (error) {
        console.error(`❌ Error: ${error.message}`);
        process.exit(1);
    } finally {
        await server.shutdown();
    }
    
    console.log('\n🎉 Test completed!');
}

// Export for use as module
module.exports = { WebAppTester, PuppeteerMCPServer };

// Run if called directly
if (require.main === module) {
    main().catch(console.error);
}
