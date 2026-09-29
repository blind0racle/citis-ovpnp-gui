<script>
  import { onMount } from 'svelte';
  import { api } from '../lib/api.js';
  import { aliases } from '../lib/stores.js';

  let form = $state({ ip: '', alias: '', scope: 'global', notes: '' });

  onMount(async () => { aliases.set(await api.aliases()); });

  async function add(e) {
    e.preventDefault();
    await api.addAlias(form);
    aliases.set(await api.aliases());
    form = { ip: '', alias: '', scope: 'global', notes: '' };
  }

  async function del(id) {
    await api.delAlias(id);
    aliases.set(await api.aliases());
  }
</script>

<h1>Aliases</h1>
<p class="muted">Give IPs human names. Everywhere the app shows an IP, it shows the alias first.</p>

<form onsubmit={add} class="card row">
  <input bind:value={form.ip}    placeholder="10.20.30.57" />
  <input bind:value={form.alias} placeholder="main-serv1" />
  <input bind:value={form.notes} placeholder="notes (optional)" />
  <button>Add</button>
</form>

<table>
  <thead><tr><th>Alias</th><th>IP</th><th>Scope</th><th>Notes</th><th></th></tr></thead>
  <tbody>
    {#each $aliases as a (a.id)}
      <tr>
        <td><strong>{a.alias}</strong></td><td>{a.ip}</td><td>{a.scope}</td>
        <td>{a.notes ?? ''}</td>
        <td><button onclick={() => del(a.id)}>Delete</button></td>
      </tr>
    {/each}
  </tbody>
</table>