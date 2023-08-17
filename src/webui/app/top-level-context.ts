import {
  User,
  UserFeatureFlagsControls,
  Workspace,
  WorkspaceFeatureFlagsControls,
} from "jupiter-gen";
import { createContext } from "react";

export interface TopLevelInfo {
  userFeatureFlagControls: UserFeatureFlagsControls;
  workspaceFeatureFlagControls: WorkspaceFeatureFlagsControls;
  user: User;
  workspace: Workspace;
}

export const TopLevelInfoContext = createContext<TopLevelInfo>({
  userFeatureFlagControls: {
    controls: {},
  },
  workspaceFeatureFlagControls: {
    controls: {},
  },
  user: {
    ref_id: { the_id: "bad" },
    version: -1,
    archived: false,
    created_time: { the_ts: "0" },
    last_modified_time: { the_ts: "0" },
    archived_time: { the_ts: "0" },
    email_address: { the_address: "foo" },
    name: { the_name: "foo" },
    avatar: { avatar_as_data_url: "this-is-not-a-data-url" },
    timezone: { the_timezone: "UTC" },
    feature_flags: {},
  },
  workspace: {
    ref_id: { the_id: "bad" },
    version: -1,
    archived: false,
    created_time: { the_ts: "0" },
    last_modified_time: { the_ts: "0" },
    archived_time: { the_ts: "0" },
    name: { the_name: "Foo" },
    default_project_ref_id: { the_id: "bad" },
    feature_flags: {},
  },
});
