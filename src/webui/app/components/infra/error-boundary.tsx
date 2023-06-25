import { Alert, AlertTitle, Box } from "@mui/material";
import { useContext } from "react";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { isDevelopment } from "~/logic/domain/env";

export function makeErrorBoundary(labelFn: () => string) {
  function ErrorBoundary({ error }: { error: Error }) {
    const globalProperties = useContext(GlobalPropertiesContext);

    return (
      <Alert severity="error">
        <AlertTitle>Danger</AlertTitle>
        {labelFn()}

        {isDevelopment(globalProperties.env) && (
          <Box>
            <pre>{error.message}</pre>
            <pre>{error.stack}</pre>
          </Box>
        )}
      </Alert>
    );
  }

  return ErrorBoundary;
}
