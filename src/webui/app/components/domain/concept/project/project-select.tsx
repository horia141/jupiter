import type { ProjectSummary } from "@jupiter/webapi-client";
import { Autocomplete, TextField } from "@mui/material";
import { useEffect, useMemo, useState } from "react";

import {
  computeProjectDistanceFromRoot,
  sortProjectsByTreeOrder,
} from "~/logic/domain/project";

interface ProjectSelectProps {
  name: string;
  label: string;
  inputsEnabled: boolean;
  disabled: boolean;
  allProjects: ProjectSummary[];
  defaultValue?: string;
  value?: string;
  onChange?: (value: string) => void;
}

export function ProjectSelect(props: ProjectSelectProps) {
  const rootProject = props.allProjects.find((p) => !p.parent_project_ref_id)!;
  const allProjectsByRefId = useMemo(
    () => new Map(props.allProjects.map((p) => [p.ref_id, p])),
    [props.allProjects],
  );
  const sortedProjects = sortProjectsByTreeOrder(props.allProjects);
  const allProjectsAsOptions = sortedProjects.map((project) => ({
    project_ref_id: project.ref_id,
    label: project.name,
    bigName: fullProjectName(project, allProjectsByRefId),
  }));

  function selectedProjectToOption() {
    const projectRefId =
      props.value || props.defaultValue || rootProject?.ref_id;
    const project = allProjectsByRefId.get(projectRefId)!;
    return {
      project_ref_id: projectRefId,
      label: project.name,
      bigName: fullProjectName(project, allProjectsByRefId),
    };
  }

  const [selectedProject, setSelectedProject] = useState(
    selectedProjectToOption(),
  );
  useEffect(() => {
    const projectRefId =
      props.value || props.defaultValue || rootProject?.ref_id;
    const project = allProjectsByRefId.get(projectRefId)!;
    setSelectedProject({
      project_ref_id: projectRefId,
      label: project.name,
      bigName: fullProjectName(project, allProjectsByRefId),
    });
  }, [
    props.value,
    props.defaultValue,
    props.allProjects,
    allProjectsByRefId,
    rootProject,
  ]);

  return (
    <>
      <Autocomplete
        disableClearable
        autoHighlight
        id={props.name}
        options={allProjectsAsOptions}
        readOnly={!props.inputsEnabled}
        disabled={props.disabled}
        value={selectedProject}
        onChange={(e, v) => {
          setSelectedProject(v);
          if (props.onChange) {
            props.onChange(v.project_ref_id);
          }
        }}
        isOptionEqualToValue={(o, v) => o.project_ref_id === v.project_ref_id}
        renderOption={(props, option) => {
          // eslint-disable-next-line react/prop-types
          const { key, ...restProps } = props;
          return (
            <li {...restProps} key={key}>
              {option.bigName}
            </li>
          );
        }}
        renderInput={(params) => <TextField {...params} label={props.label} />}
      />

      <input
        type="hidden"
        name={props.name}
        value={selectedProject.project_ref_id}
      />
    </>
  );
}

function fullProjectName(
  project: ProjectSummary,
  allProjectsByRefId: Map<string, ProjectSummary>,
): string {
  const indent = computeProjectDistanceFromRoot(project, allProjectsByRefId);
  return `${"-".repeat(indent)} ${project.name}`;
}
