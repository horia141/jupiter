declare global {
  interface Window {
    pickServer: {
      /** Opens the desktop shell's own server picker. */
      openPicker: () => Promise<void>;
    };
  }
}

export {};
