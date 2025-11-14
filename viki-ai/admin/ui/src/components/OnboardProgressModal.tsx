import React, { useCallback } from 'react'
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  VStack,
  HStack,
  Text,
  Progress,
  Button,
  Box,
  Icon,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Circle,
  useToast
} from '@chakra-ui/react'
import { FaCheck, FaExclamationTriangle } from 'react-icons/fa'
import { useOnboardProgress, type OnboardProgress, type OnboardTask } from '../hooks/useOnboardProgress'

interface OnboardProgressModalProps {
  isOpen: boolean
  onClose: () => void
  jobId: string | null
  onComplete?: (progress: OnboardProgress) => void
  onCancel?: () => void
  title?: string
}

const TaskStatusIcon: React.FC<{ status: OnboardTask['status'] }> = ({ status }) => {
  switch (status) {
    case 'COMPLETED':
      return (
        <Circle size="24px" bg="green.500" color="white">
          <Icon as={FaCheck} boxSize="12px" />
        </Circle>
      )
    case 'IN_PROGRESS':
      return (
        <Circle size="24px" bg="blue.500" color="white">
          <Spinner size="xs" color="white" />
        </Circle>
      )
    case 'FAILED':
      return (
        <Circle size="24px" bg="red.500" color="white">
          <Icon as={FaExclamationTriangle} boxSize="12px" />
        </Circle>
      )
    default:
      return (
        <Circle size="24px" bg="gray.300" color="gray.600">
          <Box w="8px" h="8px" bg="currentColor" borderRadius="full" />
        </Circle>
      )
  }
}

const TaskItem: React.FC<{ task: OnboardTask; isActive: boolean }> = ({ task, isActive }) => {
  const getStatusColor = (status: OnboardTask['status']) => {
    switch (status) {
      case 'COMPLETED': return 'green.600'
      case 'IN_PROGRESS': return 'blue.600'
      case 'FAILED': return 'red.600'
      default: return 'gray.500'
    }
  }

  const getStatusText = (status: OnboardTask['status']) => {
    switch (status) {
      case 'COMPLETED': return 'Completed'
      case 'IN_PROGRESS': return 'In Progress'
      case 'FAILED': return 'Failed'
      default: return 'Pending'
    }
  }

  return (
    <HStack spacing={4} p={3} bg={isActive ? 'blue.50' : 'transparent'} borderRadius="md">
      <TaskStatusIcon status={task.status} />
      <VStack align="start" spacing={1} flex={1}>
        <Text fontWeight="medium" color={getStatusColor(task.status)}>
          {task.name}
        </Text>
        <Text fontSize="sm" color="gray.600">
          {task.description}
        </Text>
        {task.status === 'IN_PROGRESS' && (
          <Box w="full" mt={2}>
            <Progress 
              value={task.progress_percentage} 
              size="sm" 
              colorScheme="blue"
              borderRadius="md"
            />
          </Box>
        )}
      </VStack>
      <Text fontSize="sm" color={getStatusColor(task.status)} minW="80px" textAlign="right">
        {getStatusText(task.status)}
      </Text>
    </HStack>
  )
}

