import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  Card,
  CardBody,
  CardHeader,
  Grid,
  GridItem,
  Badge,
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Select,
  useDisclosure,
  useToast,
  VStack,
  HStack,
  Icon
} from '@chakra-ui/react';
import { FaFlask, FaRobot, FaBrain, FaChartLine, FaPlay, FaPlus } from 'react-icons/fa';
import api from '../services/api';

interface ResearchProject {
  project_id: string;
  title: string;
  research_question: string;
  domain: string;
  status: string;
  progress: number;
  current_stage?: string;
  budget_total: number;
  budget_used: number;
  tasks_completed: number;
  total_tasks: number;
  active_agents: string[];
  started_at?: string;
  completed_at?: string;
  estimated_completion?: string;
  priority: string;
  findings_count?: number;
  final_report_available?: boolean;
}

interface ResearchData {
  success: boolean;
  active_projects: ResearchProject[];
  completed_projects: ResearchProject[];
  statistics: {
    total_projects: number;
    active_projects: number;
    completed_projects: number;
    total_budget_allocated: number;
    total_budget_used: number;
    average_completion_time: string;
    success_rate: number;
    active_agents: Record<string, string>;
  };
  capabilities: {
    autonomous_research: boolean;
    multi_agent_coordination: boolean;
    real_time_monitoring: boolean;
    adaptive_planning: boolean;
    cost_optimization: boolean;
    safety_validation: boolean;
    peer_review: boolean;
    auto_publication: boolean;
  };
}

