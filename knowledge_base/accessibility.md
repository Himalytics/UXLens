# Accessibility Guidance

This file summarizes selected accessibility principles useful for preliminary interface-design review. It is not a substitute for a formal WCAG conformance audit.

## Four WCAG Principles
WCAG 2.2 organizes accessibility guidance under four broad principles: perceivable, operable, understandable, and robust. A design should make important information available in forms users can perceive, make interaction possible through supported input methods, make behavior and content understandable, and use implementation patterns that can be interpreted reliably by user agents and assistive technologies.

Design guidance: consider whether users can perceive the information, operate the controls, understand the workflow, and use the experience with assistive technology. Accessibility should be considered throughout design rather than added only at the end.

Reference: https://www.w3.org/WAI/standards-guidelines/wcag/

## Form Labels and Instructions
Inputs need clear labels or instructions when users must provide information. Visible, descriptive labels help users understand the purpose of controls and reduce input mistakes. Required formats should be explained when they are not obvious.

Design guidance: give controls unique and meaningful labels; indicate required fields in more than one understandable way when appropriate; provide format examples for unusual inputs; do not rely on placeholder text as the only explanation of a field's purpose.

Reference: https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html

## Error Identification
When an input error is detected, users should be able to determine that an error exists and understand what is wrong. Descriptive text is important because color or an icon alone may not be sufficient for every user.

Design guidance: identify the affected field; explain the error in text; provide a practical correction; keep valid information intact; consider placing a summary of errors where it helps users navigate longer forms.

Reference: https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html

## Keyboard and Input Accessibility
Important functionality should not depend exclusively on a pointing device. Keyboard access is a foundational accessibility consideration for interactive web content, and focus should move in a logical sequence that users can understand.

Design guidance: ensure controls can be reached and activated from a keyboard; preserve visible focus indication; avoid interactions that require only hover or precise pointer movement; test common workflows without a mouse.

Reference: https://www.w3.org/WAI/standards-guidelines/wcag/glance/

## Do Not Rely on Color Alone
Color can reinforce meaning, but critical information should not be communicated only through color. Users with color-vision differences, low vision, display limitations, or contextual constraints may miss color-only distinctions.

Design guidance: pair color with text, labels, icons, patterns, or other perceivable cues. For example, an invalid field can use color plus a text message that explains the problem.

Reference: https://www.w3.org/WAI/WCAG22/quickref/

## Non-Text Content and Alternatives
Meaningful non-text content should have an appropriate text alternative so that its purpose or information can be conveyed to users who cannot perceive the visual content directly. Decorative images can be treated differently from meaningful images.

Design guidance: provide useful alternatives for meaningful images and controls; write alternatives around purpose rather than visual trivia; avoid duplicating nearby text unnecessarily.

Reference: https://www.w3.org/WAI/WCAG22/Understanding/non-text-content.html
