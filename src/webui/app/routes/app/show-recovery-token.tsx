import { Typography, styled } from "@mui/material";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import { useLoaderData } from "@remix-run/react";
import { useState } from "react";
import { z } from "zod";
import { parseQuery } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { CommunityLink } from "~/components/infra/community-link";
import { DocsHelp, DocsHelpSubject } from "~/components/infra/docs-help";
import { makeRootErrorBoundary } from "~/components/infra/error-boundary";
import { LifecyclePanel } from "~/components/infra/layout/lifecycle-panel";
import { StandaloneContainer } from "~/components/infra/layout/standalone-container";
import { SmartAppBar } from "~/components/infra/smart-appbar";
import { Logo } from "~/components/infra/logo";
import { Title } from "~/components/infra/title";
import { ActionsPosition, SectionCard } from "~/components/infra/section-card";
import {
  NavSingle,
  SectionActions,
  ActionsExpansion,
  ButtonSingle,
} from "~/components/infra/section-actions";
import { EMPTY_CONTEXT } from "~/top-level-context";

const QuerySchema = z.object({
  recoveryToken: z.string(),
});

// @secureFn
export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const response = await apiClient.loadTopLevelInfo.loadTopLevelInfo({});

  if (!response.user || !response.workspace) {
    return redirect("/app/init");
  }

  const query = parseQuery(request, QuerySchema);

  return json({ recoveryToken: query.recoveryToken });
}

// @secureFn
export default function ShowRecoveryToken() {
  const { recoveryToken } = useLoaderData<typeof loader>();

  const [hasCopied, setHasCopied] = useState(false);

  async function copyToClipboard() {
    await navigator.clipboard.writeText(recoveryToken);
    setHasCopied(true);
  }

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
          title="Your Recovery Token"
          actionsPosition={ActionsPosition.BELOW}
          actions={
            <SectionActions
              id="recovery-token"
              topLevelInfo={EMPTY_CONTEXT}
              inputsEnabled={true}
              expansion={ActionsExpansion.ALWAYS_SHOW}
              actions={[
                ButtonSingle({
                  text: hasCopied ? "Copied" : "Copy",
                  onClick: copyToClipboard,
                  disabled: hasCopied,
                  highlight: true,
                }),
                NavSingle({
                  text: "To Workspace",
                  link: "/app/workspace",
                }),
              ]}
            />
          }
        >
          <Typography variant="body1">
            This is your recovery token! It is used to recover your account in
            the case you forget your password!{" "}
            <em>Store it in a safe place!</em>
          </Typography>
          <RecoveryTokenBox variant="body2">{recoveryToken}</RecoveryTokenBox>
        </SectionCard>
      </LifecyclePanel>
    </StandaloneContainer>
  );
}

export const ErrorBoundary = makeRootErrorBoundary({
  error: () => `There was an error creating the workspace! Please try again!`,
});

const RecoveryTokenBox = styled(Typography)(({ theme }) => ({
  marginTop: "1rem",
  padding: "0.5rem",
  textAlign: "center",
  fontSize: "1.2rem",
  borderRadius: "0.25rem",
  backgroundColor: theme.palette.success.dark,
  color: theme.palette.success.contrastText,
}));
