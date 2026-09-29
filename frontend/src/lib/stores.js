import { writable } from 'svelte/store';

export const route = writable(window.location.hash.slice(1) || '/');
window.addEventListener('hashchange', () =>
  route.set(window.location.hash.slice(1) || '/'));

export const authed = writable(false);
export const aliases = writable([]);   // [{ip, alias}]

export function navigate(path) {
  window.location.hash = path;
}