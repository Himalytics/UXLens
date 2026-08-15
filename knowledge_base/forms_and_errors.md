# Forms, Validation, and Error Recovery

## Preserve Valid User Input
When one field is incorrect, clearing unrelated valid fields creates unnecessary work and can increase frustration. Error recovery should help users fix the smallest necessary part of the task whenever technically feasible.

Design guidance: retain valid values after validation errors; move attention to the field that needs correction; explain the expected format; avoid forcing the user to reconstruct information that the system already received correctly.

Reference: https://www.w3.org/WAI/tutorials/forms/notifications/

## Validate at an Appropriate Time
Validation should occur at a moment that helps rather than interrupts. Some fields benefit from feedback after the user leaves the field; other checks make more sense at submission. Constant premature errors while a user is still typing can be distracting.

Design guidance: validate when enough information exists to judge the input; make the message actionable; do not block progress for warnings that do not require immediate correction; distinguish warnings from errors.

Reference: https://www.w3.org/WAI/tutorials/forms/notifications/

## Explain Expected Formats
Users should not have to guess the format a field expects. Ambiguous requirements can create avoidable errors and repeated attempts.

Design guidance: provide concise examples such as date or phone-number formats when needed; place instructions near the relevant input; use sensible input controls and constraints where they reduce ambiguity.

Reference: https://www.w3.org/WAI/tutorials/forms/instructions/

## Confirm Consequential Actions
Actions such as permanent deletion, account closure, irreversible submission, or large financial commitment deserve safeguards proportionate to their consequences. Confirmation is most valuable when an action is difficult or impossible to reverse.

Design guidance: distinguish destructive actions visually and verbally; explain consequences before commitment; provide undo when feasible; avoid generic confirmations that users can dismiss without understanding the result.

Reference: https://www.nngroup.com/articles/ten-usability-heuristics/
