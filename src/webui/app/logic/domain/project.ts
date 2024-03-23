import type { Project, ProjectSummary } from "jupiter-gen";

export function sortProjectsByTreeOrder(
  projects: (Project | ProjectSummary)[]
): ProjectSummary[] {
  // Essentially we do a DFS-ish traversal of the tree.
  const projectsByParentRefId: Map<
    string | null,
    (Project | ProjectSummary)[]
  > = new Map();
  for (const project of projects) {
    const parentRefId = project.parent_project_ref_id;
    if (!projectsByParentRefId.has(parentRefId || null)) {
      projectsByParentRefId.set(parentRefId || null, []);
    }
    const children = projectsByParentRefId.get(parentRefId || null);
    if (!children) {
      throw new Error("Invariant violation");
    }
    children.push(project);
  }

  const finalProjects: ProjectSummary[] = [];

  const stack: (Project | ProjectSummary)[] =
    projectsByParentRefId.get(null) || [];
  while (stack.length > 0) {
    const currentProject = stack.pop();
    if (currentProject === undefined) {
      throw new Error("Invariant violation");
    }
    finalProjects.push(currentProject);
    const children = projectsByParentRefId.get(currentProject.ref_id) || [];
    stack.push(...children);
  }

  return finalProjects;
}

export function computeProjectHierarchicalNameFromRoot(
  project: Project | ProjectSummary,
  allProjectsByRefId: Map<string, Project | ProjectSummary>
): string {
  let name = project.name;
  let currentProject = project;
  while (currentProject.parent_project_ref_id) {
    const currentProjectTmp = allProjectsByRefId.get(
      currentProject.parent_project_ref_id
    );
    if (!currentProjectTmp) {
      throw new Error("Invariant violation");
    }
    currentProject = currentProjectTmp;
    name = `${currentProject.name} / ${name}`;
  }
  return name;
}

export function computeProjectDistanceFromRoot(
  project: Project | ProjectSummary,
  allProjectsByRefId: Map<string, Project | ProjectSummary>
): number {
  let distance = 0;
  let currentProject = project;
  while (currentProject.parent_project_ref_id) {
    distance++;
    const currentProjectTmp = allProjectsByRefId.get(
      currentProject.parent_project_ref_id
    );
    if (!currentProjectTmp) {
      throw new Error("Invariant violation");
    }
    currentProject = currentProjectTmp;
  }
  return distance;
}
