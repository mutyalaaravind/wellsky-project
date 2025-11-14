import React, { useState } from 'react'
import {
  Box,
  Text,
  VStack,
  HStack,
  Input,
  IconButton,
  Collapse,
  useDisclosure,
  Badge,
  Textarea,
  NumberInput,
  NumberInputField,
  Switch,
} from '@chakra-ui/react'
import { FiChevronDown, FiChevronRight, FiEdit2, FiCheck, FiX } from 'react-icons/fi'

interface ConfigRendererProps {
  data: any
  path?: string[]
  level?: number
  isEditable?: boolean
  filterText?: string
  showAllChildren?: boolean
  onUpdate?: (path: string[], value: any) => void
}

interface EditableFieldProps {
  value: any
  onSave: (newValue: any) => void
  onCancel: () => void
}

interface CollapsibleObjectProps {
  objKey: string
  value: any
  path: string[]
  level: number
  isEditable: boolean
  filterText: string
  showAllChildren?: boolean
  onUpdate?: (path: string[], value: any) => void
}

interface CollapsibleArrayProps {
  arrKey: string
  value: any[]
  path: string[]
  level: number
  isEditable: boolean
  filterText: string
  showAllChildren?: boolean
  onUpdate?: (path: string[], value: any) => void
}

const EditableField: React.FC<EditableFieldProps> = ({ value, onSave, onCancel }) => {
  const [editValue, setEditValue] = useState(value)
  const [error, setError] = useState<string | null>(null)

  const handleSave = () => {
    try {
      let parsedValue = editValue
      
      // Try to parse as JSON if it's a string that looks like JSON
      if (typeof editValue === 'string') {
        const trimmed = editValue.trim()
        if ((trimmed.startsWith('{') && trimmed.endsWith('}')) || 
            (trimmed.startsWith('[') && trimmed.endsWith(']'))) {
          parsedValue = JSON.parse(editValue)
        } else if (trimmed === 'true' || trimmed === 'false') {
          parsedValue = trimmed === 'true'
        } else if (!isNaN(Number(trimmed)) && trimmed !== '') {
          parsedValue = Number(trimmed)
        }
      }
      
      onSave(parsedValue)
      setError(null)
    } catch (err) {
      setError('Invalid JSON format')
    }
  }

  const renderEditor = () => {
    if (typeof value === 'boolean') {
      return (
        <Switch
          isChecked={editValue}
          onChange={(e) => setEditValue(e.target.checked)}
          size="sm"
        />
      )
    }
    
    if (typeof value === 'number') {
      return (
        <NumberInput
          value={editValue}
          onChange={(valueString) => setEditValue(Number(valueString))}
          size="sm"
          maxW="200px"
        >
          <NumberInputField />
        </NumberInput>
      )
    }
    
    if (typeof value === 'string' && value.length > 50) {
      return (
        <Textarea
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          size="sm"
          resize="vertical"
          minH="60px"
        />
      )
    }
    
    if (typeof value === 'object') {
      return (
        <Textarea
          value={typeof editValue === 'string' ? editValue : JSON.stringify(editValue, null, 2)}
          onChange={(e) => setEditValue(e.target.value)}
          size="sm"
          resize="vertical"
          minH="100px"
          fontFamily="mono"
        />
      )
    }
    
    return (
      <Input
        value={editValue}
        onChange={(e) => setEditValue(e.target.value)}
        size="sm"
        maxW="300px"
      />
    )
  }

  return (
    <VStack align="stretch" spacing={2}>
      <HStack>
        {renderEditor()}
        <IconButton
          aria-label="Save"
          icon={<FiCheck />}
          size="sm"
          colorScheme="green"
          onClick={handleSave}
        />
        <IconButton
          aria-label="Cancel"
          icon={<FiX />}
          size="sm"
          variant="outline"
          onClick={onCancel}
        />
      </HStack>
      {error && (
        <Text color="red.500" fontSize="sm">
          {error}
        </Text>
      )}
    </VStack>
  )
}

