// Evaluation-only runner; original application routes and responses are unchanged.
const fs = require('fs');
const crypto = require('crypto');
const mode = process.argv[2];
const container = process.argv[3] || '';
const account = 'https://stdkmeval0911a.blob.core.windows.net';
const clientId = 'a8b91884-b691-4445-846d-e3642418e2a2';
const prefix = '_dkm-evaluation/comparison14';
const question = 'Compare the 2025 and 2026 Cedar Bay policies: annual training days in each, the increase in days and percent, and which policy supersedes which. Cite both source documents.';
const digest = value => crypto.createHash('sha256').update(value).digest('hex');
const ascii = value => JSON.stringify(value).replace(/[\u007f-\uffff]/g, c => '\\u' + c.charCodeAt(0).toString(16).padStart(4, '0'));
const emit = value => console.log(ascii(value));
let token;
async function storage(path, options = {}) {
  if (!token) {
    if (!process.env.IDENTITY_ENDPOINT || !process.env.IDENTITY_HEADER) throw Error('Managed identity endpoint unavailable');
    const u = new URL(process.env.IDENTITY_ENDPOINT);
    u.searchParams.set('api-version', '2019-08-01');
    u.searchParams.set('resource', 'https://storage.azure.com/');
    u.searchParams.set('client_id', clientId);
    const response = await fetch(u, {headers: {'X-IDENTITY-HEADER': process.env.IDENTITY_HEADER}, signal: AbortSignal.timeout(30000)});
    if (!response.ok) throw Error('Managed identity HTTP ' + response.status);
    token = (await response.json()).access_token;
    if (!token) throw Error('Managed identity returned no access token');
  }
  return fetch(account + path, {
    ...options, signal: AbortSignal.timeout(60000),
    headers: {'Authorization': 'Bearer ' + token, 'x-ms-version': '2023-11-03',
      'x-ms-date': new Date().toUTCString(), ...options.headers}
  });
}
function blobPath(suffix) {
  if (!/^[a-z0-9-]+$/.test(container)) throw Error('Explicit existing container required');
  return '/' + container + '/' + prefix + suffix;
}
async function persist(suffix, value) {
  const text = JSON.stringify(value);
  const r = await storage(blobPath(suffix), {method: 'PUT', headers: {
    'x-ms-blob-type': 'BlockBlob', 'Content-Type': 'application/json; charset=utf-8', 'If-None-Match': '*'
  }, body: text});
  if (r.status !== 201) throw Error('Evidence Blob PUT HTTP ' + r.status + '; no inference retry');
  const verify = await storage(blobPath(suffix));
  if (verify.status !== 200) throw Error('Evidence Blob readback HTTP ' + verify.status);
  const bytes = Buffer.from(await verify.arrayBuffer());
  if (digest(bytes) !== digest(text)) throw Error('Evidence Blob readback hash mismatch');
  return {url: account + blobPath(suffix), sha256: digest(bytes), bytes: bytes.length, persisted: true};
}
function unxml(s) {
  return s.replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&apos;/g, "'");
}
async function inventory() {
  const r = await storage('/?comp=list');
  if (!r.ok) throw Error('Container inventory HTTP ' + r.status);
  const xml = await r.text();
  if (/<NextMarker>[^<]+<\/NextMarker>/.test(xml)) throw Error('Container inventory requires pagination; absence not established');
  const containers = [...xml.matchAll(/<Container><Name>([^<]+)<\/Name>/g)].map(x => unxml(x[1]));
  const findings = [];
  for (const name of containers) {
    const list = await storage('/' + name + '?restype=container&comp=list&maxresults=1000');
    if (!list.ok) throw Error('Blob inventory HTTP ' + list.status);
    const body = await list.text();
    if (/<NextMarker>[^<]+<\/NextMarker>/.test(body)) throw Error('Blob inventory requires pagination; absence not established');
    const blobs = [...body.matchAll(/<Blob>([\s\S]*?)<\/Blob>/g)].map(x => ({
      name: unxml(x[1].match(/<Name>([^<]+)<\/Name>/)[1]),
      bytes: Number(x[1].match(/<Content-Length>(\d+)<\/Content-Length>/)?.[1] || 0)
    }));
    let inspected = 0;
    const matches = [];
    for (const blob of blobs) {
      if (blob.bytes > 65536 || !/\.(json|txt|md)$/i.test(blob.name) || /embedding/i.test(blob.name)) continue;
      const file = await storage('/' + name + '/' + blob.name.split('/').map(encodeURIComponent).join('/'));
      if (!file.ok) throw Error('Recovery candidate read HTTP ' + file.status);
      const text = await file.text();
      inspected++;
      if (text.includes(question)) matches.push({name: blob.name, bytes: Buffer.byteLength(text), sha256: digest(text)});
    }
    findings.push({container: name, blobs, inspected_small_text_json: inspected, exact_question_matches: matches});
  }
  return {case: 'recovery-inventory', utc: new Date().toISOString(), inference_calls: 0,
    containers: findings, runner_sha256: digest(fs.readFileSync(__filename)),
    local_result_file_exists: fs.existsSync('/tmp/dkm-qa-corpus-result.json')};
}
async function main() {
  if (mode === 'inventory') return emit(await inventory());
  if (mode === 'probe') {
    const value = {case: 'comparison14-capture-probe', synthetic_transport_only: true, inference_calls: 0,
      text: 'minus \u2212 euro \u20ac snowman \u2603', utc: new Date().toISOString()};
    const proof = await persist('-capture-probe.json', value);
    return emit({case: 'capture-probe', proof, value});
  }
  if (mode === 'read-result') {
    const response = await storage(blobPath('-result.json'));
    if (response.status !== 200) throw Error('Stored comparison response HTTP ' + response.status);
    const text = await response.text();
    return emit({case: 'stored-comparison', proof: {url: account + blobPath('-result.json'),
      sha256: digest(text), bytes: Buffer.byteLength(text), persisted: true}, value: JSON.parse(text)});
  }
  if (mode !== 'compare') throw Error('Unsupported evaluation mode');
  const probe = await storage(blobPath('-capture-probe.json'));
  if (probe.status !== 200 || !(await probe.json()).synthetic_transport_only) throw Error('Verified Blob capture probe required');
  // The immutable lock prevents rerunning inference even if the console disconnects.
  await persist('-attempt-lock.json', {case: 'comparison14', baseline: 12, cap: 14,
    maximum_provider_attempts: 2, sdk_retries: 0, automatic_retry: false, utc: new Date().toISOString()});
  const request = {question, documents: []};
  const started = Date.now();
  let value;
  try {
    const response = await fetch('http://ca-dkm-api/Documents/Ask', {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(request),
      signal: AbortSignal.timeout(180000)
    });
    value = {case: 'qa-corpus-approved14', request, status: response.status,
      body: await response.text(), ms: Date.now() - started, utc: new Date().toISOString()};
  } catch (error) {
    value = {case: 'qa-corpus-approved14', request, status: null,
      error: String(error), ms: Date.now() - started, utc: new Date().toISOString()};
  }
  fs.writeFileSync('/tmp/dkm14-result.json', JSON.stringify(value));
  const proof = await persist('-result.json', value);
  emit({case: 'comparison-completed', proof, value});
}
main().catch(error => { emit({case: mode, error: String(error), inference_repeated: false}); process.exitCode = 1; });
