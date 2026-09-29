<script>
  import { api } from '../lib/api.js';
  let { onDone } = $props();
  let pw = $state(''), remember = $state(true), err = $state('');

  async function submit(e) {
    e.preventDefault();
    try { await api.login(pw, remember); onDone(); }
    catch (e) { err = 'Wrong password'; }
  }
</script>

<form onsubmit={submit} class="card">
  <h2>Unlock</h2>
  <input type="password" bind:value={pw} placeholder="Master password" />
  <label><input type="checkbox" bind:checked={remember} /> Remember me for 30 days</label>
  <button>Unlock</button>
  {#if err}<p class="err">{err}</p>{/if}
</form>