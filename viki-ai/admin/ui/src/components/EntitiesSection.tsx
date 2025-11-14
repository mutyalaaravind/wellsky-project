import React, { useState, useEffect } from 'react'
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  Spinner,
  Alert,
  AlertIcon,
  Collapse,
  useDisclosure,
  IconButton,
  Button,
  Select,
  Input,
  Spacer,
} from '@chakra-ui/react'
import { FiChevronDown, FiChevronRight, FiRefreshCw, FiSearch, FiCode, FiList } from 'react-icons/fi'
import { entitiesService, EntityData, ListEntitiesParams } from '../services/entitiesService'
import ConfigRenderer from './ConfigRenderer'

interface EntitiesSectionProps {
  appId: string
  subjectId: string
  documentId: string // This will be used as source_id
}

interface EntityGroupedData {
  [entityType: string]: EntityData[]
}

const EntitiesSection: React.FC<EntitiesSectionProps> = ({ appId, subjectId, documentId }) => {
  const [entities, setEntities] = useState<EntityData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  const [entityTypeFilter, setEntityTypeFilter] = useState<string>('')
  const [searchText, setSearchText] = useState('')
  const [viewMode, setViewMode] = useState<'entity' | 'json'>('entity')

  const fetchEntities = async (showRefreshSpinner = false) => {
    if (showRefreshSpinner) {
      setRefreshing(true)
    } else {
      setLoading(true)
    }

    setError(null)

    try {
      const params: ListEntitiesParams = {
        app_id: appId,
        subject_id: subjectId,
        source_id: documentId, // Filter by the document ID
        limit: 100 // Get more entities to show
      }

      if (entityTypeFilter) {
        params.entity_type = entityTypeFilter
      }

      const response = await entitiesService.listEntities(params)
      setEntities(response.data)
    } catch (err) {
      console.error('Error fetching entities:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch entities')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchEntities()
  }, [appId, subjectId, documentId, entityTypeFilter])

  const handleRefresh = () => {
    fetchEntities(true)
  }

  // Get unique entity types for filter dropdown
  const entityTypes = Array.from(new Set(entities.map(e => e.entity_type || 'Unknown'))).sort()

  // Filter entities based on search text
  const filteredEntities = entities.filter(entity => {
    if (!searchText) return true

    const searchLower = searchText.toLowerCase()

    // Search in entity type, id, and stringified data
    const searchableText = [
      entity.entity_type || '',
      entity.id || '',
      JSON.stringify(entity).toLowerCase()
    ].join(' ').toLowerCase()

    return searchableText.includes(searchLower)
  })

  // Group filtered entities
  const filteredGroupedEntities: EntityGroupedData = filteredEntities.reduce((acc, entity) => {
    const entityType = entity.entity_type || 'Unknown'
    if (!acc[entityType]) {
      acc[entityType] = []
    }
    acc[entityType].push(entity)
    return acc
  }, {} as EntityGroupedData)

  if (loading) {
    return (
      <VStack spacing={4} align="center" py={8}>
        <Spinner size="lg" color="var(--palette-accent-ws-elm-500)" />
        <Text color="gray.500">Loading entities...</Text>
      </VStack>
    )
  }

  if (error) {
    return (
      <VStack spacing={4} align="stretch">
        <Alert status="error">
          <AlertIcon />
          {error}
        </Alert>
        <Button
          leftIcon={<FiRefreshCw />}
          onClick={handleRefresh}
          isLoading={refreshing}
          loadingText="Refreshing..."
          colorScheme="blue"
          variant="outline"
          size="sm"
        >
          Retry
        </Button>
      </VStack>
    )
  }

  if (entities.length === 0) {
    return (
      <VStack spacing={4} align="center" py={8}>
        <Box color="gray.400">
          <FiSearch size={24} />
        </Box>
        <VStack spacing={2} align="center">
          <Text color="gray.500" fontWeight="medium">No entities found</Text>
          <Text color="gray.400" fontSize="sm">
            No entities have been extracted for this document yet.
          </Text>
        </VStack>
        <Button
          leftIcon={<FiRefreshCw />}
          onClick={handleRefresh}
          isLoading={refreshing}
          loadingText="Refreshing..."
          colorScheme="blue"
          variant="outline"
          size="sm"
        >
          Refresh
        </Button>
      </VStack>
    )
  }

  return (
    <VStack spacing={4} align="stretch">
      {/* Controls */}
      <HStack spacing={4} wrap="wrap">
        <HStack>
          <Text fontSize="sm" color="gray.600" minW="fit-content">Filter by type:</Text>
          <Select
            size="sm"
            value={entityTypeFilter}
            onChange={(e) => setEntityTypeFilter(e.target.value)}
            placeholder="All types"
            maxW="200px"
          >
            {entityTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </Select>
        </HStack>

        <HStack flex="1" maxW="300px">
          <Text fontSize="sm" color="gray.600" minW="fit-content">Search:</Text>
          <Input
            size="sm"
            placeholder="Search entities..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
        </HStack>

        <Spacer />

        <HStack spacing={2}>
          <HStack spacing={0}>
            <Button
              leftIcon={<FiList />}
              onClick={() => setViewMode('entity')}
              colorScheme={viewMode === 'entity' ? 'blue' : 'gray'}
              variant={viewMode === 'entity' ? 'solid' : 'outline'}
              size="sm"
              borderRightRadius={0}
            >
              Entity
            </Button>
            <Button
              leftIcon={<FiCode />}
              onClick={() => setViewMode('json')}
              colorScheme={viewMode === 'json' ? 'blue' : 'gray'}
              variant={viewMode === 'json' ? 'solid' : 'outline'}
              size="sm"
              borderLeftRadius={0}
            >
              JSON
            </Button>
          </HStack>

          <Button
            leftIcon={<FiRefreshCw />}
            onClick={handleRefresh}
            isLoading={refreshing}
            loadingText="Refreshing..."
            colorScheme="blue"
            variant="outline"
            size="sm"
          >
            Refresh
          </Button>
        </HStack>
      </HStack>

      {/* Entity Count Summary */}
      <HStack spacing={4}>
        <Text fontSize="sm" color="gray.600">
          Total: <Badge colorScheme="blue" ml={1}>{entities.length}</Badge>
        </Text>
        {searchText && (
          <Text fontSize="sm" color="gray.600">
            Filtered: <Badge colorScheme="green" ml={1}>{filteredEntities.length}</Badge>
          </Text>
        )}
        <Text fontSize="sm" color="gray.600">
          Types: <Badge colorScheme="purple" ml={1}>{Object.keys(filteredGroupedEntities).length}</Badge>
        </Text>
      </HStack>

      {/* Entities List */}
      <VStack spacing={4} align="stretch">
        {viewMode === 'entity' ? (
          filteredEntities.map((entity) => (
            <EntityItem
              key={entity.id}
              entity={entity}
              searchText={searchText}
            />
          ))
        ) : (
          filteredEntities.map((entity) => (
            <JsonEntityView
              key={entity.id}
              entity={entity}
            />
          ))
        )}
      </VStack>
    </VStack>
  )
}

interface JsonEntityViewProps {
  entity: EntityData
}

const JsonEntityView: React.FC<JsonEntityViewProps> = ({ entity }) => {
  const { isOpen: isEntityOpen, onToggle: onEntityToggle } = useDisclosure({ defaultIsOpen: true })
  const { isOpen: isHeaderOpen, onToggle: onHeaderToggle } = useDisclosure({ defaultIsOpen: false })
  const { isOpen: isEntityDataOpen, onToggle: onEntityDataToggle } = useDisclosure({ defaultIsOpen: true })

  // Get entity_data content for JSON display
  const entityDataJson = entity.entity_data || {}

  const formatDateTime = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString()
  }

  return (
    <Box>
      {/* Entity Toggle Button */}
      <HStack mb={3}>
        <IconButton
          aria-label="Toggle entity"
          icon={isEntityOpen ? <FiChevronDown /> : <FiChevronRight />}
          size="sm"
          variant="ghost"
          onClick={onEntityToggle}
        />
        <Text fontSize="lg" fontWeight="bold" color="gray.700">
          Entity: {entity.id}
        </Text>
        <Badge colorScheme="blue" variant="subtle">
          {entity.entity_type || 'Unknown'}
        </Badge>
      </HStack>

      <Collapse in={isEntityOpen}>
        <VStack align="stretch" spacing={4} ml={8}>
          {/* Header Section */}
          <Box>
            <HStack mb={2}>
              <IconButton
                aria-label="Toggle header"
                icon={isHeaderOpen ? <FiChevronDown /> : <FiChevronRight />}
                size="xs"
                variant="ghost"
                onClick={onHeaderToggle}
              />
              <Text fontSize="md" fontWeight="semibold" color="gray.700">
                Header
              </Text>
            </HStack>

            <Collapse in={isHeaderOpen}>
              <Box ml={6} p={3} bg="gray.50" borderRadius="md">
                <VStack align="stretch" spacing={2}>
                  <HStack spacing={8} wrap="wrap">
                    <Box>
                      <Text fontSize="xs" color="gray.500" mb={1}>ID</Text>
                      <Text fontSize="sm" fontFamily="mono">{entity.id}</Text>
                    </Box>
                    {entity.entity_type && (
                      <Box>
                        <Text fontSize="xs" color="gray.500" mb={1}>Type</Text>
                        <Badge colorScheme="blue" variant="outline">{entity.entity_type}</Badge>
                      </Box>
                    )}
                    {entity.run_id && (
                      <Box>
                        <Text fontSize="xs" color="gray.500" mb={1}>Run ID</Text>
                        <Text fontSize="sm" fontFamily="mono">{entity.run_id}</Text>
                      </Box>
                    )}
                  </HStack>

                  <HStack spacing={8} wrap="wrap">
                    <Box>
                      <Text fontSize="xs" color="gray.500" mb={1}>Created</Text>
                      <Text fontSize="sm">{formatDateTime(entity.created_at)}</Text>
                    </Box>
                    <Box>
                      <Text fontSize="xs" color="gray.500" mb={1}>Updated</Text>
                      <Text fontSize="sm">{formatDateTime(entity.updated_at)}</Text>
                    </Box>
                    {entity.callback_timestamp && (
                      <Box>
                        <Text fontSize="xs" color="gray.500" mb={1}>Callback</Text>
                        <Text fontSize="sm">{formatDateTime(entity.callback_timestamp)}</Text>
                      </Box>
                    )}
                  </HStack>
                </VStack>
              </Box>
            </Collapse>
          </Box>

          {/* Entity Section - JSON View */}
          {Object.keys(entityDataJson).length > 0 && (
            <Box>
              <HStack mb={2}>
                <IconButton
                  aria-label="Toggle entity data"
                  icon={isEntityDataOpen ? <FiChevronDown /> : <FiChevronRight />}
                  size="xs"
                  variant="ghost"
                  onClick={onEntityDataToggle}
                />
                <Text fontSize="md" fontWeight="semibold" color="gray.700">
                  Entity
                </Text>
                <Badge colorScheme="green" variant="outline">
                  JSON
                </Badge>
              </HStack>

              <Collapse in={isEntityDataOpen}>
                <Box ml={6}>
                  <Box
                    bg="gray.900"
                    color="white"
                    p={4}
                    borderRadius="md"
                    fontSize="sm"
                    fontFamily="mono"
                    maxH="600px"
                    overflowY="auto"
                  >
                    <Box
                      as="pre"
                      whiteSpace="pre-wrap"
                      margin={0}
                      color="inherit"
                    >
                      {JSON.stringify(entityDataJson, null, 2)}
                    </Box>
                  </Box>
                </Box>
              </Collapse>
            </Box>
          )}
        </VStack>
      </Collapse>
    </Box>
  )
}

