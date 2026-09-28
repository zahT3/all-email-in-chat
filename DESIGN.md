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
  notice-text: "#4a5d4e"
  error: "#a12c30"
  error-surface: "#fff0ed"
  error-text: "#982f2d"
  error-border: "#eec3bb"
  code-surface: "#f3f5f0"
  code-text: "#354639"
  code-border: "#e4e8e0"
typography:
  headline:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif'
    fontSize: "27px"
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
    fontSize: "17px"
    lineHeight: 1.5
  body:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif'
    fontSize: "15px"
    lineHeight: 1.65
  label:
    fontSize: "14px"
    fontWeight: 550
  helper:
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.65
  action:
    fontSize: "15px"
    fontWeight: 600
    lineHeight: 1.65
  path:
    fontFamily: "ui-monospace, SFMono-Regular, Consolas, monospace"
    fontSize: "11px"
    lineHeight: 1.8
  code:
    fontFamily: "ui-monospace, SFMono-Regular, Consolas, monospace"
    fontSize: "0.93em"
rounded:
  control: "7px"
  notice: "8px"
  inset: "9px"
  surface-mobile: "11px"
  surface: "14px"
  circle: "50%"
spacing:
  control-gap: "8px"
  action-gap: "12px"
  code-inset: "16px"
  field-grid-gap: "18px"
  section-inset: "20px"
  field-stack: "22px"
  section-gap: "24px"
  page-heading-gap: "30px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    typography: "{typography.action}"
    rounded: "{rounded.control}"
    padding: "10px 18px"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-primary-active:
    backgroundColor: "{colors.primary-active}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.secondary-text}"
    typography: "{typography.action}"
    rounded: "{rounded.control}"
    padding: "10px 18px"
  button-secondary-hover:
    backgroundColor: "{colors.secondary-hover}"
  button-text:
    backgroundColor: "transparent"
    textColor: "{colors.primary}"
    rounded: "{rounded.control}"
    padding: "7px 3px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.control}"
    padding: "9px 12px"
    width: "100%"
  progress-current:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    rounded: "{rounded.circle}"
    size: "28px"
  agent-option:
    rounded: "{rounded.notice}"
    padding: "15px 13px"
  agent-option-selected:
    backgroundColor: "{colors.selected-surface}"
    textColor: "{colors.selected-text}"
  main-surface:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.surface}"
  notice:
    backgroundColor: "{colors.inset-surface}"
    textColor: "{colors.notice-text}"
    rounded: "{rounded.notice}"
    padding: "15px 17px"
  notice-error:
    backgroundColor: "{colors.error-surface}"
    textColor: "{colors.error-text}"
    rounded: "{rounded.notice}"
    padding: "15px 17px"
  code-preview:
    backgroundColor: "{colors.code-surface}"
    textColor: "{colors.code-text}"
    rounded: "{rounded.control}"
    padding: "16px"
---

# Design System: All Email in Chat

## Overview

**Creative North Star: "Focused Settings"**

A quiet settings interface gives each task a clear heading, a readable working area, and a visible next action. Warm neutral surroundings and a white working surface carry the structure; graphite text and restrained green accents carry hierarchy and state. The character comes from proportion, practical copy, and precise controls.

System typography supports Chinese-first labels and familiar desktop form behavior. Native fields, radio buttons, checkboxes, and disclosures remain recognizable. The implementation uses CSS surfaces and inline vector icons, with no shipping raster interface assets.

This document records the implemented visual system in `frontend/src/style.css` and `frontend/src/main.tsx`, aligned with `PRODUCT.md`. It describes interface behavior; it does not certify provider connectivity, security, or desktop-client compatibility.

**Key Characteristics:**

- Warm neutral canvas, white work surface, and one restrained green accent family.
- Readable Chinese-first system typography with compact monospace previews.
- Native controls, visible keyboard focus, and explicit status text.
- Flat surfaces defined by borders, spacing, and tonal contrast.
- A responsive progress rail that becomes a horizontal sequence on small screens.

## Colors

Muted greens sit inside a warm neutral palette. The frontmatter is the normative token list; component-specific tints remain in the stylesheet where they are used.

### Primary

- **Deep Leaf** (`primary`) marks the main action, selected radio state, current progress marker, links, and completion details. Darker hover and active tones make button feedback visible.
- **Focus Green** (`focus`) is the keyboard outline color. It remains distinct from the control border.
- **Pale Leaf** (`selected-surface`, `complete-surface`) supports selection and completed progress without turning an entire panel green.

### Neutral

- **Warm Paper** (`page`) surrounds the application; **White Work Surface** (`surface`) contains the form and its controls.
- **Graphite** (`text`) carries primary copy; **Sage Gray** (`muted`) carries supporting text, paths, and footer copy.
- **Quiet Lines** (`line`) separate sections. Input and secondary-button borders have stronger dedicated tokens to keep controls recognizable.
- **Soft Inset** (`inset-surface`) supports explanatory notices and the sample prompt. Code previews have their own pale background, border, and readable green-gray text.
- **Clay Error** (`error`, `error-surface`, `error-text`, `error-border`) is a semantic exception for recoverable failures. It is not an additional brand accent.

**The State Has Words Rule.** Pair state color with a label, icon, or native checked state; color alone never communicates completion or failure.

## Typography

The body and headings use the operating system sans-serif stack, with Chinese fallbacks, as recorded in the frontmatter. There is no downloaded font or separate display face. Paths and code use the platform monospace stack.

