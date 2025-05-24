export function constructFieldName(
  namePrefix: string | undefined,
  fieldName: string,
): string {
  if (!namePrefix) {
    return fieldName;
  }
  return `${namePrefix}${
    fieldName.charAt(0).toUpperCase() + fieldName.slice(1)
  }`;
}

export function constructFieldErrorName(
  fieldsPrefix: string | undefined,
  fieldName: string,
): string {
  if (!fieldsPrefix) {
    return `/${fieldName}`;
  }
  return `/${fieldsPrefix}_${fieldName}`;
}
