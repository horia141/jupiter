import { PersonRelationship } from "jupiter-gen";

export function personRelationshipName(
  relationship: PersonRelationship
): string {
  switch (relationship) {
    case PersonRelationship.FAMILY:
      return "Family";
    case PersonRelationship.FRIEND:
      return "Friend";
    case PersonRelationship.ACQUAINTANCE:
      return "Acquaintance";
    case PersonRelationship.SCHOOL_BUDDY:
      return "School Buddy";
    case PersonRelationship.WORK_BUDDY:
      return "Work Buddy";
    case PersonRelationship.COLLEAGUE:
      return "Colleage";
    case PersonRelationship.OTHER:
      return "Other";
  }
}
