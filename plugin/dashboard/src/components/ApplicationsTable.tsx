import {
  ActionIcon,
  Box,
  Button,
  Code,
  Group,
  Popover,
  Stack,
  Text,
  Textarea,
  TextInput,
  Tooltip,
  UnstyledButton,
} from "@mantine/core";
import { IconCheck, IconExternalLink, IconPencilPlus, IconSearch } from "@tabler/icons-react";
import { useEffect, useMemo, useRef, useState } from "react";

import { postNote } from "../api";
import { daysSince, relativeDate } from "../dates";
import type { Position } from "../types";
import { STATUS_KEYS, statusColor, statusLabel } from "../statusColors";
import { StatusSelect } from "./StatusSelect";
import { TierBadge, isScored } from "./TierBadge";

interface Props {
  companies: Position[];
  onChange: () => void;
  onOpen: (p: Position) => void;
}

// The tab shown first; falls back to the first non-empty group.
const DEFAULT_TAB = "new";
// Long groups (Rejected runs to hundreds) render this many rows until "Show all".
const PAGE_SIZE = 25;
// Applied roles with no activity for this long get a "Follow up" tag.
const FOLLOW_UP_DAYS = 7;

const TIER_FILTERS: Array<{ key: string; label: string }> = [
  { key: "all", label: "All tiers" },
  { key: "P0", label: "P0" },
  { key: "P1", label: "P1" },
  { key: "P2", label: "P2" },
  { key: "P3", label: "P3" },
  { key: "unscored", label: "Unscored" },
];

export function lastActivity(p: Position): string | undefined {
  return p.last_inbound ?? p.date_applied ?? p.date_added;
}

export function ApplicationsTable({ companies, onChange, onOpen }: Props) {
  const groups = useMemo(() => buildGroups(companies), [companies]);
  const [tab, setTab] = useState<string>(DEFAULT_TAB);
  const [tier, setTier] = useState("all");
  const [query, setQuery] = useState("");
  const [showAll, setShowAll] = useState(false);

  const current = groups.find((g) => g.key === tab) ?? groups.find((g) => g.key === DEFAULT_TAB) ?? groups[0];

  const tiersPresent = useMemo(() => {
    const present = new Set(companies.map((p) => (isScored(p.tier) ? p.tier : "unscored")));
    return TIER_FILTERS.filter((f) => f.key === "all" || present.has(f.key));
  }, [companies]);

  if (groups.length === 0) {
    return (
      <section className="jst-card" style={{ padding: 24 }}>
        <Stack gap="sm" align="flex-start">
          <Text fz="lg" fw={600}>No companies yet.</Text>
          <Text size="sm" c="dimmed">
            Run <Code>/job-offer:setup</Code> first, then add your first role with{" "}
            <Code>/job-offer:evaluate-position &lt;link&gt;</Code> in Claude Code.
          </Text>
          <Text size="sm" c="dimmed">
            Once positions land in <Code>userdata/companies/</Code>, they show up here automatically.
          </Text>
        </Stack>
      </section>
    );
  }

  const q = query.trim().toLowerCase();
  const filtered = current.rows.filter(
    (p) =>
      (tier === "all" || (tier === "unscored" ? !isScored(p.tier) : p.tier === tier)) &&
      (!q || p.company.toLowerCase().includes(q) || (p.position ?? "").toLowerCase().includes(q)),
  );
  const visible = showAll ? filtered : filtered.slice(0, PAGE_SIZE);

  return (
    <section id="pipeline" className="jst-card" aria-labelledby="pipeline-h" style={{ overflow: "hidden" }}>
      <Group justify="space-between" wrap="wrap" gap="sm" px={20} pt={20}>
        <h2 id="pipeline-h" className="jst-h2">Pipeline</h2>
        <TextInput
          aria-label="Search company or role"
          placeholder="Search company or role"
          leftSection={<IconSearch size={16} stroke={1.8} />}
          value={query}
          onChange={(e) => setQuery(e.currentTarget.value)}
          radius="md"
          className="jst-search"
        />
      </Group>

      <div
        role="tablist"
        aria-label="Pipeline stage"
        style={{ display: "flex", gap: 4, padding: "8px 12px 0", borderBottom: "1px solid var(--jst-border)", overflowX: "auto" }}
      >
        {groups.map((g) => (
          <button
            key={g.key}
            type="button"
            role="tab"
            aria-selected={g.key === current.key}
            className="jst-tab"
            onClick={() => {
              setTab(g.key);
              setShowAll(false);
            }}
          >
            <span className="jst-dot" style={{ backgroundColor: statusColor(g.key) }} />
            {g.label}
            <span className="jst-count">{g.rows.length}</span>
          </button>
        ))}
      </div>

      <Group gap={8} px={20} py={14}>
        {tiersPresent.map((f) => (
          <button
            key={f.key}
            type="button"
            className="jst-chip"
            aria-pressed={tier === f.key}
            onClick={() => setTier(f.key)}
          >
            {f.label}
          </button>
        ))}
      </Group>

      <div className="jst-row jst-row-head" role="presentation">
        <span>Tier</span>
        <span>Company &amp; role</span>
        <span className="jst-col-status">Status</span>
        <span>Last</span>
      </div>

      {visible.map((p) => (
        <PositionRow key={p.folder_path} p={p} onOpen={onOpen} onChange={onChange} />
      ))}

      {filtered.length === 0 && (
        <Text size="sm" c="dimmed" px={20} py={28} style={{ borderTop: "1px solid var(--jst-divider)" }}>
          No roles match these filters.
        </Text>
      )}

      <Group
        justify="space-between"
        px={20}
        py={12}
        style={{ borderTop: "1px solid var(--jst-divider)", background: "var(--jst-subtle)" }}
      >
        <Text size="sm" c="dimmed" className="jst-num">
          Showing {visible.length} of {filtered.length}
        </Text>
        {filtered.length > PAGE_SIZE && (
          <button type="button" className="jst-btn" onClick={() => setShowAll((v) => !v)}>
            {showAll ? "Show fewer" : "Show all"}
          </button>
        )}
      </Group>
    </section>
  );
}