interface EntityItemProps {
  entity: EntityData
  searchText: string
}

const EntityItem: React.FC<EntityItemProps> = ({ entity, searchText }) => {
  const { isOpen: isEntityOpen, onToggle: onEntityToggle } = useDisclosure({ defaultIsOpen: true })
  const { isOpen: isHeaderOpen, onToggle: onHeaderToggle } = useDisclosure({ defaultIsOpen: false })
  const { isOpen: isEntityDataOpen, onToggle: onEntityDataToggle } = useDisclosure({ defaultIsOpen: true })

  // Get entity_data content for the properties section
  const entityProperties = entity.entity_data || {}

  const formatDateTime = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString()
  }

  return (
    <Box>
      {/* Entity Toggle Button */}
      <HStack mb={3}>
        <IconButton
          aria-label="Toggle entity"
          icon={isEntityOpen ? <FiChevronDown /> : <FiChevronRight />}
          size="sm"
          variant="ghost"
          onClick={onEntityToggle}
        />
        <Text fontSize="lg" fontWeight="bold" color="gray.700">
          Entity: {entity.id}
        </Text>
        <Badge colorScheme="blue" variant="subtle">
          {entity.entity_type || 'Unknown'}
        </Badge>
      </HStack>

      <Collapse in={isEntityOpen}>
        <VStack align="stretch" spacing={4} ml={8}>
          {/* Header Section */}
          <Box>
            <HStack mb={2}>
              <IconButton
                aria-label="Toggle header"
                icon={isHeaderOpen ? <FiChevronDown /> : <FiChevronRight />}
                size="xs"
                variant="ghost"
                onClick={onHeaderToggle}
              />
              <Text fontSize="md" fontWeight="semibold" color="gray.700">
                Header
              </Text>
            </HStack>

            <Collapse in={isHeaderOpen}>
              <Box ml={6} p={3} bg="gray.50" borderRadius="md">
                <VStack align="stretch" spacing={2}>
                  <HStack spacing={8} wrap="wrap">
                    <Box>
                      <Text fontSize="xs" color="gray.500" mb={1}>ID</Text>
                      <Text fontSize="sm" fontFamily="mono">{entity.id}</Text>
                    </Box>
                    {entity.entity_type && (
                      <Box>
                        <Text fontSize="xs" color="gray.500" mb={1}>Type</Text>
                        <Badge colorScheme="blue" variant="outline">{entity.entity_type}</Badge>
                      </Box>
                    )}
                    {entity.run_id && (
                      <Box>
                        <Text fontSize="xs" color="gray.500" mb={1}>Run ID</Text>
                        <Text fontSize="sm" fontFamily="mono">{entity.run_id}</Text>
                      </Box>
                    )}
                  </HStack>

                  <HStack spacing={8} wrap="wrap">
                    <Box>
                      <Text fontSize="xs" color="gray.500" mb={1}>Created</Text>
                      <Text fontSize="sm">{formatDateTime(entity.created_at)}</Text>
                    </Box>
                    <Box>
                      <Text fontSize="xs" color="gray.500" mb={1}>Updated</Text>
                      <Text fontSize="sm">{formatDateTime(entity.updated_at)}</Text>
                    </Box>
                    {entity.callback_timestamp && (
                      <Box>
                        <Text fontSize="xs" color="gray.500" mb={1}>Callback</Text>
                        <Text fontSize="sm">{formatDateTime(entity.callback_timestamp)}</Text>
                      </Box>
                    )}
                  </HStack>
                </VStack>
              </Box>
            </Collapse>
          </Box>

          {/* Entity Section */}
          {Object.keys(entityProperties).length > 0 && (
            <Box>
              <HStack mb={2}>
                <IconButton
                  aria-label="Toggle entity data"
                  icon={isEntityDataOpen ? <FiChevronDown /> : <FiChevronRight />}
                  size="xs"
                  variant="ghost"
                  onClick={onEntityDataToggle}
                />
                <Text fontSize="md" fontWeight="semibold" color="gray.700">
                  Entity
                </Text>
                <Badge colorScheme="teal" variant="subtle">
                  {Object.keys(entityProperties).length} {Object.keys(entityProperties).length === 1 ? 'property' : 'properties'}
                </Badge>
              </HStack>

              <Collapse in={isEntityDataOpen}>
                <Box ml={6}>
                  <ConfigRenderer
                    data={entityProperties}
                    isEditable={false}
                    filterText={searchText}
                    showAllChildren={false}
                  />
                </Box>
              </Collapse>
            </Box>
          )}
        </VStack>
      </Collapse>
    </Box>
  )
}

export default EntitiesSection