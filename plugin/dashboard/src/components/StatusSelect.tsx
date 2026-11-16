import { Group, Select, Text } from "@mantine/core";
import { useState } from "react";

import { patchStatus } from "../api";
import { STATUSES, statusColor } from "../statusColors";

const STATUS_OPTIONS = STATUSES.map((s) => ({ value: s.key, label: s.label }));

interface Props {
  folderPath: string;
  current: string;
  onChange: () => void;
}

// The colour comes from statusColors.ts, so it stays inline; size and shape are .jst-dot.
function StatusDot({ status }: { status: string }) {
  return <span className="jst-dot" style={{ backgroundColor: statusColor(status) }} aria-hidden />;
}

export function StatusSelect({ folderPath, current, onChange }: Props) {
  const [saving, setSaving] = useState(false);
  const [value, setValue] = useState(current);

  return (
    <Select
      size="xs"
      radius="md"
      aria-label="Status"
      classNames={{ input: "jst-status-input" }}
      data={STATUS_OPTIONS}
      value={value}
      disabled={saving}
      leftSection={<StatusDot status={value} />}
      leftSectionWidth={28}
      comboboxProps={{ width: "max-content", middlewares: { flip: true, shift: true } }}
      renderOption={({ option, checked }) => (
        <Group gap="xs" align="center" wrap="nowrap">
          <StatusDot status={option.value} />
          <Text size="sm" fw={checked ? 600 : 400} className="jst-nowrap">
            {option.label}
          </Text>
        </Group>
      )}
      onChange={async (next) => {
        if (!next || next === value) return;
        setSaving(true);
        setValue(next);
        try {
          await patchStatus(folderPath, next);
          onChange();
        } catch (e) {
          setValue(current);
          alert(`Failed to update status: ${e instanceof Error ? e.message : String(e)}`);
        } finally {
          setSaving(false);
        }
      }}
    />
  );
}
