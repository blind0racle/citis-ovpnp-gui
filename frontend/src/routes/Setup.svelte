<script>
  import { api } from '../lib/api.js';
  let { onDone } = $props();
  let pw = $state(''), pw2 = $state(''), err = $state('');

  async function submit(e) {
    e.preventDefault();
    if (pw !== pw2) { err = 'Passwords do not match'; return; }
    try { await api.setup(pw); onDone(); }
    catch (e) { err = String(e); }
  }
</script>

<form onsubmit={submit} class="card">
  <h2>Create master password</h2>
  <p class="muted">This encrypts your server credentials. It is never stored.</p>
  <input type="password" bind:value={pw}  placeholder="Master password" />
  <input type="password" bind:value={pw2} placeholder="Confirm" />
  <button>Create</button>
  {#if err}<p class="err">{err}</p>{/if}
</form>