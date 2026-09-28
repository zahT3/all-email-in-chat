---
name: All Email in Chat
description: A focused local setup interface with warm neutral surfaces and restrained green actions.
colors:
  primary: "#24664e"
  primary-hover: "#174d39"
  primary-active: "#123e2d"
  focus: "#267858"
  page: "#f4f5f2"
  surface: "#fff"
  text: "#252e2b"
  muted: "#626d65"
  line: "#dce1da"
  input-border: "#bbc5bc"
  input-border-hover: "#809485"
  placeholder: "#68776d"
  secondary-border: "#c6cec6"
  secondary-text: "#303c34"
  secondary-hover: "#f0f3ee"
  selected-surface: "#edf4ee"
  selected-text: "#214e38"
  option-border: "#d0d8d0"
  option-border-hover: "#73927e"
  complete-surface: "#e0ece2"
  complete-border: "#bfd3c6"
  inset-surface: "#f3f5ef"
  error-surface: "#fff0ed"
  error-text: "#982f2d"
  error-border: "#eec3bb"
  code-surface: "#f3f5f0"
  code-text: "#354639"
typography:
  headline:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif'
    fontSize: "26px"
    fontWeight: 650
    lineHeight: 1.35
    letterSpacing: "-0.02em"
  headline-mobile:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif'
    fontSize: "24px"
    fontWeight: 650
    lineHeight: 1.35
    letterSpacing: "-0.02em"
  title:
    fontSize: "14px"
    fontWeight: 600
    lineHeight: 1.55
  body:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif'
    fontSize: "15px"
    lineHeight: 1.55
  label:
    fontSize: "14px"
    fontWeight: 550
  helper:
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.6
  action:
    fontSize: "14px"
    fontWeight: 600
    lineHeight: 1.55
  path:
    fontSize: "12px"
    lineHeight: 1.55
  code:
    fontSize: "11px"
    lineHeight: 1.7
rounded:
  control: "7px"
  notice: "8px"
  utility: "5px"
  code: "6px"
  surface: "14px"
  circle: "50%"
spacing:
  control-gap: "8px"
  action-gap: "12px"
  code-inset: "13px"
  field-grid-gap: "12px"
  section-inset: "20px"
  field-stack: "20px"
  section-gap: "24px"
  page-heading-gap: "25px"
  surface-inset: "32px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    typography: "{typography.action}"
    rounded: "{rounded.control}"
    padding: "10px 16px"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-primary-active:
    backgroundColor: "{colors.primary-active}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.secondary-text}"
    typography: "{typography.action}"
    rounded: "{rounded.control}"
    padding: "10px 16px"
  button-secondary-hover:
    backgroundColor: "{colors.secondary-hover}"
  button-text:
    backgroundColor: "transparent"
    textColor: "{colors.primary}"
    padding: "8px 0"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.control}"
    padding: "10px 12px"
    width: "100%"
  progress-current:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    rounded: "{rounded.circle}"
    size: "22px"
  agent-option:
    rounded: "{rounded.control}"
    padding: "11px 12px"
  agent-option-selected:
    backgroundColor: "{colors.selected-surface}"
    textColor: "{colors.selected-text}"
  main-surface:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.surface}"
    padding: "32px"
  notice-success:
    backgroundColor: "{colors.selected-surface}"
    textColor: "{colors.selected-text}"
    rounded: "{rounded.notice}"
    padding: "16px"
  notice-error:
    backgroundColor: "{colors.error-surface}"
    textColor: "{colors.error-text}"
    rounded: "{rounded.notice}"
    padding: "13px 15px"
  code-preview:
    backgroundColor: "{colors.code-surface}"
    textColor: "{colors.code-text}"
    rounded: "{rounded.code}"
    padding: "13px"
  language-current:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.selected-text}"
    rounded: "{rounded.utility}"
    padding: "5px 10px"
---

# Design System: All Email in Chat

## Overview

**Creative North Star: "Focused Settings"**

