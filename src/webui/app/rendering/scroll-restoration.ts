export function saveScrollPosition(ref: HTMLElement, location: string) {
  window.sessionStorage.setItem(`scroll:${location}`, `${ref.scrollTop}`);
}

export function restoreScrollPosition(ref: HTMLElement, location: string) {
  ref.scrollTo(
    0,
    parseInt(window.sessionStorage.getItem(`scroll:${location}`) ?? "0")
  );
}
