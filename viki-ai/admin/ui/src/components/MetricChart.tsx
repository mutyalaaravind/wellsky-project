import React, { useState, useEffect } from 'react'
import {
  Box,
  Text,
  VStack,
  HStack,
  Spinner,
  Alert,
  AlertIcon,
  Badge,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Button,
} from '@chakra-ui/react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { FiRefreshCw } from 'react-icons/fi'
import { configService } from '../services/configService'
import { getAuthToken } from '../utils/auth'

interface MetricData {
  metric_name: string
  project_id: string
  time_range: {
    start: string
    end: string
    hours_back: number
  }
  aggregation_period_minutes: number
  statistics: {
    total_count: number
    data_points: number
    average: number
    min: number
    max: number
  }
  time_series: Array<{
    timestamp: string
    value: number
  }>
  status: string
  mode?: string
}

interface MetricChartProps {
  metricName: string
  title?: string
  description?: string
  color?: string
  hoursBack?: number
  aggregationPeriod?: number
}

const MetricChart: React.FC<MetricChartProps> = ({
  metricName,
  title,
  description,
  color = '#3182CE',
  hoursBack = 24,
  aggregationPeriod = 60
}) => {
  const [data, setData] = useState<MetricData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)


  const fetchMetricData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const apiBaseUrl = await configService.getAdminApiUrl()
      const token = getAuthToken()
      
      const response = await fetch(
        `${apiBaseUrl}/api/v1/metrics/${metricName}?hours_back=${hoursBack}&aggregation_period_minutes=${aggregationPeriod}`,
        {
          headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` }),
          },
        }
      )
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch metric data`)
      }
      
      const result = await response.json()
      if (result.success) {
        setData(result.data)
      } else {
        throw new Error('Failed to retrieve metric data')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMetricData()
  }, [metricName, hoursBack, aggregationPeriod])

  const formatChartData = (timeSeriesData: Array<{ timestamp: string; value: number }>) => {
    return timeSeriesData.map(point => ({
      timestamp: point.timestamp,
      value: point.value,
      formattedTime: new Date(point.timestamp).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }))
  }

  const formatTooltipLabel = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Heading size="md">{title || metricName}</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="center" py={8}>
            <Spinner size="lg" color={color} />
            <Text color="gray.500">Loading metric data...</Text>
          </VStack>
        </CardBody>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <Heading size="md">{title || metricName}</Heading>
        </CardHeader>
        <CardBody>
          <Alert status="error">
            <AlertIcon />
            {error}
          </Alert>
        </CardBody>
      </Card>
    )
  }

  if (!data) {
    return null
  }

  const chartData = formatChartData(data.time_series)

  return (
    <Card>
      <CardHeader>
        <VStack spacing={3} align="stretch">
          <HStack justify="space-between" align="start">
            <VStack align="start" spacing={1}>
              <Heading size="md">{title || metricName}</Heading>
              {description && (
                <Text fontSize="sm" color="gray.600">{description}</Text>
              )}
            </VStack>
            <HStack spacing={2}>
              {data.mode === 'emulator' && (
                <Badge colorScheme="orange" variant="subtle">Mock Data</Badge>
              )}
              <Button
                size="sm"
                variant="ghost"
                leftIcon={<FiRefreshCw />}
                onClick={fetchMetricData}
              >
                Refresh
              </Button>
            </HStack>
          </HStack>
        </VStack>
      </CardHeader>
      
      <CardBody>
        <VStack spacing={6} align="stretch">
          {/* Statistics Summary */}
          <HStack spacing={6} wrap="wrap">
            <VStack align="start" spacing={1}>
              <Text fontSize="sm" color="gray.600">Total</Text>
              <Text fontSize="lg" fontWeight="bold">{data.statistics.total_count.toLocaleString()}</Text>
            </VStack>
            <VStack align="start" spacing={1}>
              <Text fontSize="sm" color="gray.600">Average</Text>
              <Text fontSize="lg" fontWeight="bold">{data.statistics.average.toFixed(1)}</Text>
            </VStack>
            <VStack align="start" spacing={1}>
              <Text fontSize="sm" color="gray.600">Peak</Text>
              <Text fontSize="lg" fontWeight="bold">{data.statistics.max}</Text>
            </VStack>
            <VStack align="start" spacing={1}>
              <Text fontSize="sm" color="gray.600">Data Points</Text>
              <Text fontSize="lg" fontWeight="bold">{data.statistics.data_points}</Text>
            </VStack>
          </HStack>

          {/* Chart */}
          <Box h="300px" w="100%">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                <XAxis
                  dataKey="formattedTime"
                  stroke="#718096"
                  fontSize={12}
                  tick={{ fontSize: 11 }}
                  interval="preserveStartEnd"
                />
                <YAxis
                  stroke="#718096"
                  fontSize={12}
                  tick={{ fontSize: 11 }}
                />
                <Tooltip
                  labelFormatter={(value: any, payload: any) => {
                    if (payload && payload[0]) {
                      return formatTooltipLabel(payload[0].payload.timestamp)
                    }
                    return value
                  }}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #E2E8F0',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke={color}
                  strokeWidth={2}
                  dot={{ fill: color, strokeWidth: 2, r: 3 }}
                  activeDot={{ r: 5, stroke: color, strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        </VStack>
      </CardBody>
    </Card>
  )
}

export default MetricChart