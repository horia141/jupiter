import { Button, ButtonGroup, Card, CardActions, CardContent, CardHeader, Typography, styled } from "@mui/material";
import { Duration } from "luxon";
import { useEffect, useState } from "react";
import { ToolCard } from "~/components/infra/tool-card";
import { DisplayType } from "~/rendering/use-nested-entities";

const DEFAULT_DURATION = Duration.fromMillis(1000 * 4);
const DEFAULT_STEP_MS = 1000;

export const handle = {
  displayType: DisplayType.LEAF,
};

export default function Pomodoro() {
    const [timerValue, setTimerValue] = useState(DEFAULT_DURATION)
    const [timerStarted, setTimerStarted] = useState(false);
    const [timerFinished, setTimerFinished] = useState(false);
    const [intervalHandle, setIntervalHandle] = useState<string|undefined>(undefined);

    function startTimer() {
        setTimerStarted(true);
        setTimerFinished(false);
        const newIntervalHandle = setInterval(() => {
            setTimerValue(d => {
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
        setTimerValue(DEFAULT_DURATION);

        clearInterval(intervalHandle);
        setIntervalHandle(undefined);
    }

    function playNotification() {
        console.log(Notification.permission);
        Notification.requestPermission().then((perm) => {
            console.log(perm);
        });
        const x = new Notification("Hello", {icon: "/favicon.ico", body: "Hello"});
        const notificationAudio = new Audio("/pomodoro-notification.mp3");
        notificationAudio.play();
    }

    useEffect(() => {
        if (timerValue.toMillis() === 0) {
            setTimerFinished(true);
            clearInterval(intervalHandle);
            setIntervalHandle(undefined);
            setTimeout(playNotification, 0);
        }
    }, [timerValue, intervalHandle]);

    return (
        <ToolCard returnLocation="/workspace">
            <Card>
                <CardHeader title="Pomodoro Timer" />
                <PomodoroCard finished={timerFinished.toString()}>
                    <Typography variant="h2">{timerValue.toFormat("mm'm'ss's'")}</Typography>
                </PomodoroCard>

                <CardActions>
                    <ButtonGroup>
                        <Button
                            variant="contained"
                            onClick={() => startTimer()}
                            disabled={timerStarted}>
                                Start
                            </Button>
                            <Button
                                variant="outlined"
                                onClick={() => resetTimer()}
                                disabled={!timerStarted}>
                                    Reset
                                </Button>
                    </ButtonGroup>
                </CardActions>
            </Card>
        </ToolCard> 
    );
}

interface PomodoroCardProps {
    finished: string;
}

const PomodoroCard = styled(CardContent)<PomodoroCardProps>(({ theme, finished }) => ({
    backgroundColor: finished === "true" ? theme.palette.info.light : theme.palette.background.paper
}));