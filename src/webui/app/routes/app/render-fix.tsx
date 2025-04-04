import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  Typography,
} from "@mui/material";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import { Link, useLoaderData } from "@remix-run/react";
import { z } from "zod";
import { parseQuery } from "zodix";

import { CommunityLink } from "~/components/community-link";
import { DocsHelp, DocsHelpSubject } from "~/components/docs-help";
import { LifecyclePanel } from "~/components/infra/layout/lifecycle-panel";
import { StandaloneContainer } from "~/components/infra/layout/standalone-container";
import { SmartAppBar } from "~/components/infra/smart-appbar";
import { Logo } from "~/components/logo";
import { Title } from "~/components/title";
import { DisplayType } from "~/rendering/use-nested-entities";

const QuerySchema = {
  returnTo: z.string(),
};

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
        <Card>
          <CardHeader title="Oops" />
          <CardContent>
            <Typography>
              There seems to have been some application error.
            </Typography>

            <Typography>
              We&apos;ve recovered. Press the button below to return!
            </Typography>
          </CardContent>
        </Card>

        <CardActions>
          <ButtonGroup>
            <Button
              variant="contained"
              to={loaderData.returnTo}
              component={Link}
            >
              Return
            </Button>
          </ButtonGroup>
        </CardActions>
      </LifecyclePanel>
    </StandaloneContainer>
  );
}
