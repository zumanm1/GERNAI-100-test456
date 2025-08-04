#!/usr/bin/env node

const puppeteer = require('puppeteer');

class PageComparator {
    constructor() {
        this.browser = null;
        this.page = null;
    }

    async initialize() {
        console.log('🚀 Initializing Puppeteer for page comparison...');
        this.browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        this.page = await this.browser.newPage();
        await this.page.setViewport({ width: 1280, height: 720 });
        console.log('✅ Browser initialized');
    }

    async checkPage(url, expectedType) {
        console.log(`\n🔍 Checking ${expectedType} at ${url}`);
        
        try {
            const response = await this.page.goto(url, { 
                waitUntil: 'networkidle0',
                timeout: 10000 
            });
            
            const status = response.status();
            const title = await this.page.title();
            const contentType = response.headers()['content-type'] || 'unknown';
            
            console.log(`📄 Status: ${status}`);
            console.log(`📝 Title: "${title}"`);
            console.log(`📋 Content-Type: ${contentType}`);
            
            // Get page content analysis
            const pageInfo = await this.page.evaluate(() => {
                const body = document.body;
                const hasHTML = !!document.querySelector('html');
                const hasForm = !!document.querySelector('form');
                const hasNavigation = !!document.querySelector('nav, .navbar');
                const hasCards = document.querySelectorAll('.card, .card-body').length;
                const hasButtons = document.querySelectorAll('button, .btn').length;
                const textContent = body ? body.innerText.substring(0, 200) : '';
                const headings = Array.from(document.querySelectorAll('h1, h2, h3')).map(h => h.textContent.trim());
                
                return {
                    hasHTML,
                    hasForm,
                    hasNavigation,
                    hasCards,
                    hasButtons,
                    textContent,
                    headings,
                    bodyClasses: body ? body.className : '',
                    isJSON: textContent.trim().startsWith('{') && textContent.trim().endsWith('}')
                };
            });
            
            console.log(`🏗️  Structure Analysis:`);
            console.log(`   HTML Document: ${pageInfo.hasHTML}`);
            console.log(`   Has Navigation: ${pageInfo.hasNavigation}`);
            console.log(`   Has Forms: ${pageInfo.hasForm}`);
            console.log(`   Cards Found: ${pageInfo.hasCards}`);
            console.log(`   Buttons Found: ${pageInfo.hasButtons}`);
            console.log(`   Is JSON Response: ${pageInfo.isJSON}`);
            
            if (pageInfo.headings.length > 0) {
                console.log(`📑 Headings: ${pageInfo.headings.join(', ')}`);
            }
            
            if (pageInfo.textContent) {
                console.log(`📄 Content Preview: "${pageInfo.textContent.substring(0, 100)}..."`);
            }
            
            // Determine page type
            let actualType = 'unknown';
            if (contentType.includes('application/json') || pageInfo.textContent.trim().startsWith('{')) {
                actualType = 'api';
            } else if (pageInfo.hasNavigation && pageInfo.hasCards > 3) {
                actualType = 'dashboard';
            } else if (pageInfo.hasHTML && !pageInfo.textContent.trim().startsWith('{')) {
                actualType = 'web-app';
            }
            
            console.log(`🎯 Detected Type: ${actualType}`);
            console.log(`✅ Expected: ${expectedType}, Actual: ${actualType}`);
            
            return {
                url,
                status,
                title,
                contentType,
                expectedType,
                actualType,
                pageInfo,
                isCorrectType: actualType === expectedType || 
                             (expectedType === 'frontend' && actualType === 'dashboard') ||
                             (expectedType === 'backend' && actualType === 'api')
            };
            
        } catch (error) {
            console.error(`❌ Error checking ${url}: ${error.message}`);
            return {
                url,
                error: error.message,
                expectedType,
                actualType: 'error',
                isCorrectType: false
            };
        }
    }

    async comparePages() {
        console.log('🔄 Comparing Backend vs Frontend Pages');
        console.log('=====================================');
        
        const backendResult = await this.checkPage('http://localhost:5000', 'backend');
        const frontendResult = await this.checkPage('http://localhost:8001', 'frontend');
        
        console.log('\n📊 COMPARISON SUMMARY:');
        console.log('=====================');
        
        console.log(`\n🖥️  BACKEND (Port 5000):`);
        console.log(`   Status: ${backendResult.status || 'ERROR'}`);
        console.log(`   Type: ${backendResult.actualType}`);
        console.log(`   Title: ${backendResult.title || 'N/A'}`);
        console.log(`   Correct: ${backendResult.isCorrectType ? '✅' : '❌'}`);
        
        console.log(`\n🌐 FRONTEND (Port 8001):`);
        console.log(`   Status: ${frontendResult.status || 'ERROR'}`);
        console.log(`   Type: ${frontendResult.actualType}`);
        console.log(`   Title: ${frontendResult.title || 'N/A'}`);
        console.log(`   Correct: ${frontendResult.isCorrectType ? '✅' : '❌'}`);
        
        // Recommendations
        console.log('\n💡 RECOMMENDATIONS:');
        console.log('==================');
        
        if (!backendResult.isCorrectType) {
            console.log('🔧 Backend (Port 5000) should show:');
            console.log('   - API welcome message');
            console.log('   - JSON response format');
            console.log('   - Service information');
        }
        
        if (!frontendResult.isCorrectType) {
            console.log('🔧 Frontend (Port 8001) should show:');
            console.log('   - Web application interface');
            console.log('   - Welcome/landing page');
            console.log('   - Navigation elements');
        }
        
        return { backendResult, frontendResult };
    }

    async takeComparisonScreenshots() {
        console.log('\n📸 Taking comparison screenshots...');
        
        try {
            await this.page.goto('http://localhost:5000', { waitUntil: 'networkidle0' });
            await this.page.screenshot({ path: 'backend-port-5000.png', fullPage: true });
            console.log('✅ Backend screenshot saved: backend-port-5000.png');
            
            await this.page.goto('http://localhost:8001', { waitUntil: 'networkidle0' });
            await this.page.screenshot({ path: 'frontend-port-8001.png', fullPage: true });
            console.log('✅ Frontend screenshot saved: frontend-port-8001.png');
        } catch (error) {
            console.error('❌ Screenshot error:', error.message);
        }
    }

    async cleanup() {
        if (this.browser) {
            await this.browser.close();
            console.log('🧹 Browser closed');
        }
    }
}

async function main() {
    const comparator = new PageComparator();
    
    try {
        await comparator.initialize();
        const results = await comparator.comparePages();
        await comparator.takeComparisonScreenshots();
        
        console.log('\n🎉 Page comparison completed!');
        
        // Exit with appropriate code
        const success = results.backendResult.isCorrectType && results.frontendResult.isCorrectType;
        process.exit(success ? 0 : 1);
        
    } catch (error) {
        console.error('❌ Fatal error:', error.message);
        process.exit(1);
    } finally {
        await comparator.cleanup();
    }
}

if (require.main === module) {
    main();
}

module.exports = { PageComparator };