A quiet settings interface gives each task a clear heading, a readable working area, and a visible next action. Warm neutral surroundings and a white working surface carry the structure; graphite text and restrained green accents carry hierarchy and state. The character comes from proportion, practical copy, and precise controls.

System typography supports Chinese and English labels and familiar desktop form behavior. Native fields, radio buttons, checkboxes, and disclosures remain recognizable. The implementation uses CSS surfaces and inline vector icons, with no shipping raster interface assets.

This document records the implemented visual system in `frontend/src/style.css` and `frontend/src/main.tsx`, aligned with `PRODUCT.md`. It describes interface behavior; it does not certify provider connectivity, security, or desktop-client compatibility.

**Key Characteristics:**

- Warm neutral canvas, white work surface, and one restrained green accent family.
- Readable bilingual system typography with compact monospace previews.
- Native controls, visible keyboard focus, and explicit status text.
- Flat surfaces defined by borders, spacing, and tonal contrast.
- A narrow single-column wizard with horizontal progress and a persistent language switch.

## Colors

Muted greens sit inside a warm neutral palette. The frontmatter is the normative token list; component-specific tints remain in the stylesheet where they are used.

### Primary

- **Deep Leaf** (`primary`) marks the main action, native checked state, current progress marker, links, and completion icon. Darker hover and active tones make button feedback visible.
- **Focus Green** (`focus`) is the keyboard outline color, distinct from the control border.
- **Pale Leaf** (`selected-surface`, `complete-surface`) supports selection, successful checks, and completed progress.

### Neutral

- **Warm Paper** (`page`) surrounds the application; **White Work Surface** (`surface`) contains the form and controls.
- **Graphite** (`text`) carries primary copy; **Sage Gray** (`muted`) carries supporting text and footer copy.
- **Quiet Lines** (`line`) separate sections. Input and secondary-button borders use stronger dedicated tokens.
- **Soft Inset** (`inset-surface`) supports the sample prompt. Code previews use their pale background and green-gray text without a border.
- **Clay Error** (`error-surface`, `error-text`, `error-border`) is a semantic exception for recoverable failures, not an additional brand accent.

**The State Has Words Rule.** Pair state color with a label, icon, or native checked state; color alone never communicates completion or failure.

## Typography

Body and headings use the operating system sans-serif stack with Chinese fallbacks. There is no downloaded font or separate display face. Paths and code retain native browser monospace styling.

- **Page heading:** compact headline typography, reduced on mobile while preserving weight and line height.
- **Section heading:** the title role uses an explicit medium-bold weight for subordinate sections.
- **Body and labels:** body copy anchors the interface; field labels are slightly smaller and medium weight. Heading descriptions remain 14px in both layouts.
- **Helper text:** small regular copy stays adjacent to its field; field notes have a maximum measure of 65ch.
- **Code and paths:** separate compact roles wrap long content. Preview blocks scroll vertically after 300px.
- **Mobile fields:** inputs and selects use 16px text at the small breakpoint.

**The Familiar Type Rule.** Use system sans for tasks and monospace for inspectable configuration; reserve the largest text for the current task heading.

## Layout

The header is centered with a maximum width of 1120px, minimum height of 76px, and padding of 20px 32px. The product mark sits opposite the always-visible Chinese/English switch.

The centered wizard has a maximum width of 608px, including padding of 24px 24px 40px. A horizontal three-step sequence sits above the single working surface, separated by 26px. The surface uses the frontmatter padding and radius without a fixed minimum height. The footer sits below it.

Fields stack with a 7px label/control gap and the field-stack spacing. Server/port pairs use a flexible server field, an 84px port field, and a 12px gap. Agent choices use two columns with an 8px gap. Main actions fill the content width.

At viewport widths of at most 540px, header padding becomes 16px 20px with a 68px minimum height. Wizard padding becomes 14px 16px 28px; surface padding becomes 24px 20px while retaining its radius. Progress stays horizontal with 22px separation below. Agent choices stack; server/port pairs retain an 80px port field and an 8px gap. Long addresses and paths wrap.

