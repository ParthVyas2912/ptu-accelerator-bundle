export function resolveSmokeTarget(args = [], envURL = '') {
  let target = envURL.trim();
  let help = false;
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (arg === '--help' || arg === '-h') help = true;
    else if (arg === '--local') target = '';
    else if (arg === '--url') {
      target = args[++index];
      if (!target || target.startsWith('--')) throw new Error('--url requires a base URL.');
    } else if (arg.startsWith('--url=')) {
      target = arg.slice(6);
      if (!target) throw new Error('--url requires a base URL.');
    } else throw new Error('Unknown argument. Use --url BASE_URL, --local or --help.');
  }
  if (help) return { help: true };
  if (!target) return { help: false, url: null };
  const url = new URL(target);
  const loopback = ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname);
  if (url.protocol !== 'https:' && !(url.protocol === 'http:' && loopback)) {
    throw new Error('Use HTTPS for a deployed target, or HTTP on loopback for a preview.');
  }
  if (url.username || url.password || url.search || url.hash || url.pathname !== '/') {
    throw new Error('Supply only the site origin: no credentials, query, fragment or subpath.');
  }
  return { help: false, url: url.origin };
}

export const smokeHelp = `Usage: npm run test:smoke -- [--url https://example.azurestaticapps.net/] [--local]

SITE_URL supplies the target when --url is absent. CLI options take precedence.
No target: test the existing local dist/ with an ephemeral loopback server.
URL supplied: test the deployed site directly; no local build/server is used.
No credentials, deployment token, API access or private-file reads are needed.
Results and screenshots: ignored test-results/smoke/{local,deployed}/.
Exit 0 means every check passed; nonzero means failed, unavailable or not deployed.`;
