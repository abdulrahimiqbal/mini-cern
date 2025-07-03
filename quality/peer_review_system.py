"""
Peer Review System - Automated Quality Assurance
Provides comprehensive quality assessment and peer review for research outputs
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4
import statistics
import json

from core.research_project import ResearchProject
from workflow.workflow_engine import AutomatedResearchCycle
from agents.agent_types import AgentType, AgentCapability

logger = logging.getLogger(__name__)

class ReviewStatus(Enum):
    """Status of a peer review"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    REQUIRES_REVISION = "requires_revision"

class QualityDimension(Enum):
    """Dimensions of quality assessment"""
    METHODOLOGY = "methodology"
    DATA_QUALITY = "data_quality"
    STATISTICAL_VALIDITY = "statistical_validity"
    REPRODUCIBILITY = "reproducibility"
    NOVELTY = "novelty"
    SIGNIFICANCE = "significance"
    CLARITY = "clarity"
    COMPLETENESS = "completeness"

@dataclass
class QualityMetrics:
    """Quality assessment metrics"""
    overall_score: float = 0.0  # 0-100
    methodology_score: float = 0.0
    data_quality_score: float = 0.0
    statistical_validity_score: float = 0.0
    reproducibility_score: float = 0.0
    novelty_score: float = 0.0
    significance_score: float = 0.0
    clarity_score: float = 0.0
    completeness_score: float = 0.0
    
    # Additional metrics
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    reviewer_consensus: float = 0.0  # Agreement between reviewers
    publication_readiness: float = 0.0

@dataclass
class ReviewCriteria:
    """Criteria for peer review"""
    criteria_id: str
    dimension: QualityDimension
    description: str
    weight: float  # Importance weight (0-1)
    evaluation_method: str  # statistical, heuristic, ml_model
    threshold_values: Dict[str, float] = field(default_factory=dict)
    evaluation_prompts: List[str] = field(default_factory=list)

@dataclass
class ReviewComment:
    """Individual review comment"""
    comment_id: str
    reviewer_id: str
    dimension: QualityDimension
    score: float  # 0-100
    comment_text: str
    suggestions: List[str] = field(default_factory=list)
    severity: str = "minor"  # minor, major, critical
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AutomatedReview:
    """Complete automated peer review"""
    review_id: str
    target_type: str  # cycle, project, publication
    target_id: str
    status: ReviewStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    # Review assignment
    assigned_reviewers: List[str] = field(default_factory=list)
    review_coordinator: Optional[str] = None
    
    # Assessment results
    quality_metrics: QualityMetrics = field(default_factory=QualityMetrics)
    individual_scores: Dict[str, float] = field(default_factory=dict)  # reviewer_id -> overall_score
    review_comments: List[ReviewComment] = field(default_factory=list)
    
    # Review metadata
    review_criteria_used: List[str] = field(default_factory=list)
    data_analyzed: Dict[str, Any] = field(default_factory=dict)
    statistical_tests_performed: List[str] = field(default_factory=list)
    
    # Final assessment
    recommendation: str = ""  # accept, accept_with_revisions, reject
    publication_ready: bool = False
    revision_required: bool = False
    major_issues: List[str] = field(default_factory=list)
    minor_issues: List[str] = field(default_factory=list)

