/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserFeature } from './UserFeature';
import type { WidgetDimension } from './WidgetDimension';
import type { WorkspaceFeature } from './WorkspaceFeature';
/**
 * A constraints for a widget type.
 */
export type WidgetTypeConstraints = {
    allowed_dimensions: Record<string, Array<WidgetDimension>>;
    only_for_workspace_features?: (Array<WorkspaceFeature> | null);
    only_for_user_features?: (Array<UserFeature> | null);
};

