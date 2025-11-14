import { Breadcrumb, BreadcrumbItem, BreadcrumbLink } from '@chakra-ui/react'
import { useLocation, Link as RouterLink } from 'react-router-dom'

const AppBreadcrumb: React.FC = () => {
  const location = useLocation()
  
  const getBreadcrumbs = (pathname: string) => {
    const paths = [
      { label: 'Home', path: '/' }
    ]
    
    switch (pathname) {
      case '/quick-start':
        paths.push({ label: 'Quick Start', path: '/quick-start' })
        break
      case '/quick-start/step-2':
        paths.push({ label: 'Quick Start', path: '/quick-start' })
        paths.push({ label: 'Choose Template', path: '/quick-start/step-2' })
        break
      case '/quick-start/step-3':
        paths.push({ label: 'Quick Start', path: '/quick-start' })
        paths.push({ label: 'Choose Template', path: '/quick-start/step-2' })
        paths.push({ label: 'Configure Extraction', path: '/quick-start/step-3' })
        break
      case '/quick-start/step-4':
        paths.push({ label: 'Quick Start', path: '/quick-start' })
        paths.push({ label: 'Choose Template', path: '/quick-start/step-2' })
        paths.push({ label: 'Configure Extraction', path: '/quick-start/step-3' })
        paths.push({ label: 'Review Configuration', path: '/quick-start/step-4' })
        break
      case '/apps':
        paths.push({ label: 'Apps', path: '/apps' })
        break
      case '/entity-schema':
        paths.push({ label: 'Entity Schemas', path: '/entity-schema' })
        break
      case '/pipelines':
        paths.push({ label: 'Pipelines', path: '/pipelines' })
        break
      case '/testing':
        paths.push({ label: 'Testing', path: '/testing' })
        break
      case '/llm-models':
        paths.push({ label: 'LLM Models', path: '/llm-models' })
        break
      case '/settings':
        paths.push({ label: 'Settings', path: '/settings' })
        break
    }
    
    return paths
  }
  
  const breadcrumbs = getBreadcrumbs(location.pathname)
  
  // Don't show breadcrumb if we're on home page
  if (location.pathname === '/') {
    return null
  }
  
  return (
    <Breadcrumb 
      separator="/"
      mb={6}
      fontSize="sm"
    >
      {breadcrumbs.map((crumb, index) => {
        const isLast = index === breadcrumbs.length - 1
        
        return (
          <BreadcrumbItem key={crumb.path} isCurrentPage={isLast}>
            {isLast ? (
              <BreadcrumbLink 
                color="var(--Secondary-ws-elm-700)" 
                fontWeight="medium"
              >
                {crumb.label}
              </BreadcrumbLink>
            ) : (
              <BreadcrumbLink 
                as={RouterLink} 
                to={crumb.path}
                color="gray.500"
                _hover={{ color: 'var(--Secondary-ws-elm-700)' }}
              >
                {crumb.label}
              </BreadcrumbLink>
            )}
          </BreadcrumbItem>
        )
      })}
    </Breadcrumb>
  )
}

export default AppBreadcrumb