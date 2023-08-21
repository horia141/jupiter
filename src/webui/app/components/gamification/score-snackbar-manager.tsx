import { Alert, Snackbar } from "@mui/material";
import Cookies from "js-cookie";
import { useContext, useEffect, useState } from "react";
import { set } from "zod";
import { GlobalPropertiesContext } from "~/global-properties-client";

export function useScoreAction() {
    const [scoreAction, setScoreAction] = useState(undefined);

    const globalProperties = useContext(GlobalPropertiesContext);

    useEffect(() => {
        const interval = setInterval(() => {
            const scoreActionStr = Cookies.get(globalProperties.scoreActionCookieName);
            if (scoreActionStr === undefined) {
                setScoreAction(sc => {
                    if (sc !== undefined) {
                        return undefined;
                    } else {
                        return sc;
                    }
                })
            }
            const scoreAction = JSON.parse(atob(scoreActionStr));
            setScoreAction(sc => {
                if (sc === undefined && scoreAction !== undefined) {
                    return scoreAction;
                } else {
                    return sc;
                }
            });

        }, 250);

        return () => clearInterval(interval);
    }, []);

    return scoreAction;
}

export function ScoreSnackbarManager() {
    const [alertState, setAlertState] = useState(false);
    const [alertMessage, setAlertMessage] = useState("");

    const globalProperties = useContext(GlobalPropertiesContext);
    const scoreAction = useScoreAction();

    useEffect(() => {
        setAlertState(scoreAction !== undefined);
        setAlertMessage(scoreAction?.message);
    }, [scoreAction]);


    function clearMessage() {
        Cookies.remove(globalProperties.scoreActionCookieName);
        setAlertState(false);
        setAlertMessage("");
    }

    return (
    <Snackbar open={alertState} onClose={clearMessage} autoHideDuration={10000}>
      <Alert severity="success" sx={{ width: '100%' }}>
        {alertMessage}
      </Alert>
    </Snackbar>
    );
}