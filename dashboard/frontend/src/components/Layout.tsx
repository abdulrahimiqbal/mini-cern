import React, { useEffect, useState } from 'react'
import {
  Box,
  Flex,
  Text,
  Button,
  Badge,
} from '@chakra-ui/react'
import { Link, useLocation } from 'react-router-dom'
import websocketService from '../services/websocket'

interface LayoutProps {
  children: React.ReactNode
}

const navItems = [
  { label: 'Dashboard', path: '/' },
  { label: 'Testing', path: '/testing' },
  { label: 'Workflows', path: '/workflows' },
  { label: 'Research', path: '/research' },
  { label: 'Monitoring', path: '/monitoring' },
]

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation()
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    websocketService.connect()
    
    const checkConnection = () => {
      setIsConnected(websocketService.isConnected())
    }
    
    checkConnection()
    const interval = setInterval(checkConnection, 2000)

    return () => {
      clearInterval(interval)
      websocketService.disconnect()
    }
  }, [])

  return (
    <Flex h="100vh">
      {/* Sidebar */}
      <Box w="300px" bg="white" borderRight="1px" borderColor="gray.200" p={4}>
        <Box mb={6}>
          <Text fontSize="xl" fontWeight="bold" color="blue.600">
            Science Research Institute
          </Text>
          <Text fontSize="sm" color="gray.500">
            Dashboard v1.0
          </Text>
        </Box>

        <Box>
          {navItems.map((item) => {
            const isActive = location.pathname === item.path
            return (
              <Button
                key={item.path}
                as={Link}
                to={item.path}
                variant={isActive ? 'solid' : 'ghost'}
                colorScheme={isActive ? 'blue' : 'gray'}
                w="full"
                mb={2}
                justifyContent="flex-start"
              >
                {item.label}
              </Button>
            )
          })}
        </Box>

        <Box mt="auto" pt={4} borderTop="1px" borderColor="gray.200">
          <Flex align="center" gap={2}>
            <Box w={2} h={2} borderRadius="full" bg={isConnected ? 'green.500' : 'red.500'} />
            <Text fontSize="sm">
              {isConnected ? 'Connected' : 'Disconnected'}
            </Text>
            <Badge colorScheme={isConnected ? 'green' : 'red'}>
              {isConnected ? 'Live' : 'Offline'}
            </Badge>
          </Flex>
        </Box>
      </Box>

      {/* Main Content */}
      <Box flex={1} overflow="auto" p={6}>
        {children}
      </Box>
    </Flex>
  )
}

export default Layout 