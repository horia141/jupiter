import { AppShell } from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  FormControl,
  InputAdornment,
  InputLabel,
  OutlinedInput,
  Stack,
  Typography,
} from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import { Link, useTransition } from "@remix-run/react";
import { useContext, useState } from "react";
import { CommunityLink } from "~/components/community-link";
import { DocsHelp, DocsHelpSubject } from "~/components/docs-help";
import { FieldError } from "~/components/infra/errors";
import { LifecyclePanel } from "~/components/infra/layout/lifecycle-panel";
import { StandaloneContainer } from "~/components/infra/layout/standalone-container";
import { SmartAppBar } from "~/components/infra/smart-appbar";
import { Logo } from "~/components/logo";
import { Title } from "~/components/title";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { GLOBAL_PROPERTIES } from "~/global-properties-server";
import { aFieldError } from "~/logic/action-result";
import { loadFrontDoorInfo } from "~/logic/frontdoor.server";

export async function loader({ request }: LoaderArgs) {
  const frontDoor = await loadFrontDoorInfo(
    GLOBAL_PROPERTIES.version,
    request.headers.get("Cookie"),
    request.headers.get("User-Agent")
  );

  if (frontDoor.appShell !== AppShell.DESKTOP_ELECTRON) {
    return redirect("/app/workspace");
  }

  return json({});
}

export default function PickServer() {
  const globalProperties = useContext(GlobalPropertiesContext);
  const transition = useTransition();

  const inputsEnabled = transition.state === "idle";

  const [serverUrl, setServerUrl] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  return (
    <StandaloneContainer>
      <SmartAppBar>
        <Logo />

        <Title />

        <CommunityLink />

        <DocsHelp size="medium" subject={DocsHelpSubject.ROOT} />
      </SmartAppBar>

      <LifecyclePanel>
        <Card>
          <CardHeader title="Pick Server" />
          <CardContent>
            <Stack spacing={2} useFlexGap>
              <FormControl fullWidth>
                <InputLabel id="server-url">Server URL</InputLabel>
                <OutlinedInput
                  label="Server URL"
                  name="serverUrl"
                  type="text"
                  readOnly={!inputsEnabled}
                  value={serverUrl}
                  onChange={(event) => setServerUrl(event.target.value)}
                  endAdornment={
                    <InputAdornment position="end">
                      <Button
                        variant="outlined"
                        disabled={!inputsEnabled}
                        onClick={() =>
                          setServerUrl(globalProperties.hostedGlobalDomain)
                        }
                      >
                        Use Global
                      </Button>
                    </InputAdornment>
                  }
                />

                <Typography variant="caption" sx={{ paddingTop: "1rem" }}>
                  Examples:
                  <ul>
                    <li>
                      <code>thrive-test.com</code> (assumes https)
                    </li>
                    <li>
                      <code>http://thrive-test.com</code>
                    </li>
                    <li>
                      <code>https://my-thrive-instance.io</code>
                    </li>
                    <li>
                      <code>http://32.18.23.128:10000</code>
                    </li>
                  </ul>
                  You can learn more about self-hosting in the docs:
                  <DocsHelp
                    size="small"
                    subject={DocsHelpSubject.SELF_HOSTING}
                  />
                  .
                </Typography>

                {errorMessage && (
                  <FieldError
                    actionResult={aFieldError("server_url", errorMessage)}
                    fieldName="server_url"
                  />
                )}
              </FormControl>
            </Stack>
          </CardContent>

          <CardActions>
            <ButtonGroup>
              <Button
                id="pick-server"
                variant="contained"
                disabled={!inputsEnabled}
                onClick={async () => {
                  const res = await window.pickServer.pickServer(serverUrl);
                  if (res.result === "error") {
                    setErrorMessage(res.errorMsg);
                  }
                }}
              >
                Pick Server
              </Button>
              <Button
                id="go-back"
                variant="outlined"
                component={Link}
                to="/app/workspace"
              >
                Go Back
              </Button>
            </ButtonGroup>
          </CardActions>
        </Card>
      </LifecyclePanel>
    </StandaloneContainer>
  );
}
