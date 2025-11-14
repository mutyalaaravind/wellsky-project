# WellSky Design Language System (DLS) Guidelines

## ⚠️ CRITICAL FRAMEWORK MISMATCH NOTICE

**WARNING**: This document contains React/Chakra UI implementation examples, but the **official WellSky DLS is built on Angular 9** with Angular Material. This creates a significant conflict between this document and the official DLS guidance.

**Official DLS Technology Stack (per https://dls.wellsky.io):**
- Angular 9+ with TypeScript
- Angular Material base components
- Bootstrap 4 for responsive design

**Action Required**: Verify whether VIKI AI should follow the official Angular-based DLS or maintain React implementation. If using React, ensure components and patterns align with official DLS design principles even if implementation differs.

## Overview

This document provides comprehensive guidelines for implementing the WellSky Design Language System (DLS) across VIKI AI applications. The DLS ensures consistency, accessibility, and brand alignment across all user interfaces.

**Official DLS Documentation**: 
- [WellSky DLS Website](https://dls.wellsky.io/home)
- [WellSky-DLS NPM Package Installation Guide](https://wellsky.atlassian.net/wiki/spaces/~7120201d52cd4e20bb4407a33504bf83b3558f/pages/364021567/Information+on+Installation+of+WellSky+Github+NPM+Packages)

## Design Values

In order to craft great experiences, WellSky Design Language System is built on three core values:

### Put Users at the Forefront
We will act as an advocate for the end users by representing their best interests. We are empathetic, and we do our best to understand the users' environments and external factors as we help the users reach their end goal.

### UX Always Includes Research  
We recognize that research is applicable at all stages of the product development process and we choose to use evidence to drive our design decisions.

### Craft the Entire Experience
Starting from the initial touch point, we promise to guide the users – empowering them with a better understanding of how our products can address their jobs-to-be-done. We build experiences based on research and use evidence to drive our design decisions.

## Package Dependencies

### Core Packages
```json
{
  "@mediwareinc/wellsky-dls-react": "^4.1.11",
  "@mediwareinc/wellsky-dls-react-icons": "^4.1.11"
}
```

### Theme Integration
All applications must use the WellSky lightTheme:
```typescript
import { ChakraProvider } from '@chakra-ui/react'
import { lightTheme } from '@mediwareinc/wellsky-dls-react'

function App() {
  return (
    <ChakraProvider theme={lightTheme}>
      {/* Your app content */}
    </ChakraProvider>
  )
}
```

## Color Usage Guidelines

### WellSky Core Color Palette

The use of color within DLS begins with the WellSky corporate logo. The colors presented within make up our core color palette.

#### Theme Colors
```css
/* Primary Theme Color - Big Stone */
--wellsky-primary-big-stone: #253746;

/* Secondary Theme Color - Elm */  
--wellsky-secondary-elm: #228189;
--wellsky-secondary-elm-modified: #196E76; /* ADA compliant version */

/* Tertiary Theme Colors */
--wellsky-tertiary-tuscany: #8B4513; /* Adds warmth to cool palette, ADA compliant */
--wellsky-tertiary-zest: #FFB347; /* Complements secondary color, use sparingly */
```

**Color Usage Rules:**
- **Primary (Big Stone)**: The first and darkest color in the WellSky logo - excellent ADA compliant color for primary text and UI elements
- **Secondary (Elm)**: With slight modification for ADA compliance, serves as the active element color for interactive items
- **Tertiary (Tuscany)**: A splash of Tuscany adds warmth to the cool palette. The dark color keeps ADA compliance at the forefront
- **Tertiary (Zest)**: Zest complements the secondary color and when used sparingly adds brighter warmth to the palette

### Neutral Color Scale
```css
--wellsky-neutral-50: #F8FAFB;    /* Lightest backgrounds */
--wellsky-neutral-100: #F3F4F6;   /* Light backgrounds */
--wellsky-neutral-200: #E5E7EB;   /* Borders, dividers */
--wellsky-neutral-300: #D1D5DB;   /* Disabled states */
--wellsky-neutral-400: #9CA3AF;   /* Placeholder text */
--wellsky-neutral-500: #6B7280;   /* Secondary text */
--wellsky-neutral-600: #4B5563;   /* Body text */
--wellsky-neutral-700: #374151;   /* Headings */
--wellsky-neutral-800: #1F2937;   /* Primary text */
--wellsky-neutral-900: #111827;   /* High contrast text */
```

### Semantic Colors
```css
/* Text Colors */
--wellsky-text-primary: #1F2937;     /* Primary content */
--wellsky-text-secondary: #4B5563;   /* Secondary content */
--wellsky-text-muted: #6B7280;       /* Muted content */

/* Background Colors */
--wellsky-bg-primary: #FFFFFF;       /* Primary surfaces */
--wellsky-bg-secondary: #F8FAFB;     /* Secondary surfaces */
--wellsky-bg-accent: #E4F0F1;        /* Accent surfaces */
```

### Color Usage Rules
- **Primary Theme Color**: Use for primary actions, active states, and brand elements
- **Secondary Theme Color**: Use for interactive elements and action states
- **Neutral Scale**: Use for text hierarchy, backgrounds, and borders
- **Light and Dark Variants**: Use core colors at 500 level with appropriate lighter/darker variants
- **Always use CSS variables**: Reference colors via CSS custom properties for consistency

## Typography Rules

### Font Family
```css
--wellsky-font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

**CRITICAL**: Roboto is the font used across all WellSky digital properties. Please do not use any other font families (as explicitly stated on the official DLS website).

### Typography Principles

#### Legible & Accessible
Typography should meet ADA requirements outlined by WCAG 2.1 Level AA to ensure that content is accessible to a majority of users.

#### Maximize Readability  
Typography helps users read and understand more content with less effort.

**Font Requirements:**
- **Primary Font**: Roboto is the font used across all WellSky digital properties
- **Do NOT use any other font families**: This is explicitly stated in the official DLS

### Readability Guidelines

#### Line Length
- **Headers**: Best line length is between 15-40 characters per line
- **Body text**: Best line length is between 40-60 characters per line

#### Line Spacing (Leading)
Line height determines the vertical space between wrapped lines of text and is measured from baseline to baseline.

#### Header Spacing
- **Title spacing**: Space between a title (20px) and body text is 32px
- **Subhead spacing**: Space between a subheader (16px) and body text is 28px  
- **Body header spacing**: Space between a body header (13px) and body text is 20px

#### Paragraph Spacing
WCAG recommends adequate spacing between paragraphs to maximize legibility:
- **20px paragraphs**: Space between two 20px paragraphs is 28px
- **24px paragraphs**: Space between two 24px paragraphs is 32px

### Typography Components
Use DLS typography components for consistency:

```tsx
import { 
  Display1,      // Main headings
  Headline,      // Section headings  
  SubHeading1    // Subsection headings
} from '@mediwareinc/wellsky-dls-react'

// Usage
<Display1>Main Page Title</Display1>
<Headline>Section Title</Headline>
<SubHeading1>Subsection Title</SubHeading1>
```

### Typography Hierarchy
1. **Display1**: Primary page titles and hero content
2. **Headline**: Major section headings
3. **SubHeading1**: Subsection titles and card headers
4. **Body text**: Use default Chakra UI Text component with WellSky theme

## Component Guidelines

### Buttons

#### Primary Actions
```tsx
import { PrimaryButton } from '@mediwareinc/wellsky-dls-react'

<PrimaryButton onClick={handleSubmit}>
  Submit Form
</PrimaryButton>
```

#### Secondary Actions
```tsx
import { SecondaryButton } from '@mediwareinc/wellsky-dls-react'

<SecondaryButton onClick={handleCancel}>
  Cancel
</SecondaryButton>
```

#### Link Actions
```tsx
import { LinkButton } from '@mediwareinc/wellsky-dls-react'

<LinkButton onClick={handleEdit}>
  Edit Settings
</LinkButton>
```

### Form Components

#### Text Inputs
```tsx
import { TextInput } from '@mediwareinc/wellsky-dls-react'

<TextInput
  placeholder="Enter medication name"
  value={medicationName}
  onChange={setMedicationName}
/>
```

#### Text Areas
```tsx
import { TextArea } from '@mediwareinc/wellsky-dls-react'

<TextArea
  placeholder="Enter notes"
  value={notes}
  onChange={setNotes}
/>
```

#### Select Dropdowns
```tsx
import { Select } from '@mediwareinc/wellsky-dls-react'

<Select
  options={medicationTypes}
  value={selectedType}
  onChange={setSelectedType}
  placeholder="Select medication type"
/>
```

#### Checkboxes
```tsx
import { Checkbox } from '@mediwareinc/wellsky-dls-react'

<Checkbox
  isChecked={isActive}
  onChange={setIsActive}
>
  Mark as active
</Checkbox>
```

### Layout Components

#### Grid System
```tsx
import { Grid } from '@mediwareinc/wellsky-dls-react'

<Grid templateColumns="repeat(3, 1fr)" gap={4}>
  <GridItem>Content 1</GridItem>
  <GridItem>Content 2</GridItem>
  <GridItem>Content 3</GridItem>
</Grid>
```

#### Data Tables
```tsx
import { DynamicTableContainer } from '@mediwareinc/wellsky-dls-react'

<DynamicTableContainer
  data={medications}
  columns={columns}
  onRowClick={handleRowClick}
/>
```

### Navigation Components

#### Tabs
```tsx
import { Tabs } from '@mediwareinc/wellsky-dls-react'

<Tabs>
  <TabList>
    <Tab>Medications</Tab>
    <Tab>Allergies</Tab>
  </TabList>
  <TabPanels>
    <TabPanel>Medications content</TabPanel>
    <TabPanel>Allergies content</TabPanel>
  </TabPanels>
</Tabs>
```

### Feedback Components

#### Loading States
```tsx
import { Spinner } from '@mediwareinc/wellsky-dls-react'

<Spinner size="lg" color="primary" />
```

#### Tooltips
```tsx
import { Tooltip } from '@mediwareinc/wellsky-dls-react'

<Tooltip label="Additional information">
  <IconButton icon={<InfoIcon />} />
</Tooltip>
```

#### Badges
```tsx
import { Badge } from '@mediwareinc/wellsky-dls-react'

<Badge colorScheme="green">Active</Badge>
<Badge colorScheme="red">Inactive</Badge>
```

### Modal Components

#### Side Drawers
```tsx
import { CustomSideDrawer } from '@mediwareinc/wellsky-dls-react'

<CustomSideDrawer
  isOpen={isOpen}
  onClose={onClose}
  title="Edit Medication"
>
  <DrawerContent>
    {/* Form content */}
  </DrawerContent>
</CustomSideDrawer>
```

#### Popovers
```tsx
import { Popover } from '@mediwareinc/wellsky-dls-react'

<Popover
  trigger="click"
  content={<MenuContent />}
>
  <Button>Open Menu</Button>
</Popover>
```

## Icon Guidelines

### Icon Usage
Use WellSky DLS icons for consistency:
```tsx
import { 
  CheckSimple,
  AlertCircle,
  Delete,
  Upload,
  Close
} from '@mediwareinc/wellsky-dls-react-icons'
```

### Common Icon Patterns
- **Success states**: `CheckSimple`, `CheckboxMarkedCircleOutline`
- **Warning/Error states**: `AlertCircle`, `Warning`
- **Actions**: `Upload`, `Delete`, `Close`
- **Media controls**: `PlayCircle`, `PauseCircle`
- **Navigation**: `Back`, `DotsVertical`

### Icon Sizing
- Use consistent icon sizes within the same context
- Prefer 16px for inline icons, 24px for buttons, 32px for prominent actions

## Design Patterns

### Header Pattern
```tsx
// Standard application header
<Box
  w="full"
  bg="white"
  borderBottomWidth="1px"
  borderColor="gray.200"
  px={6}
  py={4}
  boxShadow="sm"
>
  <Flex justify="space-between" align="center">
    <Flex align="center" gap={4}>
      <Image src="/wellsky-logo.png" alt="Wellsky Logo" height="28px" />
      <Text fontSize="xl" fontWeight="semibold" className="wellsky-header-title">
        Application Name
      </Text>
    </Flex>
    <Avatar className="wellsky-avatar" name="User" />
  </Flex>
</Box>
```

### Sidebar Navigation Pattern
```tsx
// Standard sidebar navigation
<Box className="wellsky-sidebar-item">
  <Flex align="center" gap={3} p={3}>
    <Icon />
    <Text>Navigation Item</Text>
  </Flex>
</Box>
```

### Card Pattern
```tsx
// Standard content card
<Box
  bg="white"
  border="1px"
  borderColor="gray.200"
  borderRadius="md"
  p={6}
  shadow="sm"
>
  <SubHeading1>Card Title</SubHeading1>
  <Text color="gray.600">Card content</Text>
</Box>
```

### Form Section Pattern
```tsx
// Standard form section
<Box mb={6}>
  <SubHeading1 mb={4}>Section Title</SubHeading1>
  <Grid templateColumns="repeat(2, 1fr)" gap={4}>
    <TextInput label="Field 1" />
    <TextInput label="Field 2" />
  </Grid>
</Box>
```

### Action Bar Pattern
```tsx
// Standard action bar
<Flex justify="space-between" align="center" p={4} bg="gray.50">
  <Text color="gray.600">Selection information</Text>
  <HStack spacing={3}>
    <SecondaryButton>Cancel</SecondaryButton>
    <PrimaryButton>Save Changes</PrimaryButton>
  </HStack>
</Flex>
```

## UI/UX Best Practices

### Accessibility

**Compliance Standards**: WellSky applications must meet [WCAG 2.1 Level AA](https://www.w3.org/TR/WCAG21/) and [Section 508](https://www.section508.gov/) compliance standards.

**Official Accessibility Requirements (per DLS website):**
- Primary Standard: [WCAG 2.1 Level AA](https://www.w3.org/TR/WCAG21/)
- Federal Compliance: [Section 508](https://www.section508.gov/create/applicability-conformance)
- Reference Resources: [The A11Y Project Checklist](https://www.a11yproject.com/checklist/)

#### Color Contrast Requirements
- **Text smaller than 18px or 14px bold**: Minimum contrast of 4.5:1 between text colors and backgrounds
- **Text 18px+ or 14px+ bold**: Minimum contrast of 3:1 between text colors and backgrounds
- **WellSky targets a minimum contrast of 4.5:1** for smaller text as per official DLS
- Use adequate color contrast to ensure content is legible to the majority of users

#### Additional Accessibility Guidelines
- **Keyboard Navigation**: Ensure all interactive elements are keyboard accessible
- **Screen Readers**: Use proper ARIA labels and semantic HTML  
- **Focus States**: Visible focus indicators on all interactive elements
- **Visual and Development**: Follow both visual design and development accessibility practices

### Responsive Design
- **Mobile First**: Design for mobile and scale up
- **Breakpoints**: Use Chakra UI's responsive breakpoints
- **Touch Targets**: Minimum 44px touch targets for mobile
- **Content Priority**: Show most important content first on smaller screens

### Loading States
- **Skeleton Loading**: Use skeleton components for content loading
- **Spinner Usage**: Use spinners for short operations (<2 seconds)
- **Progress Indicators**: Show progress for longer operations
- **Optimistic Updates**: Update UI immediately for better perceived performance

### Error Handling
- **Inline Validation**: Show validation errors immediately
- **Error Messages**: Clear, actionable error messages
- **Fallback States**: Graceful degradation when components fail
- **Recovery Actions**: Provide ways for users to recover from errors

### Data Presentation
- **Pagination**: Use DLS table pagination for large datasets
- **Filtering**: Provide search and filter capabilities
- **Sorting**: Enable column sorting where appropriate
- **Empty States**: Meaningful empty state messages with next steps

### Interactive Feedback
- **Hover States**: Subtle hover effects on interactive elements
- **Active States**: Clear active/selected states
- **Disabled States**: Appropriate disabled styling and cursor states
- **Loading States**: Immediate feedback on user actions

### Content Guidelines
- **Microcopy**: Use clear, concise language
- **Labels**: Descriptive form labels and button text
- **Help Text**: Provide contextual help where needed
- **Error Messages**: Specific, actionable error messages

### Performance
- **Lazy Loading**: Load components and data as needed
- **Code Splitting**: Split code by routes and features
- **Image Optimization**: Use appropriate image formats and sizes
- **Bundle Size**: Monitor and optimize bundle sizes

## Implementation Checklist

### Before Starting Development
- [ ] Install latest WellSky DLS packages
- [ ] Configure ChakraProvider with lightTheme
- [ ] Import wellsky-theme.css for custom CSS variables
- [ ] Set up TypeScript types for DLS components

### During Development
- [ ] Use DLS components instead of custom implementations
- [ ] Follow color guidelines with CSS variables
- [ ] Implement proper typography hierarchy
- [ ] Add appropriate loading and error states
- [ ] Test keyboard navigation and screen reader compatibility

### Before Deployment
- [ ] Verify color contrast compliance
- [ ] Test responsive breakpoints
- [ ] Validate form accessibility
- [ ] Check icon usage consistency
- [ ] Review component spacing and alignment

## Common Pitfalls to Avoid

1. **Don't mix design systems**: Avoid mixing DLS with other UI libraries
2. **Don't hardcode colors**: Always use CSS variables or theme tokens
3. **Don't skip loading states**: Always provide feedback for async operations
4. **Don't ignore responsive design**: Test on multiple screen sizes
5. **Don't forget accessibility**: Include ARIA labels and keyboard navigation
6. **Don't overcomplicate layouts**: Use DLS Grid and Flex components
7. **Don't ignore error states**: Handle and display errors appropriately

## Design Patterns

### Data Tables
Use DLS data table patterns for consistent data presentation:
- Implement proper pagination for large datasets
- Enable column sorting where appropriate
- Provide search and filter capabilities
- Design meaningful empty state messages with next steps

### Empty States
- Provide clear, actionable messages when no data is available
- Include guidance on next steps users can take
- Use appropriate iconography to support the message

### Navigation Patterns
- Follow WellSky navigation standards for consistency
- Implement proper breadcrumb patterns where applicable
- Use left side navigation for complex applications
- Top navigation for simpler interfaces

### Confirmation Patterns
- Use consistent confirmation dialogs for destructive actions
- Provide clear action buttons with appropriate styling
- Include contextual information about the action being confirmed

## Framework and Technical Information

### Core Technologies
**IMPORTANT**: The official WellSky DLS is built on Angular 9, NOT React. The React packages mentioned in this document appear to be custom implementations that may not align with the official DLS.

**Official DLS Stack (per https://dls.wellsky.io):**
- **Angular 9+**: Core framework using TypeScript
- **Angular Material**: Base component library with WellSky customizations
- **Bootstrap 4**: Grid system and utilities for responsive design
- **imask.js**: Input masking for form components

**Responsive Breakpoints (Official DLS):**
- **XSmall**: 0px to 374px
- **Small**: 375px to 767px  
- **Medium**: 768px to 1023px
- **Large**: 1024px to 1919px
- **XLarge**: 1920px and above

### Browser Support
Following Angular 9 browser support standards:
- **Chrome**: Latest version
- **Firefox**: Latest version  
- **Edge**: Two most recent major versions
- **Safari**: Two most recent major versions
- **iOS**: Two most recent major versions
- **Android**: X (10.0), Pie (9.0), Oreo (8.0), Nougat (7.0)
- **Internet Explorer**: 11, 10 (compatibility view mode not supported)

## Getting Help

- **Official DLS Website**: [WellSky DLS](https://dls.wellsky.io/home)
- **Official Documentation**: [WellSky DLS Installation Guide](https://wellsky.atlassian.net/wiki/spaces/~7120201d52cd4e20bb4407a33504bf83b3558f/pages/364021567/Information+on+Installation+of+WellSky+Github+NPM+Packages)
- **GitHub Repository**: [Atlas.UI](https://github.com/mediwareinc/Atlas.UI)
- **Contact**: [ux@wellsky.com](mailto:ux@wellsky.com)
- **Package Versions**: Check package.json files in existing applications for version compatibility
- **Component Examples**: Reference existing implementations in medwidget, paperglass, and demo applications
- **Design Reviews**: Consult with design team for complex UI decisions

### Additional Resources
- [The A11Y Project](https://www.a11yproject.com/)
- [WCAG 2.1 Guidelines](https://www.w3.org/TR/WCAG21/)
- [Section 508 Standards](https://www.section508.gov/create/applicability-conformance)

---

*This guide should be updated as the WellSky DLS evolves and new components become available.*