I have created the following plan after thorough exploration and analysis of the codebase. Follow the below plan verbatim. Trust the files and references. Do not re-verify what's written in the plan. Explore only when absolutely necessary. First implement all the proposed file changes and then I'll review all the changes together at the end.

### Observations

The codebase has a well-structured foundation with comprehensive Project data model including status and progress fields. The Payload CMS collections configuration shows that status and progress fields are already defined with proper validation. A WebSocket infrastructure exists for real-time collaboration features. The form system uses React Hook Form with Zod validation and has retry functionality already implemented. The UI components follow consistent design patterns with proper accessibility.

### Approach

I'll enhance the ProjectForm with status management, progress tracking UI, and collaborative features by extending the existing validation schema, creating new UI components that follow established patterns, and integrating with the existing WebSocket infrastructure. The approach focuses on incremental enhancement rather than rebuilding, ensuring backward compatibility while adding the requested functionality. I'll implement conditional field logic and bulk operations using the existing form field patterns.

### Reasoning

I explored the repository structure and examined the relevant files mentioned by the user. I analyzed the Project interface in payload-types.ts to understand the data model, reviewed the existing ProjectForm.tsx implementation, examined the Payload collections configuration in Projects.ts, and discovered the WebSocket infrastructure in useWebSocket.ts. I also reviewed the existing UI components and form field patterns to understand the design system and implementation approach.

## Mermaid Diagram

sequenceDiagram
    participant User
    participant ProjectForm
    participant useCollaboration
    participant WebSocket
    participant ValidationSchema
    participant PayloadCMS
    participant Collaborators

    User->>ProjectForm: Update status/progress
    ProjectForm->>ValidationSchema: Validate new fields
    ValidationSchema->>ProjectForm: Return validation result
    ProjectForm->>useCollaboration: Broadcast change
    useCollaboration->>WebSocket: Send update event
    WebSocket->>Collaborators: Notify active users
    ProjectForm->>PayloadCMS: Submit form data
    PayloadCMS->>ProjectForm: Confirm update
    ProjectForm->>User: Show success feedback
    Collaborators->>ChangeNotification: Display real-time update
    ChangeNotification->>Collaborators: Show change details

## Proposed File Changes

### apps\auto-movie\src\lib\validations\project-schema.ts(MODIFY)

References: 

- apps\auto-movie\src\collections\Projects.ts

Extend the `projectSchema` to include the `status` field as a required enum matching the Payload collection configuration (concept, pre-production, production, post-production, completed, on-hold). Add `progress` object validation with `currentPhase` enum, `overallProgress` number (0-100), and `completedSteps` array. Update the `updateProjectSchema` to include these new fields as optional for editing. The validation should match the backend constraints defined in `Projects.ts` collection configuration.

### apps\auto-movie\src\components\ui\ProgressBar.tsx(NEW)

References: 

- apps\auto-movie\src\components\ui\Button.tsx
- apps\auto-movie\src\components\ui\Card.tsx

Create a reusable progress bar component that displays visual progress indicators with percentage display, color-coded progress states (red for 0-25%, yellow for 26-75%, green for 76-100%), and optional manual editing capability. The component should accept `value` (0-100), `editable` boolean, `onChange` callback, and `showPercentage` boolean props. Include accessibility features with proper ARIA labels and keyboard navigation for editable mode. Use the existing design system colors and styling patterns from `Button.tsx` and `Card.tsx`.

### apps\auto-movie\src\components\ui\StatusBadge.tsx(NEW)

References: 

- apps\auto-movie\src\components\ui\Card.tsx
- apps\auto-movie\src\collections\Projects.ts

Create a status badge component that displays project status with appropriate color coding and icons. The component should accept `status` prop matching the project status enum and display with consistent styling. Use color mapping: concept (gray), pre-production (blue), production (orange), post-production (purple), completed (green), on-hold (red). Include status transition indicators and tooltips explaining each status. Follow the existing `Card.tsx` styling patterns for consistency.

### apps\auto-movie\src\components\forms\form-fields\FormProgressInput.tsx(NEW)

References: 

- apps\auto-movie\src\components\forms\form-fields\FormNumberInput.tsx
- apps\auto-movie\src\components\forms\form-fields\FormField.tsx
- apps\auto-movie\src\components\ui\ProgressBar.tsx(NEW)

Create a specialized form field component for progress input that combines a slider and number input for manual progress updates. The component should integrate with React Hook Form using `forwardRef` and accept standard form field props. Include validation for 0-100 range, visual feedback for progress changes, and integration with the `ProgressBar` component. Follow the existing form field patterns from `FormNumberInput.tsx` and `FormField.tsx` for consistency.

### apps\auto-movie\src\hooks\useCollaboration.ts(NEW)

References: 

- apps\auto-movie\src\hooks\useWebSocket.ts
- apps\auto-movie\src\lib\toast.ts

