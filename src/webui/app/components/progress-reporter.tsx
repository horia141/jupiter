import type { AuthTokenExt } from "@jupiter/webapi-client";
import CallToActionIcon from "@mui/icons-material/CallToAction";
import CloseIcon from "@mui/icons-material/Close";
import DeleteIcon from "@mui/icons-material/Delete";
import {
  Badge,
  ButtonGroup,
  Card,
  CardContent,
  CardHeader,
  IconButton,
  styled,
} from "@mui/material";
import { useContext, useEffect, useRef, useState } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { z } from "zod";

import { ClientOnly } from "~/components/infra/client-only";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { useBigScreen } from "~/rendering/use-big-screen";

enum LogMessageType {
  SECTION = "section",
  ENTITY_LINE = "entity-line",
}

interface LogMessage {
  id: number;
  type: LogMessageType;
  message: string[];
}

interface ProgressUpdateSection {
  type: "section";
  "section-name": string;
}

interface ProgressUpdateEntityLine {
  type: "enttiy-line";
  message: string;
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
type ProgressUpdate = ProgressUpdateSection | ProgressUpdateEntityLine;

const ProgressUpdateSchema = z.discriminatedUnion("type", [
  z.object({ type: z.literal("section"), "section-name": z.string() }),
  z.object({ type: z.literal("entity-line"), message: z.string() }),
]);

function debounceCallback(delay: number, callback: () => void) {
  let timeoutId: NodeJS.Timeout | null = null;
  return () => {
    if (timeoutId !== null) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => {
      timeoutId = null;
      callback();
    }, delay);
  };
}

interface ProgressReporterProps {
  token: AuthTokenExt;
}

export default function ProgressReporter(props: ProgressReporterProps) {
  return (
    <ClientOnly
      fallback={
        <IconButton size="large" color="inherit">
          <Badge badgeContent={0} color="error">
            <CallToActionIcon />
          </Badge>
        </IconButton>
      }
    >
      {() => <ProgressReporterClientOnly token={props.token} />}
    </ClientOnly>
  );
}

function ProgressReporterClientOnly(props: ProgressReporterProps) {
  const globalProperties = useContext(GlobalPropertiesContext);
  const isBigScreen = useBigScreen();
  const [showContainer, setShowContainer] = useState<boolean>(false);
  const [progressLog, setProgressLog] = useState<LogMessage[]>([]);
  const [unseenMessages, setUnseenMessages] = useState<number>(0);

  const webApiProgressReporterUrl = new URL(
    globalProperties.webApiProgressReporterUrl,
  );
  webApiProgressReporterUrl.searchParams.append("token", props.token);

  const { lastJsonMessage, readyState } = useWebSocket(
    webApiProgressReporterUrl.toString(),
  );

  useEffect(() => {
    if (lastJsonMessage === null) {
      return;
    }

    debounceCallback(500, () => {
      const progressUpdate = ProgressUpdateSchema.parse(lastJsonMessage);

      switch (progressUpdate.type) {
        case "section": {
          setProgressLog((progressLog) => [
            ...progressLog,
            {
              id: progressLog.length,
              type: LogMessageType.SECTION,
              message: [progressUpdate["section-name"]],
            },
          ]);
          break;
        }

        case "entity-line": {
          if (!showContainer) {
            setUnseenMessages((unseenMessages) => unseenMessages + 1);
          }
          setProgressLog((progressLog) => [
            ...progressLog,
            {
              id: progressLog.length,
              type: LogMessageType.ENTITY_LINE,
              message: [progressUpdate["message"]],
            },
          ]);
          break;
        }
      }
    })();
  }, [lastJsonMessage, showContainer]);

  function renderLogMessage(logMessage: LogMessage, idx: number) {
    switch (logMessage.type) {
      case LogMessageType.SECTION: {
        return (
          <div className="panel-block" key={idx}>
            Section: {logMessage.message[0]}
          </div>
        );
      }
      case LogMessageType.ENTITY_LINE: {
        return (
          <div className="panel-block" key={idx}>
            {logMessage.message[logMessage.message.length - 1]}
          </div>
        );
      }
    }
  }

  function handleShowContainer(event: React.MouseEvent<HTMLButtonElement>) {
    event.preventDefault();
    setShowContainer((showProgressReporter) => !showProgressReporter);
    setUnseenMessages(0);
  }

  function handleClear() {
    setProgressLog([]);
  }

  function handleClose() {
    setShowContainer(false);
  }

  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [progressLog]);

  const connectionStatus = {
    [ReadyState.CONNECTING]: "connecting",
    [ReadyState.OPEN]: "open",
    [ReadyState.CLOSING]: "closing",
    [ReadyState.CLOSED]: "closed",
    [ReadyState.UNINSTANTIATED]: "uninstantiated",
  }[readyState];

  return (
    <>
      <IconButton size="large" color="inherit" onClick={handleShowContainer}>
        <Badge badgeContent={unseenMessages} color="error">
          <CallToActionIcon />
        </Badge>
      </IconButton>
      {showContainer && (
        <Container>
          <Card>
            <CardHeader
              title={`Progress reporter is ${connectionStatus}`}
              action={
                <ButtonGroup
                  orientation={isBigScreen ? "horizontal" : "vertical"}
                >
                  <IconButton size="small" onClick={handleClear}>
                    <DeleteIcon />
                  </IconButton>
                  <IconButton size="small" onClick={handleClose}>
                    <CloseIcon />
                  </IconButton>
                </ButtonGroup>
              }
            />
            <ContainerLog>
              {progressLog.map(renderLogMessage)}
              <div ref={messagesEndRef} />
            </ContainerLog>
          </Card>
        </Container>
      )}
    </>
  );
}

const Container = styled("div")(({ theme }) => ({
  zIndex: theme.zIndex.appBar + 1,
  position: "fixed",
  bottom: "5vh",
  width: "75%",
  left: "50%",
  transform: "translateX(-50%)",
  margin: "auto",
  backgroundColor: theme.palette.background.paper,
}));

const ContainerLog = styled(CardContent)(() => ({
  overflowY: "scroll",
  scrollBehavior: "smooth",
  height: "7.5rem",
  overscrollBehaviorY: "contain",
  scrollSnapType: "y mandatory",
  "> div": {
    scrollSnapAlign: "end",
  },
}));
