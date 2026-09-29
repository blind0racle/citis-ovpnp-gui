<script>
  import { onMount } from 'svelte';
  import { api } from '../lib/api.js';
  import { aliases } from '../lib/stores.js';

  let servers = $state([]);
  let loaded = $state(false);

  onMount(async () => {
    aliases.set(await api.aliases());
    servers = await api.servers();
    loaded = true;
  });

  function nameFor(ip) {
    const hit = $aliases.find(a => a.ip === ip);
    return hit ? hit.alias : ip;
  }
</script>

<h1>Dashboard</h1>
{#if !loaded}<p>Loading…</p>{:else}
  <div class="grid">
    {#each servers as s (s.id)}
      <div class="card">
        <h3>{s.name}</h3>
        <p class="muted">{nameFor(s.host)}:{s.port} · {s.username}</p>
        <a href="#/term/{s.id}">Open terminal →</a>
      </div>
    {/each}
    {#if servers.length === 0}<p>No servers yet. <a href="#/servers">Add one</a>.</p>{/if}
  </div>
{/if}