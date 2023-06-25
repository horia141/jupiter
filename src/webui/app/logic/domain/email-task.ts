import type { EmailTask, EntityName } from "jupiter-gen";

export function emailTaskNiceName(emailTask: EmailTask): EntityName {
  return {
    the_name: `Respond to message from ${emailTask.from_name.the_name} <${emailTask.from_address.the_address}> about ${emailTask.subject}`,
  };
}
