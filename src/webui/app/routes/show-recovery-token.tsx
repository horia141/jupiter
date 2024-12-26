import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  styled,
  Typography,
} from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import { Link, useLoaderData } from "@remix-run/react";
import { useContext, useState } from "react";
import { z } from "zod";
import { parseQuery } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { LifecyclePanel } from "~/components/infra/layout/lifecycle-panel";
import { StandaloneContainer } from "~/components/infra/layout/standalone-container";
import { SmartAppBar } from "~/components/infra/smart-appbar";
import { Logo } from "~/components/logo";
import { GlobalPropertiesContext } from "~/global-properties-client";

const QuerySchema = {
  recoveryToken: z.string(),
};

// @secureFn
export async function loader({ request }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const response = await apiClient.loadTopLevelInfo.loadTopLevelInfo({});

  if (!response.user || !response.workspace) {
    return redirect("/init");
  }

  const query = parseQuery(request, QuerySchema);

  return json({ recoveryToken: query.recoveryToken });
}

// @secureFn
export default function ShowRecoveryToken() {
  const { recoveryToken } = useLoaderData<typeof loader>();
  const globalProperties = useContext(GlobalPropertiesContext);

  const [hasCopied, setHasCopied] = useState(false);

  async function copyToClipboard() {
    await navigator.clipboard.writeText(recoveryToken);
    setHasCopied(true);
  }

  return (
    <StandaloneContainer>
      <SmartAppBar>
        <Logo />
        <Typography noWrap variant="h6" component="div">
          {globalProperties.title}
        </Typography>
      </SmartAppBar>

      <LifecyclePanel>
        <Card>
          <CardHeader title="Your Recovery Token" />
          <CardContent>
            <Typography variant="body1">
              This is your recovery token! It is used to recover your account in
              the case you forget your password!{" "}
              <em>Store it in a safe place!</em>
            </Typography>
            <RecoveryTokenBox variant="body2">{recoveryToken}</RecoveryTokenBox>
          </CardContent>

          <CardActions>
            <ButtonGroup>
              <Button variant="contained" to="/workspace" component={Link}>
                To Workspace
              </Button>
            </ButtonGroup>
            <ButtonGroup>
              <Button
                variant="contained"
                disabled={hasCopied}
                onClick={copyToClipboard}
              >
                {hasCopied ? "Copied" : "Copy"}
              </Button>
              <Button variant="outlined" disabled={true}>
                Save
              </Button>
            </ButtonGroup>
          </CardActions>
        </Card>
      </LifecyclePanel>
    </StandaloneContainer>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error creating the workspace! Please try again!`
);

const RecoveryTokenBox = styled(Typography)(({ theme }) => ({
  marginTop: "1rem",
  padding: "0.5rem",
  textAlign: "center",
  fontSize: "1.2rem",
  borderRadius: "0.25rem",
  backgroundColor: theme.palette.success.dark,
  color: theme.palette.success.contrastText,
}));
