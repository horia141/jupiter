import { PropsWithChildren } from "react";
import { useBigScreen } from "~/rendering/use-big-screen";

interface NestingAwarePanelProps {
    showOutlet: boolean;
}

export function NestingAwarePanel(props: PropsWithChildren<NestingAwarePanelProps>) {
    const isBigScreen = useBigScreen();

    if (isBigScreen) {
        return <>{props.children}</>;
    } else {
        if (!props.showOutlet) {
            return <>{props.children}</>;
        } else {
            return null;
        }
    }
}