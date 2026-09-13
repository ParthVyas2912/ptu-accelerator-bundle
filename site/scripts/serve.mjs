import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

// Fixed routes only. Preview never serves sources, dependencies or parent files.
export async function startServer(port = 4173) {
  const root = new URL('../dist/', import.meta.url);
  const [html, config] = await Promise.all([
    readFile(new URL('index.html', root)),
    readFile(new URL('staticwebapp.config.json', root), 'utf8').then(JSON.parse),
  ]);
  const server = createServer((request, response) => {
    const pathname = new URL(request.url, 'http://localhost').pathname;
    for (const [name, value] of Object.entries(config.globalHeaders)) response.setHeader(name, value);
    if (pathname === '/favicon.ico') {
      response.writeHead(204);
      return response.end();
    }
    if ((request.method !== 'GET' && request.method !== 'HEAD') || !['/', '/index.html'].includes(pathname)) {
      response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      return response.end('Not found');
    }
    response.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    response.end(request.method === 'HEAD' ? undefined : html);
  });
  await new Promise((resolveStart, reject) => {
    server.once('error', reject);
    server.listen(port, '127.0.0.1', resolveStart);
  });
  return { server, url: `http://127.0.0.1:${server.address().port}` };
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  const { url } = await startServer(Number(process.env.PORT || 4173));
  console.log(`Local preview: ${url} (Ctrl+C to stop)`);
}
