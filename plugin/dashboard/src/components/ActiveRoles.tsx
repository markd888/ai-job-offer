import { Button, Group, Stack, Text, Textarea, UnstyledButton } from "@mantine/core";
import { IconChevronLeft, IconChevronRight, IconPencil } from "@tabler/icons-react";
import { useEffect, useRef, useState } from "react";

import { patchNextEvent } from "../api";
import { humanizeIsoDates, relativeDate } from "../dates";
import type { Position } from "../types";
import { OpenPostingIcon, QuickAddNote, lastActivity, tierRank } from "./ApplicationsTable";
import { useScrollEdges } from "../useScrollEdges";
import { TierBadge } from "./TierBadge";

interface Props {
  companies: Position[];
  onOpen: (p: Position) => void;
  onChange: () => void;
}

export function ActiveRoles({ companies, onOpen, onChange }: Props) {
  const active = companies
    .filter((p) => p.status === "interviewing" || p.status === "offer")
    .sort((a, b) => Number(b.status === "offer") - Number(a.status === "offer") || tierRank(a) - tierRank(b));

  const scroller = useRef<HTMLDivElement>(null);
  // Which sides still have cards out of view: drives the edge fades and arrows.
  const more = useScrollEdges(scroller, active.length);

  if (active.length === 0) return null;

  // Step to the next or previous card start. Card starts are also the snap
  // points, so every step lands in the same place whichever way you go.
  const step = (dir: 1 | -1) => {
    const el = scroller.current;
    if (!el) return;
    const left = el.getBoundingClientRect().left;
    const starts = Array.from(el.children).map((c) => c.getBoundingClientRect().left - left + el.scrollLeft);
    const now = el.scrollLeft;
    const target = dir === 1 ? starts.find((x) => x > now + 1) : starts.reverse().find((x) => x < now - 1);
    el.scrollTo({ left: target ?? (dir === 1 ? el.scrollWidth : 0), behavior: "smooth" });
  };

  return (
    <section aria-labelledby="active-h">
      <div className="jst-section-head">
        <span className="jst-dot jst-dot-ok" />
        <h2 id="active-h" className="jst-h2">In interviews</h2>
        <span className="jst-count">{active.length}</span>
        <span className="jst-spacer" />
        {(more.left || more.right) && (
          <>
            <button type="button" className="jst-icon-btn" onClick={() => step(-1)} disabled={!more.left} aria-label="Scroll to earlier interviews">
              <IconChevronLeft size={16} stroke={1.8} />
            </button>
            <button type="button" className="jst-icon-btn" onClick={() => step(1)} disabled={!more.right} aria-label="Scroll to more interviews">
              <IconChevronRight size={16} stroke={1.8} />
            </button>
          </>
        )}
      </div>
      <div className="jst-fade" data-more-left={more.left} data-more-right={more.right}>
        <div ref={scroller} className="jst-hscroll" role="list" aria-label="Active interviews, scroll sideways" tabIndex={0}>
          {active.map((p) => (
            <ActiveCard key={p.folder_path} p={p} onOpen={onOpen} onChange={onChange} />
          ))}
        </div>
      </div>
    </section>
  );
}

function NextStep({ p, steps, onSaved }: { p: Position; steps: string[]; onSaved: () => void }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  // Set when the editor closes, so focus goes back to the Next step button
  // instead of dropping to the page.
  const refocus = useRef(false);

  const close = () => {
    refocus.current = true;
    setEditing(false);
  };

  useEffect(() => {
    if (editing || !refocus.current) return;
    refocus.current = false;
    buttonRef.current?.focus();
  }, [editing]);

  const start = () => {
    // Edit the raw stored steps, one per line (the card shows them humanized).
    setDraft((p.next_event ?? "").split(";").map((s) => s.trim()).filter(Boolean).join("\n"));
    setError(null);
    setEditing(true);
  };

  useEffect(() => {
    if (!editing) return;
    const t = setTimeout(() => {
      const el = textareaRef.current;
      if (el) {
        el.focus();
        el.setSelectionRange(el.value.length, el.value.length);
      }
    }, 0);
    return () => clearTimeout(t);
  }, [editing]);

  const save = async () => {
    if (saving) return;
    setSaving(true);
    setError(null);
    try {
      await patchNextEvent(p.folder_path, draft);
      close();
      onSaved();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSaving(false);
    }
  };

  const label = <p className="jst-label">Next step</p>;

  if (editing) {
    return (
      <div className="jst-next">
        {label}
        <Stack gap={8}>
          <Textarea
            ref={textareaRef}
            autosize
            minRows={2}
            radius="md"
            placeholder="One step per line"
            value={draft}
            onChange={(e) => setDraft(e.currentTarget.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                void save();
              } else if (e.key === "Escape") {
                e.preventDefault();
                close();
              }
            }}
            aria-label={`Next step for ${p.company}`}
            disabled={saving}
          />
          {error && <Text size="xs" c="red">Couldn't save: {error}</Text>}
          <Group justify="space-between" gap={8}>
            <Text size="xs" c="dimmed">⌘↵ save · Esc cancel · empty clears</Text>
            <Group gap={8}>
              <Button size="xs" variant="subtle" color="gray" onClick={() => close()} disabled={saving}>Cancel</Button>
              <Button size="xs" onClick={() => void save()} loading={saving}>Save</Button>
            </Group>
          </Group>
        </Stack>
      </div>
    );
  }

  return (
    <UnstyledButton ref={buttonRef} onClick={start} aria-label={`Edit next step for ${p.company}`} className="jst-next jst-next-step">
      <span className="jst-next-pencil" aria-hidden>
        <IconPencil size={14} stroke={1.7} />
      </span>
      {label}
      <span>
        {steps.length > 0 ? (
          steps.map((s) => <p key={s} className="jst-next-line">{s}</p>)
        ) : (
          <p className="jst-next-line jst-next-empty">Not set — click to add one.</p>
        )}
      </span>
    </UnstyledButton>
  );
}

function ActiveCard({ p, onOpen, onChange }: { p: Position; onOpen: (p: Position) => void; onChange: () => void }) {
  const [noteOpen, setNoteOpen] = useState(false);
  const steps = p.next_event ? humanizeIsoDates(p.next_event).split(";").map((s) => s.trim()).filter(Boolean) : [];

  return (
    <article className="jst-card jst-hscroll-item jst-active-card" role="listitem">
      <div className="jst-active-head">
        <UnstyledButton onClick={() => onOpen(p)} className="jst-active-title" aria-label={`Open ${p.company}`}>
          <h3 className="jst-co">
            {p.company}
            {p.status === "offer" && <span className="jst-tag jst-tag-ok">Offer</span>}
          </h3>
          <p className="jst-role">{p.position}</p>
        </UnstyledButton>
        <TierBadge tier={p.tier} p={p} />
      </div>

      <NextStep p={p} steps={steps} onSaved={onChange} />

      <div className="jst-active-foot">
        <p className="jst-meta">
          Last touch <span className="jst-num">{relativeDate(lastActivity(p))}</span>
        </p>
        <div className="jst-actions">
          <OpenPostingIcon link={p.link} company={p.company} />
          <QuickAddNote folderPath={p.folder_path} company={p.company} opened={noteOpen} onChange={setNoteOpen} onAdded={onChange} />
        </div>
      </div>
    </article>
  );
}
