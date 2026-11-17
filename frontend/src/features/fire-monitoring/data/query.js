import { writable } from 'svelte/store';

const loading = { status: 'loading' };

export function createQuery(load, { maxAge = 60_000, capacity = 24 } = {}) {
  const active = new Map();
  const cache = new Map();

  async function request(key, entry) {
    if (entry.controller) return;

    const controller = new AbortController();
    entry.controller = controller;
    entry.state.set(loading);
    try {
      const data = await load(key, controller.signal);
      if (controller.signal.aborted) return;

      const result = { status: 'ready', data };
      cache.set(key, { result, expiresAt: Date.now() + maxAge });
      if (cache.size > capacity) cache.delete(cache.keys().next().value);
      entry.state.set(result);
    } catch (error) {
      if (!controller.signal.aborted) entry.state.set({ status: 'error', error });
    } finally {
      entry.controller = undefined;
    }
  }

  return key => ({
    key,
    subscribe(run) {
      let entry = active.get(key);
      if (!entry) {
        const cached = cache.get(key);
        const result = cached?.expiresAt > Date.now() ? cached.result : loading;
        if (result === loading) cache.delete(key);

        entry = { state: writable(result), subscribers: 0 };
        active.set(key, entry);
        if (result === loading) void request(key, entry);
      }

      entry.subscribers++;
      const unsubscribe = entry.state.subscribe(run);
      return () => {
        unsubscribe();
        if (--entry.subscribers > 0) return;
        entry.controller?.abort();
        active.delete(key);
      };
    },
    refresh() {
      cache.delete(key);
      const entry = active.get(key);
      if (entry) void request(key, entry);
    },
  });
}
