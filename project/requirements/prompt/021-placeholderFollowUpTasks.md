# Capture requirement 021: Placeholder follow-up tasks

Requirement: 021 —
`project/requirements/features/021-placeholderFollowUpTasks.md`
Role: refine

Read the requirement and applicable repository instructions before changing
anything. Refine the task aggregate, lifecycle, storage ownership and safe
`eolas todo --list` projection before implementation. Preserve the scope
boundaries: exact whole-field markers only, no value guessing, no reminders or
external task-manager integration, and no private field values in default task
output.

Resolve whether task state belongs in the shared record store or a dedicated
Clann task document, how task identity remains idempotent across edits and
imports, and how a later field update resolves the correct task. Create an ADR
only if the chosen storage/lifecycle design is consequential.

Changes may be made to the requirement, its prompt, the requirements index and
an ADR when required. Do not implement capture, persistence or CLI behavior
while refining this requirement.

Verify the requirement has observable acceptance criteria, clear task-list
privacy boundaries, explicit failure behavior and a credible criterion-to-test
mapping. Leave the requirement in `ToDo` until the design is agreed.
