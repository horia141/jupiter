import type {
  User,
  UserFeatureFlagsControls,
  UserScoreOverview,
  Workspace,
  WorkspaceFeatureFlagsControls,
} from "webapi-client";
import { createContext } from "react";

export interface TopLevelInfo {
  userFeatureFlagControls: UserFeatureFlagsControls;
  workspaceFeatureFlagControls: WorkspaceFeatureFlagsControls;
  user: User;
  userScoreOverview?: UserScoreOverview;
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
    ref_id: "bad",
    version: -1,
    archived: false,
    created_time: "0",
    last_modified_time: "0",
    archived_time: "0",
    email_address: "foo",
    name: "food",
    avatar: "this-is-not-a-data-url",
    timezone: "UTC",
    feature_flags: {},
  },
  userScoreOverview: undefined,
  workspace: {
    ref_id: "bad",
    version: -1,
    archived: false,
    created_time: "0",
    last_modified_time: "0",
    archived_time: "0",
    name: "food",
    feature_flags: {},
  },
});
