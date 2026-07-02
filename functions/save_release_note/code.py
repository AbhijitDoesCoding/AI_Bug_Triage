#input_type_name: SaveReleaseNoteInput
#output_type_name: SaveReleaseNoteResult
#function_name: save_release_note

from pydantic import BaseModel
from lemma_sdk import FunctionContext, Pod


class SaveReleaseNoteInput(BaseModel):
    bug_id: str
    note: str


class SaveReleaseNoteResult(BaseModel):
    bug_id: str
    saved: bool


async def save_release_note(
    ctx: FunctionContext, data: SaveReleaseNoteInput
) -> SaveReleaseNoteResult:
    """Write the human-approved release note back to the bug and flag it approved.

    Setting release_notes_approved=True also acts as the guard that stops the
    release-notes workflow from re-firing on this write (see the workflow's
    check_fixed decision).
    """
    pod = Pod.from_env()
    pod.table("bugs").update(
        data.bug_id,
        {"release_note": data.note, "release_notes_approved": True},
    )
    return SaveReleaseNoteResult(bug_id=data.bug_id, saved=True)
