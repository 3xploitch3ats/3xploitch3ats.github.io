const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware pour ajouter les en-têtes CORS
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*'); // Autoriser toutes les origines
    res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    // Pour les requêtes OPTIONS (pré-vol), renvoyer une réponse vide avec le statut 204
    if (req.method === 'OPTIONS') {
        return res.sendStatus(204);
    }
    next();
});

// Middleware pour servir les fichiers statiques (HTML, CSS, JS)
app.use(express.static(path.join(__dirname, 'public')));

// Configuration du proxy pour rediriger les requêtes vers Pastebin
app.use('/api/pastebin', createProxyMiddleware({
    target: 'https://pastebin.com',
    changeOrigin: true,
    pathRewrite: {
        '^/api/pastebin': '', // Réécrire l'URL pour ne pas inclure /api/pastebin
    },
    onProxyReq: (proxyReq, req, res) => {
        console.log(`Proxied request: ${req.url}`);
    },
    onError: (err, req, res) => {
        console.error('Proxy error:', err);
        res.status(500).send('Proxy error');
    },
    onProxyRes: (proxyRes, req, res) => {
        if (proxyRes.statusCode !== 200) {
            console.log(`Proxy response status: ${proxyRes.statusCode}`);
        }
    }
}));

// Route pour servir le fichier HTML principal
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
