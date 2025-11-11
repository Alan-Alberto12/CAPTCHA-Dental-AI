// Step 1b — tiny mode registry (no backend)
import toothSelect from "./tooth-select/ToothSelectMode.js";

const registry = {
  "tooth-select": toothSelect,
};

export function getMode(id) {
  return registry[id];
}

export function listModes() {
  return Object.entries(registry).map(([id, m]) => ({ id, label: m.label }));
}
