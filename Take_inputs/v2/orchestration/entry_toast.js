import { resolveEntryCopy } from "./entry_copy.js";

export function showEntryToast(entryContext) {
  if (!entryContext?.last_seen) return;

  const { step, at } = entryContext.last_seen;
  const text = resolveEntryCopy(step);
  const date = new Date(at).toLocaleDateString();

  const toast = document.createElement("div");
  toast.className = "entry-toast";
  toast.innerText = `Resuming where you left off — ${text} (${date})`;

  document.body.appendChild(toast);

  setTimeout(() => toast.remove(), 5000);
}