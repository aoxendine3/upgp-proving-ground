const http = require('http');

/**
 * XORAS SANDBOX: VULNERABLE STAGING TARGET [v1.0]
 * Intentionally flawed for integrity validation.
 */

const server = http.createServer((req, res) => {
    // 1. PERFORMANCE REGRESSION: Artificial Latency
    if (req.url === '/slow') {
        setTimeout(() => {
            res.writeHead(200, { 'Content-Type': 'text/plain' });
            res.end('Regression Active');
        }, 800); // 800ms delay
        return;
    }

    // 2. SECURITY GAP: Missing CSP and HSTS headers
    // 3. EXPOSED SECRET (SIMULATED):
    const MOCK_AWS_KEY = "AKIAIOSFODNN7EXAMPLE"; 

    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end(`Target Active. AWS_KEY: ${MOCK_AWS_KEY}`);
});

const PORT = 3001;
server.listen(PORT, () => {
    console.log(`[SANDBOX] Vulnerable target listening on port ${PORT}`);
});
