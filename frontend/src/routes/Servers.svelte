<script>
  import { onMount } from 'svelte';
  import { api } from '../lib/api.js';

  let servers = $state([]);
  let form = $state({
    name: '', host: '', port: 22, username: 'root',
    auth_kind: 'password', secret: '', jump_server_id: '',
  });
  let msg = $state('');

  async function refresh() { servers = await api.servers(); }
  onMount(refresh);

  async function add(e) {
    e.preventDefault();
    const body = { ...form, jump_server_id: form.jump_server_id || null };
    await api.addServer(body);
    form = { ...form, name: '', host: '', secret: '' };
    await refresh();
  }

  async function test(s) {
    const r = await api.testServer(s.id);
    msg = r.ok ? `${s.name}: agent ${r.agent_version}` : `${s.name}: ${r.error}`;
  }
</script>

<h1>Servers</h1>

<form onsubmit={add} class="card row">
  <input bind:value={form.name}     placeholder="name (e.g. main-serv1)" />
  <input bind:value={form.host}     placeholder="host / IP" />
  <input bind:value={form.port}     type="number" placeholder="22" />
  <input bind:value={form.username} placeholder="user" />
  <select bind:value={form.auth_kind}>
    <option value="password">password</option>
    <option value="key">private key</option>
  </select>
  <input bind:value={form.secret} type="password" placeholder="secret" />
  <select bind:value={form.jump_server_id}>
    <option value="">no jump host</option>
    {#each servers as s (s.id)}<option value={s.id}>{s.name}</option>{/each}
  </select>
  <button>Add</button>
</form>

{#if msg}<p class="muted">{msg}</p>{/if}

<table>
  <thead><tr><th>Name</th><th>Host</th><th>User</th><th>Jump</th><th></th></tr></thead>
  <tbody>
    {#each servers as s (s.id)}
      <tr>
        <td>{s.name}</td><td>{s.host}:{s.port}</td><td>{s.username}</td>
        <td>{servers.find(x => x.id === s.jump_server_id)?.name ?? '—'}</td>
        <td>
          <button onclick={() => test(s)}>Test</button>
          <button onclick={async () => { await api.delServer(s.id); refresh(); }}>Delete</button>
        </td>
      </tr>
    {/each}
  </tbody>
</table>