const CollapsibleObject: React.FC<CollapsibleObjectProps> = ({
  objKey,
  value,
  path,
  level,
  isEditable,
  filterText,
  showAllChildren = false,
  onUpdate
}) => {
  const { isOpen, onToggle } = useDisclosure({ defaultIsOpen: level < 2 })
  const fullPath = [...path, objKey]

  return (
    <VStack align="stretch" spacing={1}>
      <HStack>
        <IconButton
          aria-label="Toggle"
          icon={isOpen ? <FiChevronDown /> : <FiChevronRight />}
          size="xs"
          variant="ghost"
          onClick={onToggle}
        />
        <Text fontWeight="medium" color="gray.700">
          {objKey}
        </Text>
        <Badge colorScheme="teal" variant="subtle" fontSize="xs">
          object{`{${Object.keys(value).length}}`}
        </Badge>
      </HStack>
      <Collapse in={isOpen}>
        <Box ml={6} borderLeft="2px" borderColor="gray.200" pl={4}>
          <ConfigRenderer
            data={value}
            path={fullPath}
            level={level + 1}
            isEditable={isEditable}
            filterText={showAllChildren ? '' : filterText}
            showAllChildren={showAllChildren}
            onUpdate={onUpdate}
          />
        </Box>
      </Collapse>
    </VStack>
  )
}

const CollapsibleArray: React.FC<CollapsibleArrayProps> = ({
  arrKey,
  value,
  path,
  level,
  isEditable,
  filterText,
  showAllChildren = false,
  onUpdate
}) => {
  const { isOpen, onToggle } = useDisclosure({ defaultIsOpen: level < 2 })
  const fullPath = [...path, arrKey]

  // Filter function to check if key or value matches filter text
  const matchesFilter = (key: string, item: any, searchText: string): boolean => {
    if (!searchText.trim()) return true
    
    const lowerSearchText = searchText.toLowerCase()
    
    // Check if key matches
    if (key.toLowerCase().includes(lowerSearchText)) return true
    
    // Check if value matches (for primitive values)
    if (typeof item === 'string' && item.toLowerCase().includes(lowerSearchText)) return true
    if (typeof item === 'number' && item.toString().includes(lowerSearchText)) return true
    if (typeof item === 'boolean' && item.toString().toLowerCase().includes(lowerSearchText)) return true
    
    // For objects and arrays, check recursively
    if (typeof item === 'object' && item !== null) {
      if (Array.isArray(item)) {
        return item.some((subItem, index) => matchesFilter(index.toString(), subItem, searchText))
      } else {
        return Object.entries(item).some(([nestedKey, nestedValue]) => 
          matchesFilter(nestedKey, nestedValue, searchText)
        )
      }
    }
    
    return false
  }

  const getValueTypeColor = (item: any): string => {
    if (item === null) return 'gray'
    if (typeof item === 'boolean') return 'purple'
    if (typeof item === 'number') return 'blue'
    if (typeof item === 'string') return 'green'
    if (Array.isArray(item)) return 'orange'
    if (typeof item === 'object') return 'teal'
    return 'gray'
  }

  const getValueTypeBadge = (item: any): string => {
    if (item === null) return 'null'
    if (typeof item === 'boolean') return 'boolean'
    if (typeof item === 'number') return 'number'
    if (typeof item === 'string') return 'string'
    if (Array.isArray(item)) return `array[${item.length}]`
    if (typeof item === 'object') return `object{${Object.keys(item).length}}`
    return 'unknown'
  }

  const renderValue = (item: any, _index: number, _currentPath: string[]) => {
    if (item === null) {
      return <Text color="gray.500" fontStyle="italic">null</Text>
    }

    if (typeof item === 'boolean') {
      return <Text color={item ? 'green.600' : 'red.600'}>{item.toString()}</Text>
    }

    if (typeof item === 'number') {
      return <Text color="blue.600">{item}</Text>
    }

    if (typeof item === 'string') {
      return (
        <Text 
          color="gray.700" 
          maxW="400px" 
          isTruncated={item.length > 100}
          title={item.length > 100 ? item : undefined}
        >
          "{item}"
        </Text>
      )
    }

    return null
  }

  const filteredItems = showAllChildren ? 
    value.map((item, index) => ({ item, index })) :
    value
      .map((item, index) => ({ item, index }))
      .filter(({ item, index }) => matchesFilter(index.toString(), item, filterText))

  return (
    <VStack align="stretch" spacing={1}>
      <HStack>
        <IconButton
          aria-label="Toggle"
          icon={isOpen ? <FiChevronDown /> : <FiChevronRight />}
          size="xs"
          variant="ghost"
          onClick={onToggle}
        />
        <Text fontWeight="medium" color="gray.700">
          {arrKey}
        </Text>
        <Badge colorScheme="orange" variant="subtle" fontSize="xs">
          array[{value.length}]
        </Badge>
      </HStack>
      <Collapse in={isOpen}>
        <Box ml={6} borderLeft="2px" borderColor="gray.200" pl={4}>
          <VStack align="stretch" spacing={2}>
            {filteredItems.map(({ item, index }) => (
              <Box key={index}>
                <HStack>
                  <Text fontSize="sm" color="gray.600" minW="50px">
                    [{index}]
                  </Text>
                  <Badge 
                    colorScheme={getValueTypeColor(item)} 
                    variant="outline" 
                    fontSize="xs"
                  >
                    {getValueTypeBadge(item)}
                  </Badge>
                </HStack>
                <Box ml={4}>
                  {typeof item === 'object' && item !== null ? (
                    <ConfigRenderer
                      data={item}
                      path={[...fullPath, index.toString()]}
                      level={level + 1}
                      isEditable={isEditable}
                      filterText={showAllChildren ? '' : filterText}
                      showAllChildren={showAllChildren}
                      onUpdate={onUpdate}
                    />
                  ) : (
                    renderValue(item, index, fullPath)
                  )}
                </Box>
              </Box>
            ))}
          </VStack>
        </Box>
      </Collapse>
    </VStack>
  )
}

