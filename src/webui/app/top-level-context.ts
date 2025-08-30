import {
  ADate,
  type User,
  UserCategory,
  type UserFeatureFlagsControls,
  type UserScoreOverview,
  type Workspace,
  type WorkspaceFeatureFlagsControls,
} from "@jupiter/webapi-client";
import { createContext } from "react";

export interface TopLevelInfo {
  today: ADate;
  userFeatureFlagControls: UserFeatureFlagsControls;
  workspaceFeatureFlagControls: WorkspaceFeatureFlagsControls;
  user: User;
  userScoreOverview?: UserScoreOverview | null;
  workspace: Workspace;
}

export const EMPTY_CONTEXT = {
  today: "2025-01-01",
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
    category: UserCategory.STANDARD,
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
};

export const TopLevelInfoContext = createContext<TopLevelInfo>(EMPTY_CONTEXT);