export const OnboardProgressModal: React.FC<OnboardProgressModalProps> = ({
  isOpen,
  onClose,
  jobId,
  onComplete,
  onCancel,
  title = "Generating Configuration"
}) => {
  const toast = useToast()

  const handleComplete = useCallback((progress: OnboardProgress) => {
    toast({
      title: 'Configuration Complete',
      description: 'Your onboarding configuration has been successfully generated.',
      status: 'success',
      duration: 3000,
      isClosable: true,
    })
    onComplete?.(progress)
  }, [toast, onComplete])

  const handleError = useCallback((error: string) => {
    toast({
      title: 'Configuration Failed',
      description: error,
      status: 'error',
      duration: 5000,
      isClosable: true,
    })
  }, [toast])

  const {
    progress: realProgress,
    isLoading,
    error,
    cancelJob,
    retry
  } = useOnboardProgress({
    jobId,
    enabled: isOpen && !!jobId,
    onComplete: handleComplete,
    onError: handleError
  })

  // Use real progress data from DJT/Admin API
  const progress = realProgress

  const handleCancel = async () => {
    try {
      await cancelJob()
      toast({
        title: 'Job Cancelled',
        description: 'The configuration generation has been cancelled.',
        status: 'info',
        duration: 3000,
        isClosable: true,
      })
      onCancel?.()
      onClose()
    } catch (err) {
      // Error toast is already shown by the hook
    }
  }

  const handleRetry = () => {
    retry()
  }

  const isComplete = progress?.status === 'COMPLETED'
  const isFailed = progress?.status === 'FAILED'
  const isCancelled = progress?.status === 'CANCELLED'

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={isComplete ? onClose : () => {}} 
      closeOnOverlayClick={false}
      closeOnEsc={false}
      size="lg"
    >
      <ModalOverlay bg="blackAlpha.600" />
      <ModalContent>
        <ModalHeader>
          <VStack align="start" spacing={2}>
            <Text>{title}</Text>
            {progress && (
              <Box w="full">
                <HStack justify="space-between" mb={2}>
                  <Text fontSize="sm" color="gray.600">
                    Overall Progress
                  </Text>
                  <Text fontSize="sm" fontWeight="medium">
                    {progress.overall_progress_percentage}%
                  </Text>
                </HStack>
                <Progress 
                  value={progress.overall_progress_percentage} 
                  colorScheme={isFailed ? "red" : isComplete ? "green" : "blue"}
                  size="lg"
                  borderRadius="md"
                />
              </Box>
            )}
          </VStack>
        </ModalHeader>

        <ModalBody>
          <VStack spacing={4} align="stretch">
            {error && !progress && (
              <Alert status="error">
                <AlertIcon />
                <Box>
                  <AlertTitle>Error!</AlertTitle>
                  <AlertDescription>{error}</AlertDescription>
                </Box>
              </Alert>
            )}

            {isFailed && progress?.error_message && (
              <Alert status="error">
                <AlertIcon />
                <Box>
                  <AlertTitle>Generation Failed!</AlertTitle>
                  <AlertDescription>{progress.error_message}</AlertDescription>
                </Box>
              </Alert>
            )}

            {isCancelled && (
              <Alert status="warning">
                <AlertIcon />
                <Box>
                  <AlertTitle>Job Cancelled</AlertTitle>
                  <AlertDescription>The configuration generation was cancelled.</AlertDescription>
                </Box>
              </Alert>
            )}

            {isComplete && (
              <Alert status="success">
                <AlertIcon />
                <Box>
                  <AlertTitle>Configuration Complete!</AlertTitle>
                  <AlertDescription>Your configuration has been successfully generated.</AlertDescription>
                </Box>
              </Alert>
            )}

            {!jobId && !error && (
              <HStack justify="center" py={8}>
                <Spinner size="lg" color="blue.500" />
                <Text>Starting generation...</Text>
              </HStack>
            )}

            {jobId && !progress && !error && isLoading && (
              <HStack justify="center" py={8}>
                <Spinner size="lg" color="blue.500" />
                <Text>Initializing progress tracking...</Text>
              </HStack>
            )}

            {progress && progress.tasks && progress.tasks.length > 0 && (
              <VStack spacing={2} align="stretch">
                <Text fontWeight="medium" mb={2}>Task Progress:</Text>
                {progress.tasks.map((task) => (
                  <TaskItem 
                    key={task.id} 
                    task={task} 
                    isActive={task.id === progress.current_task}
                  />
                ))}
              </VStack>
            )}

            {progress?.current_task_name && !isComplete && !isFailed && (
              <Box bg="blue.50" p={3} borderRadius="md">
                <Text fontSize="sm" color="blue.800" fontWeight="medium">
                  Currently processing: {progress.current_task_name}
                </Text>
              </Box>
            )}
          </VStack>
        </ModalBody>

        <ModalFooter>
          <HStack spacing={3}>
            {error && !progress && (
              <Button colorScheme="blue" onClick={handleRetry}>
                Retry
              </Button>
            )}
            
            {isComplete && (
              <Button colorScheme="green" onClick={onClose}>
                Continue
              </Button>
            )}
            
            {(isFailed || isCancelled) && (
              <Button variant="outline" onClick={onClose}>
                Close
              </Button>
            )}
            
            {!isComplete && !isFailed && !isCancelled && (
              <Button 
                variant="outline" 
                onClick={handleCancel}
                isLoading={isLoading}
                loadingText="Cancelling..."
              >
                Cancel
              </Button>
            )}
          </HStack>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

export default OnboardProgressModal