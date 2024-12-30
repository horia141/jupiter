export function saveScrollPosition(ref: HTMLElement, location: string) {
  window.sessionStorage.setItem(`scroll:${location}`, `${ref.scrollTop}`);
}

export function restoreScrollPosition(
  ref: HTMLElement,
  location: string,
) {
  // Regardless of what we do, we want to scroll to the leftmost part of the page.
  // Originating from work on calendars and the mobile views therein.
  ref.scrollTo(
    0,
    parseInt(window.sessionStorage.getItem(`scroll:${location}`) ?? "0")
  );
}
