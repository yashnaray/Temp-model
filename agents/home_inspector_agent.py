import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.condition_scorer import ConditionScorer
from vision.material_recognizer import MaterialRecognizer
from vision.change_detector import ChangeDetector
from vision.property_detector import PropertyDetector

class HomeInspectorAgent:
    def __init__(self):
        self.condition_scorer = ConditionScorer()
        self.material_recognizer = MaterialRecognizer()
        self.change_detector = ChangeDetector()
        self.property_detector = PropertyDetector()
        
    def inspect_property(self, images, property_info=None):
        """Comprehensive property inspection"""
        inspection_report = {
            'overall_condition': 'unknown',
            'components': {},
            'issues': [],
            'recommendations': []
        }
        
        if not images:
            return inspection_report
        
        main_image = images[0]
        
        # Detect property components
        components = self.property_detector.detect_property_components(main_image)
        inspection_report['components'] = components
        
        # Segment property for detailed analysis
        segmentation = self.property_detector.segment_property(main_image)
        
        # Analyze each component
        for component, region_data in segmentation['regions'].items():
            mask = segmentation['masks'][component]
            
            if component == 'roof':
                roof_condition = self.condition_scorer.score_roof_condition(region_data, mask)
                inspection_report['components'][component]['condition'] = roof_condition
                
            elif component == 'foundation':
                foundation_analysis = self.condition_scorer.analyze_foundation(region_data, mask)
                inspection_report['components'][component]['analysis'] = foundation_analysis
            
            # Material analysis for all components
            material_info = self.condition_scorer.analyze_material_condition(region_data, mask)
            inspection_report['components'][component]['material'] = material_info
        
        # Change detection if multiple images provided
        if len(images) > 1:
            changes = self.change_detector.detect_changes(images[0], images[-1])
            inspection_report['changes'] = changes
            
            if changes['change_percentage'] > 5:
                inspection_report['issues'].append(f"Significant changes detected: {changes['change_percentage']:.1f}%")
        
        # Generate overall condition score
        inspection_report['overall_condition'] = self._calculate_overall_condition(inspection_report)
        
        # Generate recommendations
        inspection_report['recommendations'] = self._generate_recommendations(inspection_report)
        
        return inspection_report
    
    def _calculate_overall_condition(self, report):
        """Calculate overall property condition"""
        scores = []
        
        for component, data in report['components'].items():
            if 'condition' in data:
                if isinstance(data['condition'], tuple):
                    scores.append(data['condition'][0])
                elif isinstance(data['condition'], dict) and 'severity_score' in data['condition']:
                    scores.append(10 - data['condition']['severity_score'])
        
        if scores:
            avg_score = sum(scores) / len(scores)
            if avg_score > 7:
                return 'excellent'
            elif avg_score > 5:
                return 'good'
            elif avg_score > 3:
                return 'fair'
            else:
                return 'poor'
        
        return 'unknown'
    
    def _generate_recommendations(self, report):
        """Generate maintenance recommendations"""
        recommendations = []
        
        # Check for foundation issues
        foundation = report['components'].get('foundation', {})
        if 'analysis' in foundation:
            severity = foundation['analysis'].get('severity_score', 0)
            if severity > 2:
                recommendations.append("Foundation requires immediate attention - consider professional inspection")
        
        # Check for roof issues
        roof = report['components'].get('roof', {})
        if 'condition' in roof and isinstance(roof['condition'], tuple):
            condition_score, features = roof['condition']
            if features.get('vegetation_coverage', 0) > 0.1:
                recommendations.append("Remove moss/vegetation from roof")
            if features.get('missing_shingle_ratio', 0) > 0.05:
                recommendations.append("Replace missing or damaged shingles")
        
        # Check for material degradation
        for component, data in report['components'].items():
            if 'material' in data:
                material_data = data['material']
                if material_data.get('corrosion_score', 0) > 0.2:
                    recommendations.append(f"Address corrosion in {component}")
                if material_data.get('moisture_damage', 0) > 0.3:
                    recommendations.append(f"Address moisture damage in {component}")
        
        return recommendations