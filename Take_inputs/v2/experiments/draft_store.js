const DraftStore = {
  key(experimentId) {
    return `draft:${experimentId}`;
  },

  load(experimentId) {
    const raw = localStorage.getItem(this.key(experimentId));  // ← CHANGED
    return raw ? JSON.parse(raw) : null;
  },

  save(experimentId, updater) {
    const prev = this.load(experimentId) || { experiment_id: experimentId };
    const next =
      typeof updater === "function" ? updater(prev) : updater;

    next.updated_at = new Date().toISOString();
    localStorage.setItem(this.key(experimentId), JSON.stringify(next));  // ← CHANGED
  },

  clearPhase(experimentId, phaseKey) {
    this.save(experimentId, d => {
      delete d[phaseKey];
      return d;
    });
  },

  clearAll(experimentId) {
    localStorage.removeItem(this.key(experimentId));  // ← CHANGED
  }
};

window.DraftStore = DraftStore;