import { HomeConfig, HomeTab, HomeTabTarget } from "@jupiter/webapi-client";

export function sortAndFilterTabsByTheirOrder(homeConfig: HomeConfig, target: HomeTabTarget, tabs: HomeTab[]): HomeTab[] {
  return tabs.filter((t) => t.target === target).sort((a, b) => {
    const aIndex = homeConfig.order_of_tabs[target].indexOf(a.ref_id);
    const bIndex = homeConfig.order_of_tabs[target].indexOf(b.ref_id);
    return aIndex - bIndex;
  });
}
