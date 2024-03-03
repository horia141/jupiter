import type { EmailTask, EntityName } from "jupiter-gen";

export function emailTaskNiceName(emailTask: EmailTask): EntityName {
  return `Respond to message from ${emailTask.from_name} <${emailTask.from_address}> about ${emailTask.subject}`;
}
