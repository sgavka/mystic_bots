**Is task investigated** — yes
**Commit ID** — 9731769
**Summary** — Make bot understand dates in different formats (DD.MM.YYYY, DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD, etc.)

## Checkboxes

- [ ] Create `parse_date` utility in horoscope/utils.py
- [ ] Update wizard handler to use new parser
- [ ] Update error message to show accepted formats
- [ ] Store parsed date as ISO string in FSM state instead of raw text
- [ ] Update profile creation to use date.fromisoformat()
- [ ] Add tests for date parsing
- [ ] Update handler tests

## Investigation

### Current State
- Only accepts DD.MM.YYYY format via `datetime.strptime(text, "%d.%m.%Y")`
- Two parse locations: line 142 (validation) and line 198 (profile creation)
- FSM state stores raw text string, re-parsed later

### Implementation Plan

1. **Add `parse_date()` to `horoscope/utils.py`**:
   - Try multiple formats in order: DD.MM.YYYY, DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD, YYYY/MM/DD
   - Return `date` object or None

2. **Update wizard handler** (`horoscope/handlers/wizard.py`):
   - Replace `strptime` call with `parse_date()`
   - Store `date.isoformat()` in FSM state (not raw user text)
   - Use `date.fromisoformat()` in profile creation

3. **Update error message**: Show multiple accepted formats

4. **Update `create_profile` repository method**: Accept `date` object instead of string