## Elevation & Depth

The interface has no box shadows, gradients, or backdrop effects. White and lightly tinted surfaces create depth through tonal contrast, thin borders, and spacing. Keyboard outlines express focus and do not imply an elevated surface.

**The Flat Surface Rule.** Use borders and tonal changes to distinguish working areas and states; do not add decorative elevation to this system.

## Shapes

Controls and selectable client rows share gently curved corners. Notices and the sample prompt use the notice radius; the working surface retains its broader radius on mobile. Password visibility and language controls use the smaller utility radius; code blocks use the code radius.

Borders are thin and continuous. Circular progress markers and small monochrome inline icons support familiar meanings without becoming illustrations.

## Components

### Buttons

Solid primary and bordered secondary actions have a 44px minimum height, an 8px icon gap, and the action typography. Text actions use 13px type and a 36px minimum height; the Back control has a 28px minimum height.

Primary hover and active states darken the fill. Secondary hover uses a pale neutral tint. Text and Back hover underline and darken. Disabled buttons use 0.6 opacity and the waiting cursor. There is no button transition.

### Inputs, selects, and disclosures

Inputs and selects fill their field width with a 44px minimum height and a border that strengthens on hover. A password visibility button occupies the field's right edge. Checkboxes use native 16px controls; radios retain native sizing and primary accent.

Advanced settings use native `details`/`summary` between thin rules. In the current wizard, known presets collapse server fields, while manual configuration opens them. Only `details::details-content` receives a 160ms discrete transition, gated by `prefers-reduced-motion: no-preference`.

### Language and progress navigation

The header language group uses two text buttons with `aria-pressed`; the selected language sits on white within a muted rounded container. It remains visible at all widths and across steps.

The three named steps are an ordered, non-clickable list in a labelled navigation region. The current step exposes `aria-current="step"`. All markers are 22px circles. Current markers use a solid accent; completed markers combine a check with pale green; future markers retain an outline. Thin lines connect the steps.

### Working surface and feedback

The white panel carries one task heading and its current form. The first view shows email entry, with returning accounts and provider help below. Provider selection and credentials follow; exact local domain matching has a manual fallback. Ordinary onboarding has no demo action. Explicit developer mode retains a labelled amber notice above the surface and isolated output.

Interactive elements receive a 3px focus outline with a 3px offset. Page changes focus the heading, whose outline is suppressed. Errors use `role="alert"` and receive programmatic focus; there is no separate error-outline style. Loading and busy copy use `role="status"`. Successful IMAP checks use an icon and readable text in a pale green inset.

### Agent choice, preview, and completion

Agent choices put a native radio inside a padded label. Checked rows combine a stronger green border, pale fill, and selected text. The preview separates the wrapping destination, disclosed code, explanation, and explicit apply action. Completion pairs an icon and precise saved-configuration copy with a sample prompt and follow-up actions. Read-only IMAP checks, SMTP delivery, saved configuration, and desktop-client verification remain distinct statements.

## Do's and Don'ts

### Do:

- **Do** preserve the warm neutral canvas, white working surface, and restrained green state vocabulary.
- **Do** keep native labels, inputs, selects, radio buttons, checkboxes, and disclosures recognizable.
- **Do** preserve visible focus, explicit status text, wrapping identifiers, and the documented responsive layout.
- **Do** use primary actions for the next concrete operation and secondary or text actions for alternatives.
- **Do** distinguish demo results, receiving-connection checks, saved configuration, and client verification in completion copy.

### Don't:

- **Don't** add decorative gradients, shadows, hero imagery, or oversized display typography to the settings interface.
- **Don't** replace native checked states or written status with color alone.
- **Don't** hide the configuration preview or its destination before the write action.
- **Don't** describe a saved configuration or demo completion as verified real-mailbox or desktop-client operation.