- **Page heading:** the headline role is compact and slightly tight; the mobile variant reduces its size while preserving weight and line height.
- **Section heading:** the title role introduces configuration previews and subordinate sections. Its bold weight comes from the browser heading default; the stylesheet does not define a separate weight token.
- **Body and labels:** body text anchors the interface; field labels are slightly smaller and medium weight. Introductory descriptions use 14px text and a maximum measure of 65ch; on mobile they use 13px.
- **Helper text:** small, regular text stays directly under its field or beside the relevant action. Longer field notes have a maximum measure of 70ch.
- **Code and paths:** the path role uses compact monospace text. Preview blocks start at 11px with line height 1.7; their nested `code` inherits the relative code size. Both wrap long content.
- **Mobile fields:** inputs and selects use 16px text at the small breakpoint. Labels remain visually separate from entered values.

**The Familiar Type Rule.** Use system sans for tasks and monospace for inspectable configuration; reserve the largest text for the current task heading.

## Layout

The centered application shell has a maximum width of 1240px and desktop side padding of 40px. An 88px top bar carries the product name and local-session label. The workspace uses a 250px progress rail plus a flexible content column and a minimum height of 730px.

The working surface uses content padding of 38px 44px 32px. Most fields stack vertically with a small label/control gap; the email/name row divides at 1.7:1 with an 18px gap. Server/port rows use a flexible server field and a 112px port field. Client choices form two columns. Actions wrap naturally, and the footer uses the same horizontal inset as the content.

| Viewport rule | Implemented behavior |
| --- | --- |
| At least 1500px | Add 26px top padding to the application shell. |
| At most 950px | Reduce shell sides to 24px and the rail to 200px; content becomes 32px 28px; client choices stack; the account summary may wrap. |
| At most 680px | Use 16px shell sides, a 70px top bar, and one vertical workspace. Progress becomes a compact horizontal sequence. Hide secondary sidebar copy; keep the named steps. Use content padding of 26px 20px and a smaller surface radius. |
| At most 680px, forms | Stack general field rows. Keep server/port rows paired with an 88px port field and 12px gap. Grow action buttons to fill available row width. Stack the demo entry and wrap long account identifiers and paths. |

The local-session header label becomes an icon at the small breakpoint; the footer retains the text explaining that the wizard runs locally. The working surface remains a single continuous form area rather than a collection of equal cards.

## Elevation & Depth

The implemented interface has no box shadows, gradients, or backdrop effects. White and lightly tinted surfaces create depth through tonal contrast, thin borders, and spacing. Keyboard outlines express focus and do not imply an elevated surface.

**The Flat Surface Rule.** Use borders and tonal changes to distinguish working areas and states; do not add decorative elevation to this system.

## Shapes

Controls have gently curved corners; notices and selectable client rows use a slightly broader curve. Larger working surfaces have the broadest corners, reduced on mobile. Account summaries and prompt panels use the inset radius. The radius tokens are normative.

Borders are thin and continuous. Circular markers belong to progress and small status indicators. The small monochrome inline icons reinforce familiar meanings such as mail, device, lock, back, next, and completion. They are supporting marks, not hero illustrations or a new logo asset.

## Components

### Buttons

Compact, direct actions use a solid primary, bordered secondary, or text-only treatment. Standard buttons have a minimum height of 43px, an 8px icon gap, and the action typography. Text buttons use a 40px minimum height and medium weight; the prompt-copy utility is a smaller 36px exception.

Primary hover and active states darken the fill. Secondary hover uses a pale neutral tint. Text-button hover adds an underline. Color and background transitions last 0.15s with `ease`; reduced-motion preference disables transitions. Disabled buttons use 0.58 opacity and cannot receive pointer events. Labels describe the next operation rather than a generic continuation.

### Inputs, selects, and disclosures

Native inputs and selects fill their field width, with a minimum height of 44px and a visible border that strengthens on hover. The containing label names the control, and helper text remains beside the field. Password fields preserve the native password affordance. Native validation attributes describe required values, input formats, and limits.

Checkboxes and radios remain native 17px controls with the primary accent. Client choices wrap a radio inside a padded label; selected rows combine an accent border, pale green fill, and checked radio. Advanced settings use native `details`/`summary` with top and bottom rules and a chevron that rotates when open. This is disclosure, not a separate route.

### Keyboard focus and feedback

Interactive elements receive a 3px focus outline with a 3px offset. Page changes focus the new heading programmatically; that heading suppresses its outline. Errors appear in a tinted notice with `role="alert"`, receive programmatic focus, and use a 2px error outline with a 2px offset. Loading and busy text use `role="status"`. These are implementation facts, not a claim of a completed accessibility audit.

### Progress navigation

Three named steps form an ordered, non-clickable progress list inside a labelled navigation region. The current step exposes `aria-current="step"`. Current markers use a solid accent fill; completed markers show a check inside a pale green circle; future markers retain an outline. Markers are 28px on desktop and 24px on small screens.

### Working surface and inset panels

The main white panel carries the task heading, form, and footer behind a single thin border. Account summaries, notices, and the sample prompt use flat tints and compact padding rather than shadows. A demo banner sits above the content and remains present across demo steps. Long identifiers and notice content wrap instead of expanding the panel.

### Configuration preview and completion

The preview separates the destination, inspectable code block, explanation, and explicit write action. Paths and code wrap at narrow widths. A completion mark appears with precise text identifying whether an actual configuration or an isolated demo file was saved; follow-up instructions still direct the user to verify tools in their desktop client. An IMAP result, SMTP status, saved configuration, and client verification remain separate statements.

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
