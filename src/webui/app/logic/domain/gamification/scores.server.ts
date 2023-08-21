import { createCookie } from "@remix-run/node";
import { RecordScoreResult } from "jupiter-gen";
import { createTypedCookie } from "remix-utils";
import { GLOBAL_PROPERTIES } from "~/global-properties-server";

function formatScoreUpdate(result: RecordScoreResult): string {
    let resultStr = "";

    const pointsStr = Math.abs(result.latest_task_score) === 1 ? "point" : "points";

    if (result.latest_task_score > 0) {
        resultStr += `Congratulations! You scored ${result.latest_task_score} ${pointsStr}.`;
    } else {
        resultStr += `Ah snap! You scored ${result.latest_task_score} ${pointsStr}.`;
    }

    resultStr += ` Which brings your total for today to ${result.score_overview.daily_score} and for this week to ${result.score_overview.weekly_score}.`;

    return resultStr;
}

// TODO(horia141): use createdtypedcookie
// TODO(horia141): secrets!
const scoreActionCookie = createCookie(GLOBAL_PROPERTIES.scoreActionCookieName, {
    maxAge: 60 * 60 * 24 * 30, // 30 days
});

export async function saveScoreAction(result: RecordScoreResult) {
    return await scoreActionCookie.serialize({
        message: formatScoreUpdate(result),
    });
}