interface PositionRowProps {
  p: Position;
  onOpen: (p: Position) => void;
  onChange: () => void;
}

function PositionRow({ p, onOpen, onChange }: PositionRowProps) {
  const [popoverOpen, setPopoverOpen] = useState(false);
  const last = lastActivity(p);
  const idle = daysSince(last);
  const needsFollowUp = p.status === "applied" && idle !== null && idle >= FOLLOW_UP_DAYS;

  return (
    <div className="jst-row" onClick={() => onOpen(p)}>
      <TierBadge tier={p.tier} />
      <Group gap="xs" align="center" wrap="nowrap" style={{ minWidth: 0 }}>
        <UnstyledButton
          onClick={(e) => {
            e.stopPropagation();
            onOpen(p);
          }}
          style={{ minWidth: 0, flex: "0 1 auto" }}
          aria-label={`Open ${p.company} — ${p.position || "pending"}`}
        >
          <p className="jst-co">
            {p.company}
            {needsFollowUp && <span className="jst-tag">Follow up</span>}
          </p>
          <p className="jst-role">{p.position || "(pending)"}</p>
        </UnstyledButton>
        <Box onClick={(e) => e.stopPropagation()} style={{ flexShrink: 0, lineHeight: 0, display: "flex", gap: 2 }}>
          <OpenPostingIcon link={p.link} company={p.company} />
          <QuickAddNote
            folderPath={p.folder_path}
            company={p.company}
            opened={popoverOpen}
            onChange={setPopoverOpen}
            onAdded={onChange}
          />
        </Box>
      </Group>
      <div className="jst-col-status" onClick={(e) => e.stopPropagation()}>
        <StatusSelect folderPath={p.folder_path} current={p.status} onChange={onChange} />
      </div>
      <span className={`jst-age jst-num${needsFollowUp ? " jst-age-stale" : ""}`}>{relativeDate(last)}</span>
    </div>
  );
}

interface OpenPostingIconProps {
  link: string | undefined;
  company: string;
}

export function OpenPostingIcon({ link, company }: OpenPostingIconProps) {
  if (!link) {
    // Reserve the slot so the pencil doesn't jump horizontally between rows.
    return <Box w={36} h={36} />;
  }
  return (
    <Tooltip label="Open posting" openDelay={400} withArrow>
      <ActionIcon
        component="a"
        href={link}
        target="_blank"
        rel="noopener noreferrer"
        size={36}
        variant="subtle"
        color="gray"
        radius="md"
        onClick={(e) => e.stopPropagation()}
        aria-label={`Open posting for ${company} in new tab`}
      >
        <IconExternalLink size={18} stroke={1.6} />
      </ActionIcon>
    </Tooltip>
  );
}

