import { Autocomplete, TextField } from "@mui/material";
import type { EntityId, SmartListTag } from "jupiter-gen";
import { useState } from "react";

interface Props {
  allTags: Array<SmartListTag>;
  defaultTags: Array<EntityId>;
  readOnly: boolean;
}

export function TagsEditor({ allTags, defaultTags, readOnly }: Props) {
  const allTagsAsOptions = allTags.map((tag) => tag.tag_name.the_tag);

  const tagsByRefId: { [tag: string]: SmartListTag } = {};
  for (const tag of allTags) {
    tagsByRefId[tag.ref_id.the_id] = tag;
  }

  const [tagsHiddenValue, setTagsHiddenValue] = useState(
    defaultTags.map((tid) => tagsByRefId[tid.the_id].tag_name.the_tag).join(",")
  );

  return (
    <>
      <Autocomplete
        disablePortal
        multiple
        filterSelectedOptions
        freeSolo
        onChange={(event, newValue) => {
          setTagsHiddenValue(newValue.join(","));
        }}
        options={allTagsAsOptions}
        readOnly={readOnly}
        defaultValue={defaultTags.map(
          (tid) => tagsByRefId[tid.the_id].tag_name.the_tag
        )}
        renderInput={(params) => <TextField {...params} label="Tags" />}
      />
      <input name="tags" type="hidden" value={tagsHiddenValue} />
    </>
  );
}
