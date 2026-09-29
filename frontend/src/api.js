async function req(path, opts = {}) {
  const r = await fetch(path, {
    credentials: 'include',
    headers: { 'content-type': 'application/json' },
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
  return r.status === 204 ? null : r.json();
}

export const api = {
  status:       () => req('/api/auth/status'),
  setup:        (password) => req('/api/auth/setup', { method: 'POST', body: { password } }),
  login:        (password, remember) => req('/api/auth/login', { method: 'POST', body: { password, remember } }),
  logout:       () => req('/api/auth/logout', { method: 'POST' }),

  servers:      () => req('/api/servers'),
  addServer:    (body) => req('/api/servers', { method: 'POST', body }),
  delServer:    (id) => req(`/api/servers/${id}`, { method: 'DELETE' }),
  testServer:   (id) => req(`/api/servers/${id}/test`, { method: 'POST' }),

  aliases:      () => req('/api/aliases'),
  addAlias:     (body) => req('/api/aliases', { method: 'POST', body }),
  delAlias:     (id) => req(`/api/aliases/${id}`, { method: 'DELETE' }),
};