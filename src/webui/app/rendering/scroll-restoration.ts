import { RefObject, useEffect } from "react";

export function useScrollRestoration(containerRef: RefObject<HTMLDivElement>, location: string, isPresent: boolean) {

  function handleScroll(ref: HTMLDivElement, pathname: string) {
    if (!isPresent) {
      return;
    }
    window.sessionStorage.setItem(`scroll:${pathname}`, `${ref.scrollTop}`);
  }
  
    useEffect(() => {
        if (containerRef.current === null) {
          return;
        }
    
        if (!isPresent) {
          return;
        }
    
        function handleScrollSpecial() {
          handleScroll(
            containerRef.current!,
            location
          );
        }
    
        containerRef.current.scrollTo(
          0,
          parseInt(
            window.sessionStorage.getItem(
              `scroll:${location}`
            ) ?? "0"
          )
        );
        containerRef.current.addEventListener("scrollend", handleScrollSpecial);
    
        return () => {
          containerRef.current?.removeEventListener(
            "scrollend",
            handleScrollSpecial
          );
        };
      }, [containerRef, location]);
}