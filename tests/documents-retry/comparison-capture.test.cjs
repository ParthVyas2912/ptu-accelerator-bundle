const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const script = fs.readFileSync(path.join(__dirname, '../../scripts/documents-comparison14.cjs'), 'utf8');

async function run(mode, options = {}) {
  const blobs = new Map([['_dkm-evaluation/comparison14-capture-probe.json',
    JSON.stringify({synthetic_transport_only: true})]]);
  if (mode === 'probe') blobs.clear();
  if (options.locked) blobs.set('_dkm-evaluation/comparison14-attempt-lock.json', '{}');
  const files = new Map();
  const events = [];
  let applicationCalls = 0;
  let resolve;
  const done = new Promise(r => resolve = r);
  const context = {
    __filename: '/tmp/dkm14.cjs',
    process: {argv: ['node', '/tmp/dkm14.cjs', mode, 'kernel-memory'],
      env: {IDENTITY_ENDPOINT: 'http://identity.invalid', IDENTITY_HEADER: 'offline-fixture'}, exitCode: 0},
    Buffer, URL, AbortSignal,
    require(name) {
      if (name === 'crypto') return crypto;
      assert.equal(name, 'fs');
      return {writeFileSync: (p, v) => files.set(p, v), readFileSync: () => Buffer.from(script),
        existsSync: p => files.has(p)};
    },
    console: {log(value) { events.push('console'); resolve(JSON.parse(value)); }},
    async fetch(url, request = {}) {
      const u = new URL(String(url));
      if (u.hostname === 'identity.invalid')
        return new Response(JSON.stringify({access_token: 'offline-not-a-real-token'}));
      if (u.hostname === 'ca-dkm-api') {
        assert.equal(u.pathname, '/Documents/Ask');
        applicationCalls++;
        events.push('application');
        return new Response(JSON.stringify({text: 'Unicode \u2212 \u20ac \u2603', relevantSources: []}));
      }
      assert.equal(u.hostname, 'stdkmeval0911a.blob.core.windows.net');
      const key = u.pathname.replace('/kernel-memory/', '');
      if (request.method === 'PUT') {
        events.push('put:' + key);
        if (options.failResult && key.endsWith('-result.json')) return new Response('', {status: 500});
        if (blobs.has(key)) return new Response('', {status: 412});
        blobs.set(key, request.body);
        return new Response('', {status: 201});
      }
      events.push('get:' + key);
      return new Response(blobs.get(key) || '', {status: blobs.has(key) ? 200 : 404});
    }
  };
  vm.runInNewContext(script, context);
  const result = await done;
  return {result, blobs, files, events, applicationCalls};
}
test('Unicode probe round-trips through Blob before console, no inference', async () => {
  const r = await run('probe');
  assert.equal(r.applicationCalls, 0);
  assert.equal(r.result.value.text, 'minus \u2212 euro \u20ac snowman \u2603');
  assert.equal(r.result.proof.persisted, true);
  assert.equal(r.events.at(-1), 'console');
});
test('Full unmodified JSON is stored and read back before console', async () => {
  const r = await run('compare');
  assert.equal(r.applicationCalls, 1);
  const saved = JSON.parse(r.blobs.get('_dkm-evaluation/comparison14-result.json'));
  assert.equal(saved.body, r.result.value.body);
  assert.equal(JSON.parse(saved.body).text, 'Unicode \u2212 \u20ac \u2603');
  assert.equal(r.events.at(-2), 'get:_dkm-evaluation/comparison14-result.json');
  assert.equal(r.events.at(-1), 'console');
});
test('Existing immutable attempt lock prevents any repeat', async () => {
  const r = await run('compare', {locked: true});
  assert.equal(r.applicationCalls, 0);
  assert.match(r.result.error, /412/);
  assert.equal(r.result.value, undefined);
});
test('Blob failure never exports full response or repeats inference', async () => {
  const r = await run('compare', {failResult: true});
  assert.equal(r.applicationCalls, 1);
  assert.match(r.result.error, /500/);
  assert.equal(r.result.value, undefined);
  assert.ok(r.files.has('/tmp/dkm14-result.json'));
});
