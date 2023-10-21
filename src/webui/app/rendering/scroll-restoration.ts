export function saveScrollPosition(ref: HTMLDivElement, location: string) {
  window.sessionStorage.setItem(`scroll:${location}`, `${ref.scrollTop}`);
}

export function restoreScrollPosition(ref: HTMLDivElement, location: string) {
  ref.scrollTo(
    0,
    parseInt(window.sessionStorage.getItem(`scroll:${location}`) ?? "0")
  );
}
