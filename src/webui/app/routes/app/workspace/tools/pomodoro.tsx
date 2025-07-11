import { Button, CardContent, Typography, styled } from "@mui/material";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Duration } from "luxon";
import { useCallback, useContext, useEffect, useState } from "react";

import { ClientOnly } from "~/components/infra/client-only";
import { makeToolErrorBoundary } from "~/components/infra/error-boundary";
import { ToolPanel } from "~/components/infra/layout/tool-panel";
import {
  SectionActions,
  ButtonSingle,
} from "~/components/infra/section-actions";
import { SectionCard } from "~/components/infra/section-card";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { TopLevelInfoContext } from "~/top-level-context";
import { isDevelopment } from "~/logic/domain/env";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";

const DEFAULT_PROD_DURATION = Duration.fromMillis(1000 * 60 * 25);
const DEFAULT_DEV_DURATION = Duration.fromMillis(1000 * 4);
const DEFAULT_STEP_MS = 1000;

export const handle = {
  displayType: DisplayType.TOOL,
};

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Pomodoro() {
  const globalProperties = useContext(GlobalPropertiesContext);
  const actualDuration = isDevelopment(globalProperties.env)
    ? DEFAULT_DEV_DURATION
    : DEFAULT_PROD_DURATION;
  const topLevelInfo = useContext(TopLevelInfoContext);
  const [timerValue, setTimerValue] = useState(actualDuration);
  const [timerStarted, setTimerStarted] = useState(false);
  const [timerFinished, setTimerFinished] = useState(false);
  const [intervalHandle, setIntervalHandle] = useState<string | undefined>(
    undefined,
  );

  function startTimer() {
    setTimerStarted(true);
    setTimerFinished(false);
    const newIntervalHandle = setInterval(() => {
      setTimerValue((d) => {
        if (d.toMillis() > 0) {
          return d.minus(DEFAULT_STEP_MS);
        } else {
          return d;
        }
      });
    }, DEFAULT_STEP_MS);
    setIntervalHandle(newIntervalHandle as unknown as string);
  }

  function resetTimer() {
    setTimerStarted(false);
    setTimerFinished(false);
    setTimerValue(actualDuration);

    clearInterval(intervalHandle);
    setIntervalHandle(undefined);
  }

  const notifyToast = useCallback(() => {
    if (!("Notification" in window)) {
      return;
    }

    new Notification(`${globalProperties.title}} Pomodoro Timer`, {
      icon: "/favicon.ico",
      body: `Your ${actualDuration.toFormat(
        "m",
      )} minutes Pomodor interval is finished!`,
    });
  }, [actualDuration, globalProperties]);

  function notifyAudio() {
    const notificationAudio = new Audio("/pomodoro-notification.mp3");
    notificationAudio.play();
  }

  useEffect(() => {
    if (timerValue.toMillis() === 0) {
      setTimerFinished(true);
      clearInterval(intervalHandle);
      setIntervalHandle(undefined);
      setTimeout(notifyToast, 0);
      setTimeout(notifyAudio, 0);
    }
  }, [timerValue, intervalHandle, notifyToast]);

  return (
    <ToolPanel>
      <SectionCard
        title="Pomodoro Timer"
        actions={
          <SectionActions
            id="pomodoro-actions"
            topLevelInfo={topLevelInfo}
            inputsEnabled={true}
            actions={[
              ButtonSingle({
                text: "Start",
                highlight: true,
                disabled: timerStarted,
                onClick: () => startTimer(),
              }),
              ButtonSingle({
                text: "Reset",
                disabled: !timerStarted,
                onClick: () => resetTimer(),
              }),
            ]}
          />
        }
      >
        <PomodoroCard finished={timerFinished.toString()}>
          <Typography variant="h2">
            {timerValue.toFormat("mm'm'ss's'")}
          </Typography>
        </PomodoroCard>

        <ClientOnly fallback={<></>}>
          {() => "Notification" in window && <NotificationControl />}
        </ClientOnly>
      </SectionCard>
    </ToolPanel>
  );
}

export const ErrorBoundary = makeToolErrorBoundary(
  () => `There was an error with the pomodoro timing! Please try again!`,
);

interface PomodoroCardProps {
  finished: string;
}

const PomodoroCard = styled(CardContent)<PomodoroCardProps>(
  ({ theme, finished }) => ({
    backgroundColor:
      finished === "true"
        ? theme.palette.info.light
        : theme.palette.background.paper,
  }),
);

function NotificationControl() {
  const [permissionStatus, setPermissionStatus] = useState(
    Notification.permission,
  );

  function enableNotifications() {
    Notification.requestPermission().then((permission) => {
      setPermissionStatus(permission);
    });
  }

  if (permissionStatus === "default") {
    return (
      <Button onClick={enableNotifications} variant="text">
        Enable Notif.
      </Button>
    );
  } else if (permissionStatus === "denied") {
    return (
      <Button variant="text" disabled>
        Notif. Blocked
      </Button>
    );
  } else {
    return (
      <Button variant="text" disabled>
        Notif. Allowed
      </Button>
    );
  }
}
