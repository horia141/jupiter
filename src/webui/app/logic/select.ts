import type { EntityId } from "jupiter-gen";
import { z } from "zod";

export function selectZod<R extends string>(zodEntity: z.ZodType<R>) {
  // function isProperType(value: string[]): value is R[] {
  //   return z.array(zodEntity).safeParse(value).success;
  // }
  return z.union([
    z.undefined(),
    z
      .string()
      .length(0)
      .transform(() => undefined),
    z
      .string()
      .transform((value) => {
        if (value.trim() === "") {
          return undefined;
        }
        return value.split(",").map((item) => item.trim());
      })
      .refine((value) => {
        if (value === undefined) {
          return undefined;
        }
        return z.array(zodEntity).parse(value) as unknown as R[];
      }),
  ]);
}

export function fixSelectOutputToEnum<T extends string>(
  selectOutput: undefined | string | string[] | T | T[]
): T[] | undefined {
  if (selectOutput === undefined) {
    return undefined;
  }

  if (selectOutput === "") {
    return undefined;
  }

  if (!Array.isArray(selectOutput)) {
    return [selectOutput as T];
  }

  return selectOutput as T[];
}

export function fixSelectOutputEntityId(
  selectOutput: undefined | string | string[]
): EntityId[] | undefined {
  if (selectOutput === undefined) {
    return undefined;
  }

  if (selectOutput === "") {
    return undefined;
  }

  if (!Array.isArray(selectOutput)) {
    return [selectOutput];
  }

  return selectOutput;
}