const Research: React.FC = () => {
  const [researchData, setResearchData] = useState<ResearchData | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  // Form state for creating new research project
  const [formData, setFormData] = useState({
    research_question: '',
    domain: 'quantum_physics',
    budget: 50000,
    priority: 'medium'
  });

  useEffect(() => {
    fetchResearchData();
  }, []);

  const fetchResearchData = async () => {
    try {
      const response = await api.getResearchProjects();
      setResearchData(response);
    } catch (error) {
      console.error('Error fetching research data:', error);
      toast({
        title: 'Error',
        description: 'Failed to load research projects',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const createResearchProject = async () => {
    setCreating(true);
    try {
      const response = await api.createResearchProject(formData);
      
      if (response.success) {
        toast({
          title: 'Success',
          description: response.message,
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
        
        // Reset form and close modal
        setFormData({
          research_question: '',
          domain: 'quantum_physics',
          budget: 50000,
          priority: 'medium'
        });
        onClose();
        
        // Refresh data
        fetchResearchData();
      } else {
        throw new Error(response.error || 'Failed to create project');
      }
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Failed to create research project',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setCreating(false);
    }
  };

  const startProject = async (projectId: string) => {
    try {
      const response = await api.startResearchProject(projectId);
      
      if (response.success) {
        toast({
          title: 'Success',
          description: `Research project execution started`,
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
        fetchResearchData();
      }
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Failed to start project',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'executing': return 'blue';
      case 'completed': return 'green';
      case 'planning': return 'orange';
      case 'failed': return 'red';
      default: return 'gray';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'red';
      case 'medium': return 'orange';
      case 'low': return 'green';
      default: return 'gray';
    }
  };

  if (loading) {
    return (
      <Container maxW="7xl" py={8}>
        <Text>Loading autonomous research dashboard...</Text>
      </Container>
    );
  }

  if (!researchData) {
    return (
      <Container maxW="7xl" py={8}>
        <Text>Failed to load research data</Text>
      </Container>
    );
  }

  return (
    <Container maxW="7xl" py={8}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Box>
          <HStack justify="space-between" align="center" mb={4}>
            <VStack align="start" spacing={1}>
              <Heading size="lg" color="blue.600">
                <Icon as={FaBrain} mr={3} />
                Autonomous Research System
              </Heading>
              <Text color="gray.600">
                Phase 6: AI-driven scientific discovery and hypothesis generation
              </Text>
            </VStack>
            <Button
              leftIcon={<FaPlus />}
              colorScheme="blue"
              onClick={onOpen}
              size="lg"
            >
              Create Research Project
            </Button>
          </HStack>
        </Box>

        {/* Statistics Overview */}
        <Grid templateColumns="repeat(4, 1fr)" gap={6}>
          <GridItem>
            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>Active Projects</StatLabel>
                  <StatNumber color="blue.600">{researchData.statistics.active_projects}</StatNumber>
                  <StatHelpText>Currently executing</StatHelpText>
                </Stat>
              </CardBody>
            </Card>
          </GridItem>
          <GridItem>
            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>Success Rate</StatLabel>
                  <StatNumber color="green.600">{researchData.statistics.success_rate}%</StatNumber>
                  <StatHelpText>Project completion</StatHelpText>
                </Stat>
              </CardBody>
            </Card>
          </GridItem>
          <GridItem>
            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>Budget Utilization</StatLabel>
                  <StatNumber color="orange.600">
                    ${(researchData.statistics.total_budget_used / 1000).toFixed(0)}K
                  </StatNumber>
                  <StatHelpText>
                    of ${(researchData.statistics.total_budget_allocated / 1000).toFixed(0)}K allocated
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>
          </GridItem>
          <GridItem>
            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>Avg. Completion</StatLabel>
                  <StatNumber color="purple.600">{researchData.statistics.average_completion_time}</StatNumber>
                  <StatHelpText>Time per project</StatHelpText>
                </Stat>
              </CardBody>
            </Card>
          </GridItem>
        </Grid>

        {/* Active Research Projects */}
        <Card>
          <CardHeader>
            <Heading size="md">
              <Icon as={FaFlask} mr={2} color="blue.500" />
              Active Research Projects
            </Heading>
          </CardHeader>
          <CardBody>
            {researchData.active_projects.length > 0 ? (
              <Table variant="simple">
                <Thead>
                  <Tr>
                    <Th>Research Question</Th>
                    <Th>Domain</Th>
                    <Th>Status</Th>
                    <Th>Progress</Th>
                    <Th>Budget</Th>
                    <Th>Active Agents</Th>
                    <Th>Actions</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {researchData.active_projects.map((project) => (
                    <Tr key={project.project_id}>
                      <Td>
                        <VStack align="start" spacing={1}>
                          <Text fontWeight="medium" noOfLines={2}>
                            {project.research_question}
                          </Text>
                          <Badge colorScheme={getPriorityColor(project.priority)} size="sm">
                            {project.priority}
                          </Badge>
                        </VStack>
                      </Td>
                      <Td>
                        <Badge colorScheme="purple" variant="subtle">
                          {project.domain.replace('_', ' ')}
                        </Badge>
                      </Td>
                      <Td>
                        <VStack align="start" spacing={1}>
                          <Badge colorScheme={getStatusColor(project.status)}>
                            {project.status}
                          </Badge>
                          {project.current_stage && (
                            <Text fontSize="xs" color="gray.500">
                              {project.current_stage.replace('_', ' ')}
                            </Text>
                          )}
                        </VStack>
                      </Td>
                      <Td>
                        <VStack align="start" spacing={1}>
                          <Progress 
                            value={project.progress} 
                            width="100px" 
                            colorScheme="blue"
                            size="sm"
                          />
                          <Text fontSize="xs">
                            {project.tasks_completed}/{project.total_tasks} tasks
                          </Text>
                        </VStack>
                      </Td>
                      <Td>
                        <VStack align="start" spacing={1}>
                          <Text fontSize="sm" fontWeight="medium">
                            ${(project.budget_used / 1000).toFixed(1)}K
                          </Text>
                          <Text fontSize="xs" color="gray.500">
                            of ${(project.budget_total / 1000).toFixed(0)}K
                          </Text>
                        </VStack>
                      </Td>
                      <Td>
                        <VStack align="start" spacing={1}>
                          {project.active_agents.map((agent) => (
                            <Badge key={agent} colorScheme="green" size="sm">
                              <Icon as={FaRobot} mr={1} />
                              {agent.replace('_agent', '')}
                            </Badge>
                          ))}
                        </VStack>
                      </Td>
                      <Td>
                        {project.status === 'planning' && (
                          <Button
                            size="sm"
                            colorScheme="blue"
                            leftIcon={<FaPlay />}
                            onClick={() => startProject(project.project_id)}
                          >
                            Start
                          </Button>
                        )}
                        {project.status === 'executing' && (
                          <Button size="sm" variant="outline" leftIcon={<FaChartLine />}>
                            Monitor
                          </Button>
                        )}
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            ) : (
              <Text color="gray.500" textAlign="center" py={8}>
                No active research projects. Create one to begin autonomous research.
              </Text>
            )}
          </CardBody>
        </Card>

        {/* Completed Projects */}
        {researchData.completed_projects.length > 0 && (
          <Card>
            <CardHeader>
              <Heading size="md">
                <Icon as={FaChartLine} mr={2} color="green.500" />
                Completed Research Projects
              </Heading>
            </CardHeader>
            <CardBody>
              <Table variant="simple">
                <Thead>
                  <Tr>
                    <Th>Research Question</Th>
                    <Th>Domain</Th>
                    <Th>Completion</Th>
                    <Th>Budget Used</Th>
                    <Th>Findings</Th>
                    <Th>Report</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {researchData.completed_projects.map((project) => (
                    <Tr key={project.project_id}>
                      <Td>
                        <Text fontWeight="medium" noOfLines={2}>
                          {project.research_question}
                        </Text>
                      </Td>
                      <Td>
                        <Badge colorScheme="purple" variant="subtle">
                          {project.domain.replace('_', ' ')}
                        </Badge>
                      </Td>
                      <Td>
                        <Text fontSize="sm">
                          {project.completed_at && new Date(project.completed_at).toLocaleDateString()}
                        </Text>
                      </Td>
                      <Td>
                        <Text fontSize="sm" fontWeight="medium">
                          ${(project.budget_used / 1000).toFixed(1)}K
                        </Text>
                      </Td>
                      <Td>
                        <Badge colorScheme="blue">
                          {project.findings_count} findings
                        </Badge>
                      </Td>
                      <Td>
                        {project.final_report_available && (
                          <Button size="sm" variant="outline">
                            View Report
                          </Button>
                        )}
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </CardBody>
          </Card>
        )}
      </VStack>

      {/* Create Project Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Create Autonomous Research Project</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Research Question</FormLabel>
                <Textarea
                  placeholder="Enter your research question (e.g., How can quantum computing improve machine learning algorithms?)"
                  value={formData.research_question}
                  onChange={(e) => setFormData({ ...formData, research_question: e.target.value })}
                  rows={3}
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Research Domain</FormLabel>
                <Select
                  value={formData.domain}
                  onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
                >
                  <option value="quantum_physics">Quantum Physics</option>
                  <option value="particle_physics">Particle Physics</option>
                  <option value="artificial_intelligence">Artificial Intelligence</option>
                  <option value="materials_science">Materials Science</option>
                  <option value="biotechnology">Biotechnology</option>
                  <option value="astronomy">Astronomy</option>
                  <option value="nuclear_physics">Nuclear Physics</option>
                  <option value="computational_biology">Computational Biology</option>
                </Select>
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Budget ($)</FormLabel>
                <Input
                  type="number"
                  value={formData.budget}
                  onChange={(e) => setFormData({ ...formData, budget: Number(e.target.value) })}
                  min={10000}
                  max={500000}
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Priority</FormLabel>
                <Select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </Select>
              </FormControl>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button
              colorScheme="blue"
              onClick={createResearchProject}
              isLoading={creating}
              loadingText="Creating..."
              isDisabled={!formData.research_question.trim()}
            >
              Create Project
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Container>
  );
};

export default Research; 