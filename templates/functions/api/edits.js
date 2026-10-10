// Cloudflare Pages Function: cloud storage for in-page text edits.
// GET  /api/edits?page=slides|detail  → { items: { "group:index": "<html>" } }   (public)
// POST /api/edits?page=...            → 200 if the x-edit-password header is right
// PUT  /api/edits?page=...            → replace the stored edits (open to anyone)
//      body { items, build } — build = the page version the edits belong to
// Every PUT first copies the previous document into <page>:history (last 30) for rollback.
// Bindings: KV namespace EDITS, secret EDIT_PASSWORD (only used by POST now).

const PAGES = ['slides', 'detail'];
const MAX_BYTES = 400_000;
const HISTORY = 30;

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
  });

function pageOf(request) {
  const page = new URL(request.url).searchParams.get('page');
  return PAGES.includes(page) ? page : null;
}

function authorized(request, env) {
  const want = env.EDIT_PASSWORD || '';
  if (!want) return false;
  const enc = new TextEncoder();
  const a = enc.encode(request.headers.get('x-edit-password') || '');
  const b = enc.encode(want);
  return a.length === b.length && crypto.subtle.timingSafeEqual(a, b);
}

export async function onRequestGet({ request, env }) {
  const page = pageOf(request);
  if (!page) return json({ error: 'unknown page' }, 400);
  const stored = await env.EDITS.get(page);
  return json(stored ? JSON.parse(stored) : { items: {} });
}

export async function onRequestPost({ request, env }) {
  if (!pageOf(request)) return json({ error: 'unknown page' }, 400);
  return authorized(request, env) ? json({ ok: true }) : json({ error: 'wrong password' }, 401);
}

export async function onRequestPut({ request, env }) {
  const page = pageOf(request);
  if (!page) return json({ error: 'unknown page' }, 400);
  const text = await request.text();
  if (text.length > MAX_BYTES) return json({ error: 'too large' }, 413);

  let items, build;
  try {
    ({ items, build = '' } = JSON.parse(text));
  } catch {
    return json({ error: 'bad json' }, 400);
  }
  if (!items || typeof items !== 'object' || Array.isArray(items)) return json({ error: 'bad items' }, 400);
  for (const [k, v] of Object.entries(items)) {
    if (typeof v !== 'string' || !/^[\w-]+:\d+$/.test(k)) return json({ error: 'bad item' }, 400);
  }

  if (typeof build !== 'string' || !/^[\w-]{1,40}$/.test(build)) return json({ error: 'bad build' }, 400);

  const previous = await env.EDITS.get(page);
  if (previous) {
    const history = JSON.parse((await env.EDITS.get(page + ':history')) || '[]');
    history.unshift(JSON.parse(previous));
    await env.EDITS.put(page + ':history', JSON.stringify(history.slice(0, HISTORY)));
  }

  const savedAt = new Date().toISOString();
  await env.EDITS.put(page, JSON.stringify({ items, build, savedAt }));
  return json({ ok: true, savedAt });
}