class PeerReviewSystem:
    """
    Automated Peer Review and Quality Assurance System
    
    Provides:
    - Multi-dimensional quality assessment
    - Automated peer review coordination
    - Statistical validation
    - Publication readiness evaluation
    - Reproducibility verification
    """
    
    def __init__(self):
        # Review management
        self.active_reviews: Dict[str, AutomatedReview] = {}
        self.completed_reviews: Dict[str, AutomatedReview] = {}
        self.review_criteria: Dict[str, ReviewCriteria] = {}
        
        # Quality thresholds
        self.quality_thresholds = {
            "publication_ready": 75.0,
            "acceptable_quality": 60.0,
            "revision_required": 40.0,
            "reject_threshold": 25.0
        }
        
        # Review configuration
        self.min_reviewers = 2
        self.max_reviewers = 5
        self.reviewer_consensus_threshold = 0.7
        self.review_timeout_hours = 48
        
        # Statistical validation settings
        self.statistical_significance_threshold = 0.05
        self.effect_size_threshold = 0.2
        self.power_analysis_threshold = 0.8
        
        # Review statistics
        self.review_stats = {
            "total_reviews": 0,
            "accepted_reviews": 0,
            "rejected_reviews": 0,
            "revision_required": 0,
            "average_review_time_hours": 0.0,
            "average_quality_score": 0.0
        }
        
        # Initialize review criteria
        self._initialize_review_criteria()
    
    def _initialize_review_criteria(self):
        """Initialize standard review criteria"""
        
        # Methodology criteria
        self.review_criteria["methodology_experimental_design"] = ReviewCriteria(
            criteria_id="methodology_experimental_design",
            dimension=QualityDimension.METHODOLOGY,
            description="Evaluate experimental design appropriateness and rigor",
            weight=0.9,
            evaluation_method="heuristic",
            threshold_values={"good": 70.0, "acceptable": 50.0},
            evaluation_prompts=[
                "Is the experimental design appropriate for the research question?",
                "Are proper controls included?",
                "Is the sample size adequate?",
                "Are confounding variables addressed?"
            ]
        )
        
        # Data quality criteria
        self.review_criteria["data_quality_completeness"] = ReviewCriteria(
            criteria_id="data_quality_completeness",
            dimension=QualityDimension.DATA_QUALITY,
            description="Assess data completeness and integrity",
            weight=0.8,
            evaluation_method="statistical",
            threshold_values={"complete": 95.0, "acceptable": 85.0, "poor": 70.0}
        )
        
        self.review_criteria["data_quality_accuracy"] = ReviewCriteria(
            criteria_id="data_quality_accuracy",
            dimension=QualityDimension.DATA_QUALITY,
            description="Evaluate data accuracy and measurement precision",
            weight=0.8,
            evaluation_method="statistical",
            threshold_values={"high_precision": 90.0, "acceptable": 75.0}
        )
        
        # Statistical validity criteria
        self.review_criteria["statistical_significance"] = ReviewCriteria(
            criteria_id="statistical_significance",
            dimension=QualityDimension.STATISTICAL_VALIDITY,
            description="Check statistical significance and power",
            weight=0.85,
            evaluation_method="statistical",
            threshold_values={"significant": 0.05, "marginal": 0.1}
        )
        
        self.review_criteria["effect_size"] = ReviewCriteria(
            criteria_id="effect_size",
            dimension=QualityDimension.STATISTICAL_VALIDITY,
            description="Evaluate practical significance through effect size",
            weight=0.7,
            evaluation_method="statistical",
            threshold_values={"large": 0.8, "medium": 0.5, "small": 0.2}
        )
        
        # Reproducibility criteria
        self.review_criteria["reproducibility_documentation"] = ReviewCriteria(
            criteria_id="reproducibility_documentation",
            dimension=QualityDimension.REPRODUCIBILITY,
            description="Assess documentation quality for reproducibility",
            weight=0.8,
            evaluation_method="heuristic",
            threshold_values={"excellent": 90.0, "good": 75.0, "adequate": 60.0}
        )
        
        # Novelty and significance
        self.review_criteria["novelty_contribution"] = ReviewCriteria(
            criteria_id="novelty_contribution",
            dimension=QualityDimension.NOVELTY,
            description="Evaluate novelty and contribution to field",
            weight=0.7,
            evaluation_method="heuristic",
            threshold_values={"novel": 80.0, "incremental": 60.0, "limited": 40.0}
        )
        
        self.review_criteria["scientific_significance"] = ReviewCriteria(
            criteria_id="scientific_significance",
            dimension=QualityDimension.SIGNIFICANCE,
            description="Assess scientific significance and impact",
            weight=0.75,
            evaluation_method="heuristic",
            threshold_values={"high_impact": 85.0, "moderate": 65.0, "limited": 45.0}
        )
        
        # Clarity and completeness
        self.review_criteria["clarity_presentation"] = ReviewCriteria(
            criteria_id="clarity_presentation",
            dimension=QualityDimension.CLARITY,
            description="Evaluate clarity of presentation and communication",
            weight=0.6,
            evaluation_method="heuristic",
            threshold_values={"clear": 80.0, "adequate": 65.0, "unclear": 45.0}
        )
        
        self.review_criteria["completeness_analysis"] = ReviewCriteria(
            criteria_id="completeness_analysis",
            dimension=QualityDimension.COMPLETENESS,
            description="Assess completeness of analysis and discussion",
            weight=0.7,
            evaluation_method="heuristic",
            threshold_values={"complete": 85.0, "mostly_complete": 70.0, "incomplete": 50.0}
        )
        
        logger.info(f"Initialized {len(self.review_criteria)} review criteria")
    
    async def start_review(self, target_type: str, target_id: str, 
                          review_data: Dict[str, Any] = None) -> Optional[str]:
        """Start an automated peer review"""
        try:
            review_id = str(uuid4())
            
            review = AutomatedReview(
                review_id=review_id,
                target_type=target_type,
                target_id=target_id,
                status=ReviewStatus.PENDING,
                created_at=datetime.utcnow(),
                data_analyzed=review_data or {}
            )
            
            # Assign reviewers (simulated)
            review.assigned_reviewers = await self._assign_reviewers(target_type, review_data)
            if len(review.assigned_reviewers) < self.min_reviewers:
                logger.error(f"Insufficient reviewers available for review {review_id}")
                return None
            
            # Select review criteria
            review.review_criteria_used = await self._select_review_criteria(target_type, review_data)
            
            self.active_reviews[review_id] = review
            
            # Start the review process
            asyncio.create_task(self._conduct_review(review))
            
            logger.info(f"Started peer review {review_id} for {target_type} {target_id}")
            return review_id
            
        except Exception as e:
            logger.error(f"Failed to start peer review: {e}")
            return None
    
    async def _assign_reviewers(self, target_type: str, review_data: Dict[str, Any]) -> List[str]:
        """Assign appropriate reviewers for the review"""
        # Simulated reviewer assignment based on expertise
        available_reviewers = [
            "theory_reviewer_001",
            "experimental_reviewer_001", 
            "analysis_reviewer_001",
            "methodology_reviewer_001",
            "statistics_reviewer_001"
        ]
        
        # Select reviewers based on target type and content
        if target_type == "cycle":
            selected = available_reviewers[:3]  # 3 reviewers for cycles
        elif target_type == "project":
            selected = available_reviewers[:4]  # 4 reviewers for projects
        else:
            selected = available_reviewers[:2]  # 2 reviewers for other targets
        
        return selected
    
    async def _select_review_criteria(self, target_type: str, review_data: Dict[str, Any]) -> List[str]:
        """Select appropriate review criteria"""
        # Default criteria for all reviews
        selected_criteria = [
            "methodology_experimental_design",
            "data_quality_completeness",
            "statistical_significance",
            "clarity_presentation"
        ]
        
        # Add specific criteria based on target type
        if target_type == "cycle":
            selected_criteria.extend([
                "data_quality_accuracy",
                "effect_size",
                "reproducibility_documentation"
            ])
        elif target_type == "project":
            selected_criteria.extend([
                "novelty_contribution",
                "scientific_significance",
                "completeness_analysis"
            ])
        
        return selected_criteria
    
    async def _conduct_review(self, review: AutomatedReview) -> None:
        """Conduct the complete peer review process"""
        try:
            review.status = ReviewStatus.IN_PROGRESS
            
            # Phase 1: Individual reviewer assessments
            individual_assessments = await self._conduct_individual_assessments(review)
            
            # Phase 2: Statistical validation
            statistical_results = await self._conduct_statistical_validation(review)
            
            # Phase 3: Aggregate results and generate consensus
            await self._aggregate_review_results(review, individual_assessments, statistical_results)
            
            # Phase 4: Generate final recommendation
            await self._generate_final_recommendation(review)
            
            review.status = ReviewStatus.COMPLETED
            review.completed_at = datetime.utcnow()
            
            # Move to completed reviews
            self.completed_reviews[review.review_id] = review
            if review.review_id in self.active_reviews:
                del self.active_reviews[review.review_id]
            
            # Update statistics
            self._update_review_statistics(review)
            
            logger.info(f"Completed peer review {review.review_id} with overall score {review.quality_metrics.overall_score:.1f}")
            
        except Exception as e:
            logger.error(f"Error conducting review {review.review_id}: {e}")
            review.status = ReviewStatus.REJECTED
            review.completed_at = datetime.utcnow()
    
    async def _conduct_individual_assessments(self, review: AutomatedReview) -> Dict[str, Dict[str, float]]:
        """Conduct individual reviewer assessments"""
        assessments = {}
        
        for reviewer_id in review.assigned_reviewers:
            reviewer_assessment = {}
            
            # Evaluate each criterion
            for criteria_id in review.review_criteria_used:
                criteria = self.review_criteria[criteria_id]
                score = await self._evaluate_criterion(criteria, review.data_analyzed, reviewer_id)
                reviewer_assessment[criteria_id] = score
                
                # Generate review comment
                comment = await self._generate_review_comment(criteria, score, reviewer_id)
                review.review_comments.append(comment)
            
            # Calculate reviewer's overall score
            overall_score = await self._calculate_reviewer_overall_score(reviewer_assessment, review.review_criteria_used)
            review.individual_scores[reviewer_id] = overall_score
            assessments[reviewer_id] = reviewer_assessment
        
        return assessments
    
    async def _evaluate_criterion(self, criteria: ReviewCriteria, data: Dict[str, Any], reviewer_id: str) -> float:
        """Evaluate a single review criterion"""
        if criteria.evaluation_method == "statistical":
            return await self._statistical_evaluation(criteria, data)
        elif criteria.evaluation_method == "heuristic":
            return await self._heuristic_evaluation(criteria, data, reviewer_id)
        elif criteria.evaluation_method == "ml_model":
            return await self._ml_model_evaluation(criteria, data)
        else:
            # Default random evaluation for simulation
            import random
            return random.uniform(50, 90)
    
    async def _statistical_evaluation(self, criteria: ReviewCriteria, data: Dict[str, Any]) -> float:
        """Perform statistical evaluation of a criterion"""
        if criteria.criteria_id == "data_quality_completeness":
            # Simulate data completeness check
            completeness = data.get("data_completeness_percent", 85.0)
            if completeness >= criteria.threshold_values.get("complete", 95.0):
                return 95.0
            elif completeness >= criteria.threshold_values.get("acceptable", 85.0):
                return 75.0
            else:
                return 50.0
        
        elif criteria.criteria_id == "statistical_significance":
            # Simulate p-value analysis
            p_value = data.get("p_value", 0.03)
            if p_value <= criteria.threshold_values.get("significant", 0.05):
                return 90.0
            elif p_value <= criteria.threshold_values.get("marginal", 0.1):
                return 70.0
            else:
                return 40.0
        
        elif criteria.criteria_id == "effect_size":
            # Simulate effect size evaluation
            effect_size = data.get("effect_size", 0.6)
            if effect_size >= criteria.threshold_values.get("large", 0.8):
                return 95.0
            elif effect_size >= criteria.threshold_values.get("medium", 0.5):
                return 80.0
            elif effect_size >= criteria.threshold_values.get("small", 0.2):
                return 65.0
            else:
                return 40.0
        
        # Default statistical evaluation
        import random
        return random.uniform(60, 85)
    
    async def _heuristic_evaluation(self, criteria: ReviewCriteria, data: Dict[str, Any], reviewer_id: str) -> float:
        """Perform heuristic evaluation of a criterion"""
        # Simulate expert reviewer assessment
        base_scores = {
            "methodology_experimental_design": 78.0,
            "reproducibility_documentation": 72.0,
            "novelty_contribution": 68.0,
            "scientific_significance": 75.0,
            "clarity_presentation": 80.0,
            "completeness_analysis": 73.0
        }
        
        base_score = base_scores.get(criteria.criteria_id, 70.0)
        
        # Add reviewer-specific variation
        import random
        reviewer_bias = random.uniform(-10, 10)
        
        # Add data-driven adjustments
        data_quality_factor = data.get("overall_data_quality", 0.8)
        methodology_factor = data.get("methodology_rigor", 0.75)
        
        adjusted_score = base_score + reviewer_bias + (data_quality_factor * 10) + (methodology_factor * 5)
        
        return max(0, min(100, adjusted_score))
    
    async def _ml_model_evaluation(self, criteria: ReviewCriteria, data: Dict[str, Any]) -> float:
        """Perform ML model-based evaluation (simulated)"""
        # In real implementation, would use trained ML models
        import random
        return random.uniform(65, 85)
    
    async def _generate_review_comment(self, criteria: ReviewCriteria, score: float, reviewer_id: str) -> ReviewComment:
        """Generate a review comment for a criterion"""
        comment_id = str(uuid4())
        
        # Generate comment based on score
        if score >= 80:
            comment_text = f"Excellent {criteria.dimension.value}. The work demonstrates high quality in this dimension."
            severity = "minor"
            suggestions = ["Consider minor improvements for publication"]
        elif score >= 60:
            comment_text = f"Good {criteria.dimension.value}. The work meets acceptable standards with room for improvement."
            severity = "minor"
            suggestions = ["Address minor concerns", "Consider additional validation"]
        else:
            comment_text = f"Concerning {criteria.dimension.value}. Significant improvements needed."
            severity = "major"
            suggestions = ["Major revision required", "Additional analysis needed", "Consider alternative approaches"]
        
        return ReviewComment(
            comment_id=comment_id,
            reviewer_id=reviewer_id,
            dimension=criteria.dimension,
            score=score,
            comment_text=comment_text,
            suggestions=suggestions,
            severity=severity
        )
    
    async def _calculate_reviewer_overall_score(self, assessment: Dict[str, float], criteria_ids: List[str]) -> float:
        """Calculate a reviewer's overall score"""
        weighted_scores = []
        total_weight = 0
        
        for criteria_id in criteria_ids:
            if criteria_id in assessment and criteria_id in self.review_criteria:
                criteria = self.review_criteria[criteria_id]
                score = assessment[criteria_id]
                weight = criteria.weight
                
                weighted_scores.append(score * weight)
                total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return sum(weighted_scores) / total_weight
    
    async def _conduct_statistical_validation(self, review: AutomatedReview) -> Dict[str, Any]:
        """Conduct statistical validation of research results"""
        data = review.data_analyzed
        statistical_results = {}
        tests_performed = []
        
        # Simulate statistical tests
        if "experimental_data" in data:
            # Power analysis
            power = data.get("statistical_power", 0.85)
            statistical_results["power_analysis"] = {
                "power": power,
                "adequate": power >= self.power_analysis_threshold
            }
            tests_performed.append("power_analysis")
            
            # Effect size calculation
            effect_size = data.get("effect_size", 0.6)
            statistical_results["effect_size"] = {
                "value": effect_size,
                "interpretation": self._interpret_effect_size(effect_size)
            }
            tests_performed.append("effect_size_calculation")
            
            # Confidence intervals
            ci_lower = data.get("ci_lower", 0.45)
            ci_upper = data.get("ci_upper", 0.75)
            statistical_results["confidence_interval"] = {
                "lower": ci_lower,
                "upper": ci_upper,
                "excludes_null": ci_lower > 0
            }
            tests_performed.append("confidence_interval")
        
        review.statistical_tests_performed = tests_performed
        return statistical_results
    
    def _interpret_effect_size(self, effect_size: float) -> str:
        """Interpret effect size magnitude"""
        if effect_size >= 0.8:
            return "large"
        elif effect_size >= 0.5:
            return "medium"
        elif effect_size >= 0.2:
            return "small"
        else:
            return "negligible"
    
    async def _aggregate_review_results(self, review: AutomatedReview, 
                                      individual_assessments: Dict[str, Dict[str, float]],
                                      statistical_results: Dict[str, Any]) -> None:
        """Aggregate individual review results into overall quality metrics"""
        # Calculate overall scores by dimension
        dimension_scores = {}
        for dimension in QualityDimension:
            dimension_scores[dimension] = []
        
        # Collect scores by dimension
        for reviewer_id, assessment in individual_assessments.items():
            for criteria_id, score in assessment.items():
                criteria = self.review_criteria[criteria_id]
                dimension_scores[criteria.dimension].append(score)
        
        # Calculate mean scores for each dimension
        metrics = QualityMetrics()
        
        if dimension_scores[QualityDimension.METHODOLOGY]:
            metrics.methodology_score = statistics.mean(dimension_scores[QualityDimension.METHODOLOGY])
        
        if dimension_scores[QualityDimension.DATA_QUALITY]:
            metrics.data_quality_score = statistics.mean(dimension_scores[QualityDimension.DATA_QUALITY])
        
        if dimension_scores[QualityDimension.STATISTICAL_VALIDITY]:
            metrics.statistical_validity_score = statistics.mean(dimension_scores[QualityDimension.STATISTICAL_VALIDITY])
        
        if dimension_scores[QualityDimension.REPRODUCIBILITY]:
            metrics.reproducibility_score = statistics.mean(dimension_scores[QualityDimension.REPRODUCIBILITY])
        
        if dimension_scores[QualityDimension.NOVELTY]:
            metrics.novelty_score = statistics.mean(dimension_scores[QualityDimension.NOVELTY])
        
        if dimension_scores[QualityDimension.SIGNIFICANCE]:
            metrics.significance_score = statistics.mean(dimension_scores[QualityDimension.SIGNIFICANCE])
        
        if dimension_scores[QualityDimension.CLARITY]:
            metrics.clarity_score = statistics.mean(dimension_scores[QualityDimension.CLARITY])
        
        if dimension_scores[QualityDimension.COMPLETENESS]:
            metrics.completeness_score = statistics.mean(dimension_scores[QualityDimension.COMPLETENESS])
        
        # Calculate overall score (weighted average)
        dimension_weights = {
            QualityDimension.METHODOLOGY: 0.15,
            QualityDimension.DATA_QUALITY: 0.15,
            QualityDimension.STATISTICAL_VALIDITY: 0.15,
            QualityDimension.REPRODUCIBILITY: 0.12,
            QualityDimension.NOVELTY: 0.12,
            QualityDimension.SIGNIFICANCE: 0.13,
            QualityDimension.CLARITY: 0.08,
            QualityDimension.COMPLETENESS: 0.10
        }
        
        weighted_sum = 0
        total_weight = 0
        
        dimension_score_map = {
            QualityDimension.METHODOLOGY: metrics.methodology_score,
            QualityDimension.DATA_QUALITY: metrics.data_quality_score,
            QualityDimension.STATISTICAL_VALIDITY: metrics.statistical_validity_score,
            QualityDimension.REPRODUCIBILITY: metrics.reproducibility_score,
            QualityDimension.NOVELTY: metrics.novelty_score,
            QualityDimension.SIGNIFICANCE: metrics.significance_score,
            QualityDimension.CLARITY: metrics.clarity_score,
            QualityDimension.COMPLETENESS: metrics.completeness_score
        }
        
        for dimension, weight in dimension_weights.items():
            score = dimension_score_map[dimension]
            if score > 0:  # Only include dimensions that were evaluated
                weighted_sum += score * weight
                total_weight += weight
        
        if total_weight > 0:
            metrics.overall_score = weighted_sum / total_weight
        
        # Calculate reviewer consensus
        individual_overall_scores = list(review.individual_scores.values())
        if len(individual_overall_scores) > 1:
            score_variance = statistics.variance(individual_overall_scores)
            # Convert variance to consensus measure (0-1, higher is better consensus)
            metrics.reviewer_consensus = max(0, 1 - (score_variance / 1000))
        else:
            metrics.reviewer_consensus = 1.0
        
        # Calculate publication readiness
        metrics.publication_readiness = self._calculate_publication_readiness(metrics)
        
        # Set confidence interval for overall score
        if individual_overall_scores:
            std_dev = statistics.stdev(individual_overall_scores) if len(individual_overall_scores) > 1 else 5.0
            metrics.confidence_interval = (
                max(0, metrics.overall_score - 1.96 * std_dev),
                min(100, metrics.overall_score + 1.96 * std_dev)
            )
        
        review.quality_metrics = metrics
    
    def _calculate_publication_readiness(self, metrics: QualityMetrics) -> float:
        """Calculate publication readiness score"""
        # Publication readiness considers multiple factors
        factors = [
            metrics.overall_score * 0.4,           # Overall quality
            metrics.statistical_validity_score * 0.2,  # Statistical validity
            metrics.reproducibility_score * 0.2,      # Reproducibility 
            metrics.clarity_score * 0.1,              # Clarity
            metrics.completeness_score * 0.1          # Completeness
        ]
        
        return sum(f for f in factors if f > 0) / len([f for f in factors if f > 0])
    
    async def _generate_final_recommendation(self, review: AutomatedReview) -> None:
        """Generate final recommendation based on review results"""
        metrics = review.quality_metrics
        overall_score = metrics.overall_score
        
        # Collect major and minor issues
        major_issues = []
        minor_issues = []
        
        for comment in review.review_comments:
            if comment.severity == "critical" or comment.severity == "major":
                major_issues.extend(comment.suggestions)
            else:
                minor_issues.extend(comment.suggestions)
        
        # Generate recommendation
        if overall_score >= self.quality_thresholds["publication_ready"]:
            if metrics.reviewer_consensus >= self.reviewer_consensus_threshold:
                review.recommendation = "accept"
                review.publication_ready = True
            else:
                review.recommendation = "accept_with_revisions"
                review.revision_required = True
                minor_issues.append("Address reviewer consensus concerns")
        
        elif overall_score >= self.quality_thresholds["acceptable_quality"]:
            review.recommendation = "accept_with_revisions"
            review.revision_required = True
            
        elif overall_score >= self.quality_thresholds["revision_required"]:
            review.recommendation = "major_revision_required"
            review.revision_required = True
            major_issues.append("Significant improvements required across multiple dimensions")
            
        else:
            review.recommendation = "reject"
            major_issues.append("Quality does not meet minimum standards")
        
        # Remove duplicates
        review.major_issues = list(set(major_issues))
        review.minor_issues = list(set(minor_issues))
    
    def _update_review_statistics(self, review: AutomatedReview) -> None:
        """Update review statistics"""
        self.review_stats["total_reviews"] += 1
        
        if review.recommendation == "accept":
            self.review_stats["accepted_reviews"] += 1
        elif review.recommendation == "reject":
            self.review_stats["rejected_reviews"] += 1
        else:
            self.review_stats["revision_required"] += 1
        
        # Update average quality score
        total_reviews = self.review_stats["total_reviews"]
        current_avg = self.review_stats["average_quality_score"]
        new_score = review.quality_metrics.overall_score
        self.review_stats["average_quality_score"] = (current_avg * (total_reviews - 1) + new_score) / total_reviews
        
        # Update average review time
        if review.completed_at and review.created_at:
            review_time = (review.completed_at - review.created_at).total_seconds() / 3600
            current_avg_time = self.review_stats["average_review_time_hours"]
            self.review_stats["average_review_time_hours"] = (current_avg_time * (total_reviews - 1) + review_time) / total_reviews
    
    async def get_review_status(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a review"""
        review = self.active_reviews.get(review_id) or self.completed_reviews.get(review_id)
        if not review:
            return None
        
        return {
            "review_id": review.review_id,
            "target_type": review.target_type,
            "target_id": review.target_id,
            "status": review.status.value,
            "created_at": review.created_at.isoformat(),
            "completed_at": review.completed_at.isoformat() if review.completed_at else None,
            "assigned_reviewers": review.assigned_reviewers,
            "quality_metrics": {
                "overall_score": review.quality_metrics.overall_score,
                "methodology_score": review.quality_metrics.methodology_score,
                "data_quality_score": review.quality_metrics.data_quality_score,
                "statistical_validity_score": review.quality_metrics.statistical_validity_score,
                "publication_readiness": review.quality_metrics.publication_readiness,
                "reviewer_consensus": review.quality_metrics.reviewer_consensus
            },
            "recommendation": review.recommendation,
            "publication_ready": review.publication_ready,
            "revision_required": review.revision_required,
            "major_issues": review.major_issues,
            "minor_issues": review.minor_issues
        }
    
    async def get_review_details(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed review information including comments"""
        review = self.active_reviews.get(review_id) or self.completed_reviews.get(review_id)
        if not review:
            return None
        
        comments = []
        for comment in review.review_comments:
            comments.append({
                "comment_id": comment.comment_id,
                "reviewer_id": comment.reviewer_id,
                "dimension": comment.dimension.value,
                "score": comment.score,
                "comment_text": comment.comment_text,
                "suggestions": comment.suggestions,
                "severity": comment.severity,
                "created_at": comment.created_at.isoformat()
            })
        
        return {
            **await self.get_review_status(review_id),
            "individual_scores": review.individual_scores,
            "review_comments": comments,
            "statistical_tests_performed": review.statistical_tests_performed,
            "confidence_interval": review.quality_metrics.confidence_interval
        }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get peer review system status"""
        return {
            "active_reviews": len(self.active_reviews),
            "completed_reviews": len(self.completed_reviews),
            "review_criteria": len(self.review_criteria),
            "quality_thresholds": self.quality_thresholds,
            "statistics": self.review_stats
        } 