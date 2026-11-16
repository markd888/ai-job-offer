import { useEffect, useState, type RefObject } from "react";

export interface ScrollEdges {
  left: boolean;
  right: boolean;
}

// Width of the edge fade; --jst-fade-w in theme.css.
const FADE_PX = 48;

// Reports which sides of a sideways scroller still have content out of view.
// Drives the edge fades (and the arrows on the interview row), so a cut-off
// card or tab always reads as "there is more this way". Also keeps a focused
// child clear of the fades, so keyboard focus never lands half-hidden.
export function useScrollEdges(ref: RefObject<HTMLElement>, dep: unknown): ScrollEdges {
  const [edges, setEdges] = useState<ScrollEdges>({ left: false, right: false });

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const update = () => {
      const left = el.scrollLeft > 4;
      const right = el.scrollLeft + el.clientWidth < el.scrollWidth - 4;
      setEdges((e) => (e.left === left && e.right === right ? e : { left, right }));
    };

    const reveal = (e: FocusEvent) => {
      const target = e.target as HTMLElement | null;
      if (!target || target === el || el.scrollWidth <= el.clientWidth) return;
      const box = el.getBoundingClientRect();
      const r = target.getBoundingClientRect();
      if (r.left < box.left + FADE_PX) el.scrollLeft += r.left - box.left - FADE_PX;
      else if (r.right > box.right - FADE_PX) el.scrollLeft += r.right - box.right + FADE_PX;
    };

    update();
    el.addEventListener("scroll", update, { passive: true });
    el.addEventListener("focusin", reveal);
    // Watch the children too: a card or tab can change width (a count going
    // from 99 to 100) without the scroller itself resizing.
    const ro = new ResizeObserver(update);
    ro.observe(el);
    Array.from(el.children).forEach((c) => ro.observe(c));
    return () => {
      el.removeEventListener("scroll", update);
      el.removeEventListener("focusin", reveal);
      ro.disconnect();
    };
  }, [ref, dep]);

  return edges;
}