Create a custom hook for managing collaborative editing features using the existing `useWebSocket` hook. The hook should handle real-time project updates, change notifications, edit conflict detection, and user presence indicators. Include functions for broadcasting project changes, listening for collaborator updates, and managing edit history. Integrate with the existing WebSocket infrastructure from `useWebSocket.ts` and provide toast notifications for collaborative events using the existing toast system.

### apps\auto-movie\src\components\ui\ChangeNotification.tsx(NEW)

References: 

- apps\auto-movie\src\components\ui\Card.tsx
- apps\auto-movie\src\components\ui\Button.tsx
- apps\auto-movie\src\hooks\useCollaboration.ts(NEW)

Create a change notification component that displays real-time updates from collaborators. The component should show user avatars, change descriptions, timestamps, and action buttons (view, dismiss). Include different notification types for status changes, progress updates, and field modifications. Use the existing `Card.tsx` and `Button.tsx` patterns for styling and integrate with the collaboration hook for real-time updates.

### apps\auto-movie\src\components\forms\form-fields\ConditionalFormSection.tsx(NEW)

References: 

- apps\auto-movie\src\components\forms\form-fields\FormField.tsx

Create a conditional form section component that shows/hides form fields based on other field values. The component should accept `condition` function, `watchFields` array, and `children` elements. Include smooth animations for show/hide transitions and proper accessibility attributes. This will be used to show advanced settings based on status or progress values. Follow React Hook Form patterns for field watching and validation.

### apps\auto-movie\src\components\forms\form-fields\index.ts(MODIFY)

References: 

- apps\auto-movie\src\components\forms\form-fields\FormProgressInput.tsx(NEW)
- apps\auto-movie\src\components\forms\form-fields\ConditionalFormSection.tsx(NEW)

Update the form fields index file to export the new `FormProgressInput` and `ConditionalFormSection` components alongside the existing form field exports. This maintains the centralized export pattern for all form field components.

### apps\auto-movie\src\components\ui\index.ts(MODIFY)

References: 

- apps\auto-movie\src\components\ui\ProgressBar.tsx(NEW)
- apps\auto-movie\src\components\ui\StatusBadge.tsx(NEW)
- apps\auto-movie\src\components\ui\ChangeNotification.tsx(NEW)

Update the UI components index file to export the new `ProgressBar`, `StatusBadge`, and `ChangeNotification` components alongside the existing UI component exports. This maintains the centralized export pattern for all UI components.

### apps\auto-movie\src\components\forms\ProjectForm.tsx(MODIFY)

References: 

- apps\auto-movie\src\components\forms\form-fields\FormSelect.tsx
- apps\auto-movie\src\components\forms\form-fields\FormProgressInput.tsx(NEW)
- apps\auto-movie\src\components\forms\form-fields\ConditionalFormSection.tsx(NEW)
- apps\auto-movie\src\components\ui\StatusBadge.tsx(NEW)
- apps\auto-movie\src\components\ui\ChangeNotification.tsx(NEW)
- apps\auto-movie\src\hooks\useCollaboration.ts(NEW)
- apps\auto-movie\src\collections\Projects.ts

Enhance the existing ProjectForm with status management dropdown, progress tracking UI, and collaborative features. Add status field using `FormSelect` with the status options from the collections configuration. Add progress section with `currentPhase` dropdown, `overallProgress` using `FormProgressInput`, and visual progress indicators. Integrate the `useCollaboration` hook for real-time updates and change notifications. Add conditional sections that show advanced settings based on status (e.g., show production settings only when status is 'production'). Update the form submission logic to handle the new fields and broadcast changes to collaborators. Maintain the existing retry functionality and error handling patterns.

### apps\auto-movie\src\app\(frontend)\dashboard\projects\[id]\edit\page.tsx(MODIFY)

References: 

- apps\auto-movie\src\components\ui\StatusBadge.tsx(NEW)
- apps\auto-movie\src\components\ui\ProgressBar.tsx(NEW)
- apps\auto-movie\src\components\ui\ChangeNotification.tsx(NEW)

Update the edit page to handle the new status and progress fields in the `handleUpdateProject` function. Add the new fields (`status`, `progress.currentPhase`, `progress.overallProgress`) to the FormData construction. Update the current project info display to show the new status badge and progress bar. Add collaborative editing indicators showing active collaborators and recent changes. Ensure the page properly handles the enhanced form data and maintains backward compatibility with existing projects.

### apps\auto-movie\src\components\projects\BulkProjectActions.tsx(NEW)

References: 

- apps\auto-movie\src\components\ui\Button.tsx
- apps\auto-movie\src\components\ui\Modal.tsx
- apps\auto-movie\src\components\forms\form-fields\FormSelect.tsx
- apps\auto-movie\src\lib\toast.ts

Create a bulk operations component for managing multiple projects simultaneously. The component should provide checkboxes for project selection, bulk status updates, bulk progress updates, and bulk deletion with confirmation dialogs. Include filtering and sorting capabilities for the bulk selection. Use the existing `Button.tsx`, `Modal.tsx`, and form field patterns. Integrate with the project API endpoints for bulk operations and provide proper error handling and success feedback using the existing toast system.