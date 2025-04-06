import type { ADate, TimeInDay } from "@jupiter/webapi-client";
import { useSearchParams } from "@remix-run/react";
import { useEffect } from "react";

interface TimeEventParamsSourceParams {
  startDate: ADate;
  startTimeInDay: TimeInDay;
  durationMins: number;
}

export function TimeEventParamsSource(props: TimeEventParamsSourceParams) {
  const [searchParams, setSearchParms] = useSearchParams();

  useEffect(() => {
    const newSearchParams = new URLSearchParams(searchParams.toString());
    newSearchParams.set("sourceStartDate", props.startDate.toString());
    newSearchParams.set(
      "sourceStartTimeInDay",
      props.startTimeInDay.toString(),
    );
    newSearchParams.set("sourceDurationMins", props.durationMins.toString());
    setSearchParms(newSearchParams, {
      replace: true,
    });
  }, [
    searchParams,
    setSearchParms,
    props.startDate,
    props.startTimeInDay,
    props.durationMins,
  ]);

  useEffect(() => {
    return () => {
      const newSearchParams = new URLSearchParams(searchParams.toString());
      newSearchParams.delete("sourceStartDate");
      newSearchParams.delete("sourceStartTimeInDay");
      newSearchParams.delete("sourceDurationMins");
      setSearchParms(newSearchParams, {
        replace: true,
      });
    };
  }, [searchParams, setSearchParms]);

  return null;
}
