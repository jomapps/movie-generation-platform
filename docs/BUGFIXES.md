# Bug Fixes Log

**Last Updated**: September 30, 2025  
**Purpose**: Track all bug fixes and their resolutions

---

## 🐛 Fixed Bugs

### [2025-09-30] Project Creation Form Save Failure

**Severity**: Critical  
**Status**: ✅ Fixed  
**Module**: `apps/auto-movie`  
**Files Modified**: 
- `apps/auto-movie/src/actions/create-project.ts`

#### Problem Description
When users attempted to create a new project through the form at `/dashboard/projects/new`, the save operation would fail with the following errors:

1. **Primary Error**: Zod validation error - "Please select a valid project status"
2. **Secondary Error**: "Cannot read properties of undefined (reading '0')" - Error handler crash

#### Root Causes

**Bug #1: Missing `status` field in Zod validation**
```typescript
// ❌ BEFORE: status was extracted but NOT passed to validation
const validatedData = projectSchema.parse({
  title: rawData.title,
  description: rawData.description,
  genre: rawData.genre,
  episodeCount: rawData.episodeCount,
  targetAudience: rawData.targetAudience,
  // ❌ status: rawData.status,  <-- MISSING!
  projectSettings: { ... }
})
```

**Bug #2: Incorrect Zod v4 error handling**
```typescript
// ❌ BEFORE: Accessing zodError.errors[0] when using Zod v4
if (error?.constructor?.name === 'ZodError') {
  const zodError = error as any
  const firstError = zodError.errors[0]  // ❌ Zod v4 uses 'issues' not 'errors'
  return {
    success: false,
    error: firstError?.message || 'Invalid form data...',
  }
}
```

**Bug #3: Hardcoded status value**
```typescript
// ❌ BEFORE: Ignoring validated status
const result = await payload.create({
  collection: 'projects',
  data: {
    // ...
    status: 'concept', // ❌ Hardcoded instead of using validated value
  },
})
```

#### Solution

**Fix #1: Added `status` to validation** (Line 42)
```typescript
// ✅ AFTER: Include status in validation
const validatedData = projectSchema.parse({
  title: rawData.title,
  description: rawData.description,
  genre: rawData.genre,
  episodeCount: rawData.episodeCount,
  targetAudience: rawData.targetAudience,
  status: rawData.status,  // ✅ ADDED
  projectSettings: {
    aspectRatio: rawData.aspectRatio,
    episodeDuration: rawData.episodeDuration,
    qualityTier: rawData.qualityTier,
  },
})
```

**Fix #2: Corrected Zod v4 error handling** (Line 113)
```typescript
// ✅ AFTER: Use 'issues' for Zod v4
if (error?.constructor?.name === 'ZodError') {
  const zodError = error as any
  const firstError = zodError.issues?.[0]  // ✅ Use 'issues' for Zod v4
  return {
    success: false,
    error: firstError?.message || 'Invalid form data. Please check your inputs.',
  }
}
```

**Fix #3: Use validated status** (Line 90)
```typescript
// ✅ AFTER: Use validated status value
const result = await payload.create({
  collection: 'projects',
  data: {
    title: validatedData.title,
    description: validatedData.description,
    genre: validatedData.genre,
    episodeCount: validatedData.episodeCount,
    targetAudience: validatedData.targetAudience,
    status: validatedData.status,  // ✅ Use validated value
    projectSettings: validatedData.projectSettings,
    createdBy: defaultUser.id,
  },
})
```

#### Testing Results
- ✅ Project successfully created with all fields
- ✅ Proper validation error messages displayed
- ✅ Correct redirect to project detail page
- ✅ No server errors in logs
- ✅ Test project ID: `68db63f41703f1f5b6a8d7aa`

#### Impact
- **Users Affected**: All users attempting to create projects
- **Downtime**: None (development environment)
- **Data Loss**: None

#### Prevention
- Add integration tests for form submission
- Add Zod version compatibility checks
- Ensure all schema fields are included in validation calls

---

## 📋 Known Issues

### Form Validation Button State
**Severity**: Minor  
**Status**: 🔍 Under Investigation  
**Module**: `apps/auto-movie`

The "Create Project" button remains disabled even when all required fields are filled. This is a React Hook Form `isValid` state issue that doesn't affect functionality (form can still be submitted programmatically).

**Workaround**: Button becomes enabled after clicking in/out of form fields to trigger validation.

**Planned Fix**: Review React Hook Form validation mode and trigger logic.

---

## 🔄 Change History

| Date | Bug ID | Severity | Status | Module |
|------|--------|----------|--------|--------|
| 2025-09-30 | Project Creation Save | Critical | ✅ Fixed | apps/auto-movie |

---

**Maintained By**: Development Team  
**Review Cycle**: After each bug fix

