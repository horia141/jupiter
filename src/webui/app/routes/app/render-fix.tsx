import { Typography } from "@mui/material";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import { useLoaderData } from "@remix-run/react";
import { z } from "zod";
import { parseQuery } from "zodix";

import { CommunityLink } from "~/components/infra/community-link";
import { DocsHelp, DocsHelpSubject } from "~/components/infra/docs-help";
import { LifecyclePanel } from "~/components/infra/layout/lifecycle-panel";
import { StandaloneContainer } from "~/components/infra/layout/standalone-container";
import { SmartAppBar } from "~/components/infra/smart-appbar";
import { Logo } from "~/components/infra/logo";
import { Title } from "~/components/infra/title";
import { DisplayType } from "~/rendering/use-nested-entities";
import { ActionsPosition, SectionCard } from "~/components/infra/section-card";
import { NavSingle, SectionActions } from "~/components/infra/section-actions";
import { EMPTY_CONTEXT } from "~/top-level-context";

const QuerySchema = z.object({
  returnTo: z.string(),
});

export const handle = {
  displayType: DisplayType.ROOT,
};

export async function loader({ request }: LoaderFunctionArgs) {
  const params = parseQuery(request, QuerySchema);
  const returnTo = Buffer.from(params.returnTo, "base64").toString("utf-8");
  return json({
    returnTo: returnTo,
  });
}

export default function RenderFix() {
  const loaderData = useLoaderData<typeof loader>();

  return (
    <StandaloneContainer>
      <SmartAppBar>
        <Logo />

        <Title />

        <CommunityLink />

        <DocsHelp size="medium" subject={DocsHelpSubject.ROOT} />
      </SmartAppBar>

      <LifecyclePanel>
        <SectionCard
          title="Oops"
          actionsPosition={ActionsPosition.BELOW}
          actions={
            <SectionActions
              id="render-fix"
              topLevelInfo={EMPTY_CONTEXT}
              inputsEnabled={true}
              actions={[
                NavSingle({
                  text: "Return",
                  link: loaderData.returnTo,
                }),
              ]}
            />
          }
        >
          <Typography>
            There seems to have been some application error.
          </Typography>

          <Typography>
            We&apos;ve recovered. Press the button below to return!
          </Typography>
        </SectionCard>
      </LifecyclePanel>
    </StandaloneContainer>
  );
}
