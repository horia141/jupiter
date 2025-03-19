interface PickServerResultOk {
  result: "ok";
}

interface PickServerResultError {
  result: "error";
  errorMsg: string;
}

type PickServerResult = PickServerResultOk | PickServerResultError;

declare global {
  interface Window {
    pickServer: {
      pickServer: (url: string) => Promise<PickServerResult>;
    };
  }
}

export {};