const ConfigRenderer: React.FC<ConfigRendererProps> = ({
  data,
  path = [],
  level = 0,
  isEditable = false,
  filterText = '',
  showAllChildren = false,
  onUpdate
}) => {
  const [editingKey, setEditingKey] = useState<string | null>(null)
  
  // Filter function to check if key or value matches filter text
  const matchesFilter = (key: string, value: any, searchText: string): boolean => {
    if (!searchText.trim()) return true
    
    const lowerSearchText = searchText.toLowerCase()
    
    // Check if key matches
    if (key.toLowerCase().includes(lowerSearchText)) return true
    
    // Check if value matches (for primitive values)
    if (typeof value === 'string' && value.toLowerCase().includes(lowerSearchText)) return true
    if (typeof value === 'number' && value.toString().includes(lowerSearchText)) return true
    if (typeof value === 'boolean' && value.toString().toLowerCase().includes(lowerSearchText)) return true
    
    // For objects and arrays, check recursively
    if (typeof value === 'object' && value !== null) {
      if (Array.isArray(value)) {
        return value.some((item, index) => matchesFilter(index.toString(), item, searchText))
      } else {
        return Object.entries(value).some(([nestedKey, nestedValue]) => 
          matchesFilter(nestedKey, nestedValue, searchText)
        )
      }
    }
    
    return false
  }
  
  const getValueTypeColor = (value: any): string => {
    if (value === null) return 'gray'
    if (typeof value === 'boolean') return 'purple'
    if (typeof value === 'number') return 'blue'
    if (typeof value === 'string') return 'green'
    if (Array.isArray(value)) return 'orange'
    if (typeof value === 'object') return 'teal'
    return 'gray'
  }

  const getValueTypeBadge = (value: any): string => {
    if (value === null) return 'null'
    if (typeof value === 'boolean') return 'boolean'
    if (typeof value === 'number') return 'number'
    if (typeof value === 'string') return 'string'
    if (Array.isArray(value)) return `array[${value.length}]`
    if (typeof value === 'object') return `object{${Object.keys(value).length}}`
    return 'unknown'
  }

  const renderValue = (value: any, key: string, currentPath: string[]) => {
    const isEditing = editingKey === key
    const fullPath = [...currentPath, key]

    if (isEditing && isEditable && onUpdate) {
      return (
        <EditableField
          value={value}
          onSave={(newValue) => {
            onUpdate(fullPath, newValue)
            setEditingKey(null)
          }}
          onCancel={() => setEditingKey(null)}
        />
      )
    }

    if (value === null) {
      return <Text color="gray.500" fontStyle="italic">null</Text>
    }

    if (typeof value === 'boolean') {
      return <Text color={value ? 'green.600' : 'red.600'}>{value.toString()}</Text>
    }

    if (typeof value === 'number') {
      return <Text color="blue.600">{value}</Text>
    }

    if (typeof value === 'string') {
      return (
        <Text 
          color="gray.700" 
          maxW="400px" 
          isTruncated={value.length > 100}
          title={value.length > 100 ? value : undefined}
        >
          "{value}"
        </Text>
      )
    }

    return null
  }

  // Early validation - ensure we have data
  const hasValidData = data && typeof data === 'object'
  
  // Check if current item directly matches the filter (for determining if children should show all)
  const currentItemMatches = (key: string, value: any, searchText: string): boolean => {
    if (!searchText.trim()) return false
    const lowerSearchText = searchText.toLowerCase()
    return key.toLowerCase().includes(lowerSearchText) || 
           (typeof value === 'string' && value.toLowerCase().includes(lowerSearchText)) ||
           (typeof value === 'number' && value.toString().includes(lowerSearchText)) ||
           (typeof value === 'boolean' && value.toString().toLowerCase().includes(lowerSearchText))
  }

  // Filter entries based on filter text
  const filteredEntries = hasValidData ? 
    (showAllChildren ? 
      Object.entries(data) : 
      Object.entries(data).filter(([key, value]) => matchesFilter(key, value, filterText))
    ) : []

  const hasFilteredResults = filteredEntries.length > 0 || !filterText.trim()

  // Handle no data case
  if (!hasValidData) {
    return <Text color="gray.500">No configuration data available</Text>
  }

  // Handle no filter results case
  if (!hasFilteredResults) {
    return (
      <Box p={4} textAlign="center">
        <Text color="gray.500">No configuration items match the filter "{filterText}"</Text>
      </Box>
    )
  }

  return (
    <VStack align="stretch" spacing={3}>
      {filteredEntries.map(([key, value]) => (
        <Box key={key} p={3} bg="white" borderRadius="md" border="1px" borderColor="gray.100">
          {Array.isArray(value) ? (
            <CollapsibleArray
              arrKey={key}
              value={value}
              path={path}
              level={level}
              isEditable={isEditable}
              filterText={filterText}
              showAllChildren={showAllChildren || currentItemMatches(key, value, filterText)}
              onUpdate={onUpdate}
            />
          ) : typeof value === 'object' && value !== null ? (
            <CollapsibleObject
              objKey={key}
              value={value}
              path={path}
              level={level}
              isEditable={isEditable}
              filterText={filterText}
              showAllChildren={showAllChildren || currentItemMatches(key, value, filterText)}
              onUpdate={onUpdate}
            />
          ) : (
            <VStack align="stretch" spacing={2}>
              <HStack justify="space-between">
                <HStack>
                  <Text fontWeight="medium" color="gray.700">
                    {key}
                  </Text>
                  <Badge 
                    colorScheme={getValueTypeColor(value)} 
                    variant="outline" 
                    fontSize="xs"
                  >
                    {getValueTypeBadge(value)}
                  </Badge>
                </HStack>
                {isEditable && onUpdate && (
                  <IconButton
                    aria-label="Edit"
                    icon={<FiEdit2 />}
                    size="xs"
                    variant="ghost"
                    onClick={() => setEditingKey(key)}
                  />
                )}
              </HStack>
              <Box ml={4}>
                {renderValue(value, key, path)}
              </Box>
            </VStack>
          )}
        </Box>
      ))}
    </VStack>
  )
}

export default ConfigRenderer