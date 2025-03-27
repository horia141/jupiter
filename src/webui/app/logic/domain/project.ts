import type { Project, ProjectSummary } from "@jupiter/webapi-client";

export function isRootProject(project: Project | ProjectSummary): boolean {
  return !project.parent_project_ref_id;
}

export function sortProjectsByTreeOrder(
  projects: (Project | ProjectSummary)[],
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
    const sortedChildren = sortProjectsByOrderWithinParent(
      currentProject,
      children,
    );
    stack.push(...sortedChildren);
  }

  return finalProjects;
}

function sortProjectsByOrderWithinParent(
  parent: Project | ProjectSummary,
  children: (Project | ProjectSummary)[],
): ProjectSummary[] {
  return [...children].sort((a, b) => {
    const first = parent.order_of_child_projects.findIndex(
      (x) => x === a.ref_id,
    );
    const second = parent.order_of_child_projects.findIndex(
      (x) => x === b.ref_id,
    );
    return second - first;
  });
}

export function computeProjectHierarchicalNameFromRoot(
  project: Project | ProjectSummary,
  allProjectsByRefId: Map<string, Project | ProjectSummary>,
): string {
  let name = project.name;
  let currentProject = project;
  while (currentProject.parent_project_ref_id) {
    const currentProjectTmp = allProjectsByRefId.get(
      currentProject.parent_project_ref_id,
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
  allProjectsByRefId: Map<string, Project | ProjectSummary>,
): number {
  let distance = 0;
  let currentProject = project;
  while (currentProject.parent_project_ref_id) {
    distance++;
    const currentProjectTmp = allProjectsByRefId.get(
      currentProject.parent_project_ref_id,
    );
    if (!currentProjectTmp) {
      throw new Error("Invariant violation");
    }
    currentProject = currentProjectTmp;
  }
  return distance;
}

export function shiftProjectUpInListOfChildren(
  project: Project | ProjectSummary,
  orderOfChildProjects: string[],
): string[] {
  const index = orderOfChildProjects.findIndex((x) => x === project.ref_id);
  if (index === -1) {
    throw new Error("Invariant violation");
  }
  if (index === 0) {
    return orderOfChildProjects;
  }
  const newOrderOfChildProjects = [...orderOfChildProjects];
  newOrderOfChildProjects[index] = orderOfChildProjects[index - 1];
  newOrderOfChildProjects[index - 1] = orderOfChildProjects[index];
  return newOrderOfChildProjects;
}

export function shiftProjectDownInListOfChildren(
  project: Project | ProjectSummary,
  orderOfChildProjects: string[],
): string[] {
  const index = orderOfChildProjects.findIndex((x) => x === project.ref_id);
  if (index === -1) {
    throw new Error("Invariant violation");
  }
  if (index === orderOfChildProjects.length - 1) {
    return orderOfChildProjects;
  }
  const newOrderOfChildProjects = [...orderOfChildProjects];
  newOrderOfChildProjects[index] = orderOfChildProjects[index + 1];
  newOrderOfChildProjects[index + 1] = orderOfChildProjects[index];
  return newOrderOfChildProjects;
}
