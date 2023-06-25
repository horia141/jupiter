import { create } from "zustand";

interface EntitiesInFlux {
  entities: Map<string, Set<string>>;
  isEntityInFlux: (entity_type: string, entity_id: string) => boolean;
  addEntityInFlux: (entity_type: string, entity_id: string) => void;
  removeEntityInFlux: (entity_type: string, entity_id: string) => void;
}

export const useEntitiesInFluxStore = create<EntitiesInFlux>()((set, get) => ({
  entities: new Map(),
  isEntityInFlux: (entity_type: string, entity_id: string) => {
    const entities = get().entities;
    if (!entities.has(entity_type)) {
      return false;
    }
    return entities.get(entity_type)?.has(entity_id) || false;
  },
  addEntityInFlux: (entity_type: string, entity_id: string) =>
    set((state) => {
      const newEntities = new Map();
      for (const keyAndValue of state.entities.entries()) {
        newEntities.set(keyAndValue[0], keyAndValue[1]);
      }
      if (newEntities.has(entity_type)) {
        newEntities.get(entity_type).add(entity_id);
      } else {
        newEntities.set(entity_type, new Set([entity_id]));
      }
      return { entities: newEntities };
    }),
  removeEntityInFlux: (entity_type: string, entity_id: string) =>
    set((state) => {
      const newEntities = new Map();
      for (const keyAndValue of state.entities.entries()) {
        newEntities.set(keyAndValue[0], keyAndValue[1]);
      }
      if (newEntities.has(entity_type)) {
        newEntities.get(entity_type).delete(entity_id);
      }
      return { entities: newEntities };
    }),
}));
