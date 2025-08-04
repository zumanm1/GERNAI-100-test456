#!/usr/bin/env node

/**
 * Puppeteer MCP (Model Context Protocol) Server
 * 
 * This server provides web testing capabilities via MCP protocol
 * Can be used with Warp terminal and other MCP-compatible tools
 */

const { PuppeteerMCPServer } = require('./puppeteer-test.js');

class PuppeteerMCPProtocolServer {
    constructor() {
        this.server = new PuppeteerMCPServer();
        this.capabilities = {
            name: 'puppeteer-testing',
            version: '1.0.0',
            description: 'Web application testing using Puppeteer',
            author: 'Network Automation Team',
            tools: [
                {
                    name: 'test_web_app',
                    description: 'Test frontend web application functionality',
                    parameters: {
                        type: 'object',
                        properties: {
                            url: {
                                type: 'string',
                                description: 'URL of the web application to test',
                                default: 'http://localhost:8001'
                            }
                        }
                    }
                },
                {
                    name: 'test_api',
                    description: 'Test backend API endpoints',
                    parameters: {
                        type: 'object',
                        properties: {
                            url: {
                                type: 'string',
                                description: 'Base URL of the API to test',
                                default: 'http://localhost:5000'
                            }
                        }
                    }
                },
                {
                    name: 'take_screenshot',
                    description: 'Take a screenshot of a web page',
                    parameters: {
                        type: 'object',
                        properties: {
                            url: {
                                type: 'string',
                                description: 'URL to take screenshot of',
                                default: 'http://localhost:8001'
                            },
                            filename: {
                                type: 'string',
                                description: 'Output filename for screenshot',
                                default: 'screenshot.png'
                            }
                        }
                    }
                },
                {
                    name: 'performance_test',
                    description: 'Run performance metrics on a web page',
                    parameters: {
                        type: 'object',
                        properties: {
                            url: {
                                type: 'string',
                                description: 'URL to test performance',
                                default: 'http://localhost:8001'
                            }
                        }
                    }
                },
                {
                    name: 'full_integration_test',
                    description: 'Run complete integration test suite',
                    parameters: {
                        type: 'object',
                        properties: {
                            frontend_url: {
                                type: 'string',
                                description: 'Frontend application URL',
                                default: 'http://localhost:8001'
                            },
                            backend_url: {
                                type: 'string',
                                description: 'Backend API URL',
                                default: 'http://localhost:5000'
                            }
                        }
                    }
                }
            ]
        };
    }

    async handleToolCall(toolName, parameters = {}) {
        try {
            switch (toolName) {
                case 'test_web_app':
                    const frontendResult = await this.server.handleRequest('test_frontend', {
                        url: parameters.url || 'http://localhost:8001'
                    });
                    return {
                        success: frontendResult,
                        message: frontendResult ? 'Frontend test passed' : 'Frontend test failed'
                    };

                case 'test_api':
                    const backendResult = await this.server.handleRequest('test_backend', {
                        url: parameters.url || 'http://localhost:5000'
                    });
                    return {
                        success: backendResult,
                        message: backendResult ? 'API test passed' : 'API test failed'
                    };

                case 'take_screenshot':
                    await this.server.handleRequest('screenshot', {
                        filename: parameters.filename || 'screenshot.png'
                    });
                    // Navigate to URL first if specified
                    if (parameters.url) {
                        await this.server.tester.page.goto(parameters.url, { waitUntil: 'networkidle0' });
                        await this.server.tester.takeScreenshot(parameters.filename || 'screenshot.png');
                    }
                    return {
                        success: true,
                        message: `Screenshot saved as ${parameters.filename || 'screenshot.png'}`,
                        filename: parameters.filename || 'screenshot.png'
                    };

                case 'performance_test':
                    const metrics = await this.server.handleRequest('performance', {
                        url: parameters.url || 'http://localhost:8001'
                    });
                    return {
                        success: true,
                        message: 'Performance test completed',
                        metrics: metrics
                    };

                case 'full_integration_test':
                    const results = await this.server.handleRequest('full_test', {
                        frontendUrl: parameters.frontend_url || 'http://localhost:8001',
                        backendUrl: parameters.backend_url || 'http://localhost:5000'
                    });
                    return {
                        success: results.frontend && results.backend,
                        message: 'Integration test completed',
                        results: results
                    };

                default:
                    throw new Error(`Unknown tool: ${toolName}`);
            }
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    async getCapabilities() {
        return this.capabilities;
    }

    async shutdown() {
        await this.server.shutdown();
    }
}

// CLI interface for standalone usage
async function runCLI() {
    const args = process.argv.slice(2);
    const command = args[0];
    const server = new PuppeteerMCPProtocolServer();

    console.log('🎭 Puppeteer MCP Server');
    console.log('========================');

    try {
        switch (command) {
            case 'capabilities':
                const caps = await server.getCapabilities();
                console.log(JSON.stringify(caps, null, 2));
                break;

            case 'test':
                const testResult = await server.handleToolCall('full_integration_test');
                console.log('Test Results:', testResult);
                break;

            case 'screenshot':
                const screenshotResult = await server.handleToolCall('take_screenshot', {
                    url: args[1] || 'http://localhost:8001',
                    filename: args[2] || 'mcp-screenshot.png'
                });
                console.log('Screenshot Result:', screenshotResult);
                break;

            case 'help':
            default:
                console.log('Available commands:');
                console.log('  capabilities  - Show MCP server capabilities');
                console.log('  test         - Run full integration test');
                console.log('  screenshot [url] [filename] - Take screenshot');
                console.log('  help         - Show this help');
                break;
        }
    } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
    } finally {
        await server.shutdown();
    }
}

// WebSocket server for MCP protocol (simplified)
function startMCPServer(port = 3001) {
    const server = new PuppeteerMCPProtocolServer();
    
    console.log(`🌐 Starting MCP Server on port ${port}`);
    console.log('MCP Server capabilities:');
    console.log('  - Web application testing');
    console.log('  - API endpoint testing');
    console.log('  - Screenshot capture');
    console.log('  - Performance metrics');
    console.log('  - Full integration testing');
    
    // In a real MCP implementation, you would set up WebSocket or HTTP server here
    // For now, we'll just show the capabilities
    server.getCapabilities().then(caps => {
        console.log('\\nServer Tools:');
        caps.tools.forEach(tool => {
            console.log(`  - ${tool.name}: ${tool.description}`);
        });
    });

    return server;
}

// Export for use as module
module.exports = { PuppeteerMCPProtocolServer };

// Main execution logic
if (require.main === module) {
    const command = process.argv[2];
    
    if (command === 'server') {
        startMCPServer();
    } else {
        runCLI();
    }
}
