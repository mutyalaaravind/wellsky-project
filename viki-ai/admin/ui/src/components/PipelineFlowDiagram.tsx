import React, { useMemo, useCallback, useState, useEffect } from 'react'
import {
  Box,
  Text,
  VStack,
  HStack,
  Badge,
  IconButton,
  Tooltip,
  useDisclosure,
} from '@chakra-ui/react'
import {
  ReactFlow,
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  ConnectionMode,
  ReactFlowProvider,
  addEdge,
  Connection,
  Handle,
  Position,
  MarkerType,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { FiSettings } from 'react-icons/fi'
import { TaskConfig } from '../services/pipelinesService'
import TaskEditModal from './TaskEditModal'

// Custom node component for tasks
const TaskNode = ({ data }: { data: any }) => {
  const { task, onTaskSetup } = data

  const getTaskTypeColor = (type: string) => {
    switch (type) {
      case 'module': return '#3182ce' // blue.500
      case 'pipeline': return '#805ad5' // purple.500
      case 'prompt': return '#38a169' // green.500
      case 'remote': return '#dd6b20' // orange.500
      case 'publish_callback': return '#d53f8c' // pink.500
      default: return '#718096' // gray.500
    }
  }

  const getTaskIcon = (type: string) => {
    switch (type) {
      case 'module': return '⚙️'
      case 'pipeline': return '🔗'
      case 'prompt': return '🤖'
      case 'remote': return '🌐'
      case 'publish_callback': return '📡'
      default: return '📋'
    }
  }

  const getBorderColor = (type: string) => {
    const color = getTaskTypeColor(type)
    return `${color}80` // Add transparency
  }

  const hasForEach = task.post_processing?.for_each

  return (
    <Box
      bg="white"
      border="2px solid"
      borderColor={getBorderColor(task.type)}
      borderRadius="lg"
      p={4}
      minW="200px"
      maxW="250px"
      shadow="md"
      _hover={{ 
        shadow: "lg",
        transform: "translateY(-1px)"
      }}
      transition="all 0.2s"
    >
      <VStack spacing={2} align="start">
        <HStack justify="space-between" w="full">
          <HStack>
            <Text fontSize="lg">{getTaskIcon(task.type)}</Text>
            <Badge 
              bg={getTaskTypeColor(task.type)}
              color="white"
              size="sm"
              borderRadius="md"
            >
              {task.type}
            </Badge>
          </HStack>
          <Tooltip label="Configure Task" placement="top">
            <IconButton
              aria-label="Configure task"
              icon={<FiSettings />}
              size="xs"
              variant="ghost"
              colorScheme="gray"
              onClick={(e) => {
                e.stopPropagation()
                onTaskSetup?.(task)
              }}
              _hover={{
                bg: 'gray.100',
                color: getTaskTypeColor(task.type)
              }}
            />
          </Tooltip>
        </HStack>
        
        <Text fontWeight="bold" fontSize="sm" color="gray.800" noOfLines={1}>
          {task.id}
        </Text>
        
        {/* Task details based on type */}
        {task.type === 'module' && task.module && (
          <Text fontSize="xs" color="gray.600">
            Module: {task.module.type}
          </Text>
        )}
        
        {task.type === 'prompt' && task.prompt && (
          <Text fontSize="xs" color="gray.600" noOfLines={2}>
            Model: {task.prompt.model}
          </Text>
        )}
        
        {task.type === 'remote' && task.remote && (
          <Text fontSize="xs" color="gray.600" noOfLines={1}>
            URL: {new URL(task.remote.url).hostname}
          </Text>
        )}
        
        {task.type === 'pipeline' && task.pipelines && task.pipelines.length > 0 && (
          <Text fontSize="xs" color="gray.600">
            Pipeline: {task.pipelines[0].id}
          </Text>
        )}

        {/* For Each indicator */}
        {hasForEach && (
          <Badge colorScheme="orange" size="sm" variant="subtle">
            ⚡ For Each: {task.post_processing.for_each}
          </Badge>
        )}
      </VStack>
      
      {/* React Flow handles */}
      <Handle
        type="target"
        position={Position.Left}
        style={{
          left: -8,
          backgroundColor: getTaskTypeColor(task.type),
          border: '2px solid white',
          width: 12,
          height: 12
        }}
      />
      <Handle
        type="source"
        position={Position.Right}
        style={{
          right: -8,
          backgroundColor: getTaskTypeColor(task.type),
          border: '2px solid white',
          width: 12,
          height: 12
        }}
      />
    </Box>
  )
}

// Start node component
const StartNode = () => (
  <Box
    bg="green.100"
    border="2px solid"
    borderColor="green.400"
    borderRadius="full"
    w="80px"
    h="80px"
    display="flex"
    alignItems="center"
    justifyContent="center"
    flexDirection="column"
  >
    <Text fontSize="2xl">🚀</Text>
    <Text fontSize="xs" color="green.700" fontWeight="bold">START</Text>
    <Handle
      type="source"
      position={Position.Right}
      style={{
        right: -8,
        backgroundColor: '#38a169',
        border: '2px solid white',
        width: 12,
        height: 12
      }}
    />
  </Box>
)

// End node component
const EndNode = () => (
  <Box
    bg="red.100"
    border="2px solid"
    borderColor="red.400"
    borderRadius="full"
    w="80px"
    h="80px"
    display="flex"
    alignItems="center"
    justifyContent="center"
    flexDirection="column"
  >
    <Text fontSize="2xl">🏁</Text>
    <Text fontSize="xs" color="red.700" fontWeight="bold">END</Text>
    <Handle
      type="target"
      position={Position.Left}
      style={{
        left: -8,
        backgroundColor: '#e53e3e',
        border: '2px solid white',
        width: 12,
        height: 12
      }}
    />
  </Box>
)

const nodeTypes = {
  taskNode: TaskNode,
  startNode: StartNode,
  endNode: EndNode,
}

interface PipelineFlowDiagramProps {
  tasks: TaskConfig[]
  pipelineId: string
  onTaskUpdate: (updatedTask: TaskConfig) => Promise<void>
}

const PipelineFlowContent: React.FC<{ tasks: TaskConfig[]; pipelineId: string; onTaskUpdate: (updatedTask: TaskConfig) => Promise<void> }> = ({ tasks, pipelineId: _pipelineId, onTaskUpdate }) => {
  const { isOpen, onOpen, onClose } = useDisclosure()
  const [selectedTask, setSelectedTask] = useState<TaskConfig | undefined>()
  
  const handleTaskSetup = useCallback((task: TaskConfig) => {
    console.log('Setup task:', task)
    setSelectedTask(task)
    onOpen()
  }, [onOpen])

  const handleTaskSave = useCallback(async (updatedTask: TaskConfig) => {
    console.log('Saving task:', updatedTask)
    try {
      await onTaskUpdate(updatedTask)
      onClose()
    } catch (error) {
      console.error('Failed to save task:', error)
      // Error handling is done in the parent component
    }
  }, [onTaskUpdate, onClose])
  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
    if (!tasks || tasks.length === 0) {
      return { nodes: [], edges: [] }
    }

    const nodes: Node[] = []
    const edges: Edge[] = []
    
    const nodeSpacing = 300
    const yPosition = 100

    // Start node
    nodes.push({
      id: 'start',
      type: 'startNode',
      position: { x: 0, y: yPosition },
      data: {},
    })

    // Task nodes
    tasks.forEach((task, index) => {
      const nodeId = `task-${index}`
      const xPosition = (index + 1) * nodeSpacing
      
      nodes.push({
        id: nodeId,
        type: 'taskNode',
        position: { x: xPosition, y: yPosition },
        data: { task, taskType: task.type, onTaskSetup: handleTaskSetup },
      })
    })

    // End node
    const endXPosition = (tasks.length + 1) * nodeSpacing
    nodes.push({
      id: 'end',
      type: 'endNode',
      position: { x: endXPosition, y: yPosition },
      data: {},
    })

    // Create edges
    // Start to first task
    if (tasks.length > 0) {
      edges.push({
        id: 'start-to-task-0',
        source: 'start',
        target: 'task-0',
        type: 'smoothstep',
        style: { stroke: '#38a169', strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#38a169' },
      })
    }

    // Between tasks
    tasks.forEach((task, index) => {
      if (index < tasks.length - 1) {
        const sourceId = `task-${index}`
        const targetId = `task-${index + 1}`
        const hasForEach = task.post_processing?.for_each
        
        edges.push({
          id: `${sourceId}-to-${targetId}`,
          source: sourceId,
          target: targetId,
          type: 'smoothstep',
          style: { 
            stroke: hasForEach ? '#dd6b20' : '#718096', 
            strokeWidth: hasForEach ? 3 : 2,
            strokeDasharray: hasForEach ? '5,5' : undefined
          },
          markerEnd: { 
            type: MarkerType.ArrowClosed, 
            color: hasForEach ? '#dd6b20' : '#718096' 
          },
          label: hasForEach ? '⚡ For Each' : undefined,
          labelStyle: { 
            fontSize: '12px', 
            fontWeight: 'bold',
            fill: '#dd6b20'
          },
          labelBgStyle: { fill: '#fff', fillOpacity: 0.8 },
        })
      }
    })

    // Last task to end
    if (tasks.length > 0) {
      edges.push({
        id: `task-${tasks.length - 1}-to-end`,
        source: `task-${tasks.length - 1}`,
        target: 'end',
        type: 'smoothstep',
        style: { stroke: '#e53e3e', strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#e53e3e' },
      })
    }

    return { nodes, edges }
  }, [tasks, handleTaskSetup])

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  // Sync React Flow's internal state when tasks prop updates
  useEffect(() => {
    setNodes(initialNodes)
  }, [initialNodes, setNodes])

  useEffect(() => {
    setEdges(initialEdges)
  }, [initialEdges, setEdges])

  const onConnect = useCallback(
    (params: Connection) => {
      console.log('Connection created:', params)
      
      // Create new edge with custom styling
      const newEdge: Edge = {
        ...params,
        id: `${params.source}-${params.target}`,
        type: 'smoothstep',
        style: { 
          stroke: '#718096', 
          strokeWidth: 2
        },
        markerEnd: { 
          type: MarkerType.ArrowClosed, 
          color: '#718096' 
        },
      }
      
      setEdges((eds) => addEdge(newEdge, eds))
    },
    [setEdges]
  )

  const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
    console.log('Node clicked:', node)
    // TODO: Handle node click for editing
  }, [])

  const onEdgeClick = useCallback((_event: React.MouseEvent, edge: Edge) => {
    console.log('Edge clicked:', edge)
    // TODO: Handle edge click for editing/deletion
  }, [])

  if (!tasks || tasks.length === 0) {
    return (
      <Box 
        height="400px" 
        display="flex" 
        alignItems="center" 
        justifyContent="center"
        bg="gray.50"
        borderRadius="md"
      >
        <VStack spacing={2}>
          <Text color="gray.500" fontSize="lg">No Pipeline Tasks</Text>
          <Text color="gray.400" fontSize="sm">Add tasks to see the pipeline flow</Text>
        </VStack>
      </Box>
    )
  }

  return (
    <Box height="500px" width="100%" border="1px solid" borderColor="gray.200" borderRadius="md">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        onEdgeClick={onEdgeClick}
        nodeTypes={nodeTypes}
        connectionMode={ConnectionMode.Loose}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        attributionPosition="bottom-left"
        defaultEdgeOptions={{
          style: { strokeWidth: 2, stroke: '#718096' },
          markerEnd: { type: MarkerType.ArrowClosed, color: '#718096' },
        }}
      >
        <Background color="#f7fafc" gap={20} />
        <Controls showInteractive={false} />
      </ReactFlow>

      {/* Task Edit Modal */}
      <TaskEditModal
        isOpen={isOpen}
        onClose={onClose}
        onSave={handleTaskSave}
        task={selectedTask}
      />
    </Box>
  )
}

const PipelineFlowDiagram: React.FC<PipelineFlowDiagramProps> = ({ tasks, pipelineId, onTaskUpdate }) => {
  return (
    <ReactFlowProvider>
      <PipelineFlowContent tasks={tasks} pipelineId={pipelineId} onTaskUpdate={onTaskUpdate} />
    </ReactFlowProvider>
  )
}

export default PipelineFlowDiagram