import { AppShell } from "@jupiter/webapi-client";
import {
  Button,
  FormControl,
  InputAdornment,
  InputLabel,
  OutlinedInput,
  Stack,
  Typography,
} from "@mui/material";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import { useNavigation } from "@remix-run/react";
import { useContext, useState } from "react";

import { CommunityLink } from "~/components/infra/community-link";
import { DocsHelp, DocsHelpSubject } from "~/components/infra/docs-help";
import { FieldError } from "~/components/infra/errors";
import { LifecyclePanel } from "~/components/infra/layout/lifecycle-panel";
import { StandaloneContainer } from "~/components/infra/layout/standalone-container";
import { SmartAppBar } from "~/components/infra/smart-appbar";
import { Logo } from "~/components/infra/logo";
import { Title } from "~/components/infra/title";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { GLOBAL_PROPERTIES } from "~/global-properties-server";
import { aFieldError } from "~/logic/action-result";
import { loadFrontDoorInfo } from "~/logic/frontdoor.server";
import { SectionCard, ActionsPosition } from "~/components/infra/section-card";
import {
  ButtonSingle,
  NavSingle,
  SectionActions,
  ActionsExpansion,
} from "~/components/infra/section-actions";
import { EMPTY_CONTEXT } from "~/top-level-context";

export async function loader({ request }: LoaderFunctionArgs) {
  const frontDoor = await loadFrontDoorInfo(
    GLOBAL_PROPERTIES.version,
    request.headers.get("Cookie"),
    request.headers.get("User-Agent"),
  );

  if (frontDoor.appShell !== AppShell.DESKTOP_ELECTRON) {
    return redirect("/app/workspace");
  }

  return json({});
}

export default function PickServer() {
  const globalProperties = useContext(GlobalPropertiesContext);
  const navigation = useNavigation();

  const inputsEnabled = navigation.state === "idle";

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
        <SectionCard
          title="Pick Server"
          actionsPosition={ActionsPosition.BELOW}
          actions={
            <SectionActions
              id="pick-server"
              topLevelInfo={EMPTY_CONTEXT}
              inputsEnabled={inputsEnabled}
              expansion={ActionsExpansion.ALWAYS_SHOW}
              actions={[
                ButtonSingle({
                  text: "Pick Server",
                  highlight: true,
                  onClick: async () => {
                    const res = await window.pickServer.pickServer(serverUrl);
                    if (res.result === "error") {
                      setErrorMessage(res.errorMsg);
                    }
                  },
                }),
                NavSingle({
                  text: "Go Back",
                  link: "/app/workspace",
                }),
              ]}
            />
          }
        >
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
                <DocsHelp size="small" subject={DocsHelpSubject.SELF_HOSTING} />
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
        </SectionCard>
      </LifecyclePanel>
    </StandaloneContainer>
  );
}