interface QuickAddNoteProps {
  folderPath: string;
  company: string;
  opened: boolean;
  onChange: (opened: boolean) => void;
  onAdded: () => void;
}

export function QuickAddNote({ folderPath, company, opened, onChange, onAdded }: QuickAddNoteProps) {
  const [note, setNote] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [savedFlash, setSavedFlash] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (opened) {
      // Defer focus a tick — Popover mounts the dropdown asynchronously.
      const t = setTimeout(() => textareaRef.current?.focus(), 0);
      return () => clearTimeout(t);
    }
    setNote("");
    setError(null);
  }, [opened]);

  const submit = async () => {
    if (!note.trim() || saving) return;
    setSaving(true);
    setError(null);
    try {
      await postNote(folderPath, note);
      setNote("");
      onChange(false);
      // Pencil morphs to a green check for ~900ms, then back.
      setSavedFlash(true);
      window.setTimeout(() => setSavedFlash(false), 900);
      onAdded();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Popover
      opened={opened}
      onChange={onChange}
      position="bottom-end"
      withArrow
      shadow="md"
      radius="md"
      width={320}
      trapFocus
    >
      <Popover.Target>
        <Tooltip label="Add a note" openDelay={400} withArrow disabled={opened || savedFlash}>
          <ActionIcon
            size={36}
            variant={savedFlash ? "light" : "subtle"}
            color={savedFlash ? "green" : "gray"}
            radius="md"
            onClick={(e) => {
              e.stopPropagation();
              if (savedFlash) return;
              onChange(!opened);
            }}
            aria-label={savedFlash ? "Saved" : `Add a note about ${company}`}
            style={{ transition: "background-color 200ms ease, color 200ms ease" }}
          >
            {savedFlash ? <IconCheck size={18} stroke={2} /> : <IconPencilPlus size={18} stroke={1.6} />}
          </ActionIcon>
        </Tooltip>
      </Popover.Target>
      <Popover.Dropdown onClick={(e) => e.stopPropagation()}>
        <Stack gap="xs">
          <Textarea
            ref={textareaRef}
            autosize
            minRows={3}
            radius="md"
            placeholder={`What's new with ${company}?`}
            value={note}
            onChange={(e) => setNote(e.currentTarget.value)}
            disabled={saving}
            onKeyDown={(e) => {
              if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
                e.preventDefault();
                void submit();
              } else if (e.key === "Escape") {
                e.preventDefault();
                onChange(false);
              }
            }}
          />
          {error && <Text size="xs" c="red">{error}</Text>}
          <Group justify="space-between" align="center">
            <Text size="xs" c="dimmed">⌘↵ to save · esc to cancel</Text>
            <Button size="xs" radius="md" loading={saving} onClick={submit} disabled={!note.trim()}>
              Add note
            </Button>
          </Group>
        </Stack>
      </Popover.Dropdown>
    </Popover>
  );
}

interface GroupBucket {
  key: string;
  label: string;
  rows: Position[];
}

function buildGroups(rows: Position[]): GroupBucket[] {
  const buckets = new Map<string, Position[]>();
  for (const row of rows) {
    const key = row.status || "—";
    if (!buckets.has(key)) buckets.set(key, []);
    buckets.get(key)!.push(row);
  }
  const ordered: GroupBucket[] = [];
  for (const key of STATUS_KEYS) {
    if (buckets.has(key)) {
      ordered.push({ key, label: statusLabel(key), rows: buckets.get(key)! });
      buckets.delete(key);
    }
  }
  for (const [key, value] of buckets.entries()) {
    ordered.push({ key, label: statusLabel(key), rows: value });
  }
  // Within each group: P0 first, then P1, P2, unscored; higher score first inside a tier.
  for (const g of ordered) {
    g.rows.sort((a, b) => tierRank(a) - tierRank(b) || (Number(b.score) || 0) - (Number(a.score) || 0));
  }
  return ordered;
}

export function tierRank(r: Position): number {
  return ({ P0: 0, P1: 1, P2: 2, P3: 3 } as Record<string, number>)[r.tier] ?? 4;
}
