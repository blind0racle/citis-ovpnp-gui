<script>
  import { onMount, onDestroy } from 'svelte';
  import { Terminal } from '@xterm/xterm';
  import { FitAddon } from '@xterm/addon-fit';
  import '@xterm/xterm/css/xterm.css';

  let { sid } = $props();
  let host;
  let term, fit, ws;

  onMount(() => {
    term = new Terminal({ fontFamily: 'monospace', fontSize: 13, theme: { background: '#0b0d10' } });
    fit = new FitAddon();
    term.loadAddon(fit);
    term.open(host);
    fit.fit();

    ws = new WebSocket(`ws://${location.host}/ws/term/${sid}`);
    ws.binaryType = 'arraybuffer';

    ws.onmessage = ev => {
      if (typeof ev.data === 'string') {
        const m = JSON.parse(ev.data);
        if (m.type === 'error') term.writeln(`\r\n[error] ${m.error}`);
      } else {
        term.write(new Uint8Array(ev.data));
      }
    };
    term.onData(d => ws.readyState === 1 && ws.send(JSON.stringify({ type: 'input', data: d })));

    const ro = new ResizeObserver(() => {
      fit.fit();
      if (ws.readyState === 1)
        ws.send(JSON.stringify({ type: 'resize', cols: term.cols, rows: term.rows }));
    });
    ro.observe(host);
    return () => ro.disconnect();
  });

  onDestroy(() => ws?.close());
</script>

<div class="termwrap" bind:this={host}></div>