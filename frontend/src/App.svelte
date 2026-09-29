<script>
  import { onMount } from 'svelte';
  import { route, authed } from './lib/stores.js';
  import { api } from './lib/api.js';

  import Setup from './routes/Setup.svelte';
  import Login from './routes/Login.svelte';
  import Dashboard from './routes/Dashboard.svelte';
  import Servers from './routes/Servers.svelte';
  import Aliases from './routes/Aliases.svelte';
  import Terminal from './routes/Terminal.svelte';

  let ready = $state(false);
  let initialised = $state(false);

  onMount(async () => {
    const s = await api.status();
    initialised = s.initialised;
    authed.set(s.unlocked);
    ready = true;
  });
</script>

{#if !ready}
  <p class="center">Loading…</p>
{:else if !initialised}
  <Setup onDone={() => { initialised = true; authed.set(true); }} />
{:else if !$authed}
  <Login onDone={() => authed.set(true)} />
{:else}
  <nav class="topbar">
    <a href="#/">Dashboard</a>
    <a href="#/servers">Servers</a>
    <a href="#/aliases">Aliases</a>
    <button onclick={async () => { await api.logout(); authed.set(false); }}>Logout</button>
  </nav>

  <main>
    {#if $route === '/'}            <Dashboard />
    {:else if $route === '/servers'} <Servers />
    {:else if $route === '/aliases'} <Aliases />
    {:else if $route.startsWith('/term/')}
      <Terminal sid={$route.slice('/term/'.length)} />
    {:else}                          <p>Not found</p>
    {/if}
  </main>
{/if}