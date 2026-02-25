"""
Use Case Strategy System
Each strategy defines weights and scoring adjustments for specific use cases.
Final score always follows: FinalScore = Σ (weight × adjusted_spec_score)
"""

class BaseStrategy:
    """Base class for all use case strategies"""
    
    # Weight tiers
    CRITICAL = 0.3
    IMPORTANT = 0.15
    SECONDARY = 0.05
    
    weights = {}
    
    @staticmethod
    def normalize_spec(value, min_val, max_val, inverse=False):
        """Normalize a spec value to 0-1 range"""
        if value is None or min_val == max_val:
            return 0.5
        normalized = (value - min_val) / (max_val - min_val)
        return 1 - normalized if inverse else normalized
    
    def adjust_scores(self, normalized_scores, raw_specs):
        """
        Apply use case-specific adjustments to normalized scores.
        Override in subclasses for custom behavior.
        """
        return normalized_scores


class GamingStrategy(BaseStrategy):
    """
    Gaming Use Case
    Critical: Low latency, good mics
    Important: Wired preference, driver size, price
    Secondary: Battery life, water resistance
    """
    
    weights = {
        'latency': BaseStrategy.CRITICAL,        # 0.3
        'num_mics': BaseStrategy.CRITICAL,       # 0.3
        'device_type': BaseStrategy.IMPORTANT,   # 0.15 (wired bonus)
        'driver_size': BaseStrategy.IMPORTANT,   # 0.15
        'price': BaseStrategy.SECONDARY,         # 0.05 (value for money)
        'battery_life': BaseStrategy.SECONDARY,  # 0.025
        'water_resistance': BaseStrategy.SECONDARY, # 0.025
    }
    
    def adjust_scores(self, normalized_scores, raw_specs):
        adjusted = normalized_scores.copy()
        
        # Latency: Aggressive penalty for high latency
        latency = raw_specs.get('latency', 100)
        if latency:
            if latency <= 30:
                adjusted['latency'] = 1.0  # Perfect score
            elif latency <= 50:
                adjusted['latency'] = 0.8
            elif latency <= 100:
                adjusted['latency'] = 0.4
            else:
                adjusted['latency'] = 0.1  # Severe penalty
        
        # Wired preference: Binary boost
        device_type = raw_specs.get('device_type', '')
        if 'wired' in device_type.lower():
            # Apply 1.3x multiplier to the wired score component
            adjusted['device_type'] = 1.0 * 1.3
        else:
            adjusted['device_type'] = 0.6
        
        # Mic count: More mics = better clarity potential
        num_mics = raw_specs.get('num_mics', 0)
        if num_mics >= 4:
            adjusted['num_mics'] = min(1.0, adjusted.get('num_mics', 0) * 1.2)
        
        return adjusted


class GymStrategy(BaseStrategy):
    """
    Gym Use Case
    Critical: Water resistance, wireless, battery life
    Secondary: Everything else
    Penalty: Wired devices
    """
    
    weights = {
        'water_resistance': BaseStrategy.CRITICAL,  # 0.3
        'device_type': BaseStrategy.CRITICAL,       # 0.3
        'battery_life': BaseStrategy.CRITICAL,      # 0.3
        'price': BaseStrategy.SECONDARY,            # 0.05
        'num_mics': BaseStrategy.SECONDARY / 2,     # 0.025
        'latency': BaseStrategy.SECONDARY / 4,      # 0.0125
        'driver_size': BaseStrategy.SECONDARY / 4,  # 0.0125
    }
    
    def adjust_scores(self, normalized_scores, raw_specs):
        adjusted = normalized_scores.copy()
        
        # Wired = heavy penalty
        device_type = raw_specs.get('device_type', '')
        if 'wired' in device_type.lower():
            adjusted['device_type'] = 0.1  # Major reduction
        else:
            adjusted['device_type'] = 1.0
        
        # Water resistance: IPX7+ gets multiplier
        water_res = raw_specs.get('water_resistance', 0)
        if water_res >= 0.7:  # IPX7+
            adjusted['water_resistance'] = min(1.0, adjusted.get('water_resistance', 0) * 1.25)
        elif water_res == 0:  # None
            adjusted['water_resistance'] = 0.2  # Major reduction
        
        return adjusted


class WorkCallsStrategy(BaseStrategy):
    """
    Work Calls Use Case
    Critical: Mic count (dominant factor)
    Important: Low latency
    Secondary: ANC, battery
    """
    
    weights = {
        'num_mics': BaseStrategy.CRITICAL * 1.5,    # 0.45 (dominant)
        'latency': BaseStrategy.IMPORTANT,          # 0.15
        'battery_life': BaseStrategy.IMPORTANT,     # 0.15
        'price': BaseStrategy.IMPORTANT,            # 0.15 (value matters)
        'driver_size': BaseStrategy.SECONDARY,      # 0.05
        'water_resistance': BaseStrategy.SECONDARY, # 0.05
    }
    
    def adjust_scores(self, normalized_scores, raw_specs):
        adjusted = normalized_scores.copy()
        
        # Mic count: Strong positive curve
        num_mics = raw_specs.get('num_mics', 0)
        if num_mics >= 8:
            adjusted['num_mics'] = 1.0  # Excellent (8+ mics)
        elif num_mics >= 4:
            adjusted['num_mics'] = 0.8  # Very good (4-7 mics)
        elif num_mics >= 2:
            adjusted['num_mics'] = 0.5  # Average (2-3 mics)
        else:
            adjusted['num_mics'] = 0.2  # Poor (0-1 mics)
        
        return adjusted


class TravelStrategy(BaseStrategy):
    """
    Travel Use Case
    Critical: Battery life, ANC
    Important: Wireless, Water resistance, comfort
    Secondary:  driver size
    """
    
    weights = {
        'battery_life': BaseStrategy.CRITICAL,      # 0.3
        'device_type': BaseStrategy.CRITICAL,       # 0.3 (wireless preference)
        'water_resistance': BaseStrategy.IMPORTANT, # 0.15
        'price': BaseStrategy.IMPORTANT,            # 0.15 (budget-conscious travelers)
        'driver_size': BaseStrategy.SECONDARY,      # 0.05
        'num_mics': BaseStrategy.SECONDARY,         # 0.05
    }
    
    def adjust_scores(self, normalized_scores, raw_specs):
        adjusted = normalized_scores.copy()
        
        # Wireless preference
        device_type = raw_specs.get('device_type', '')
        if 'wireless' in device_type.lower():
            adjusted['device_type'] = 1.0
        else:
            adjusted['device_type'] = 0.5
        
        return adjusted


class CasualMusicStrategy(BaseStrategy):
    """
    Casual Music Use Case
    Critical: Price (budget-sensitive), battery
    Important: Comfort
    Secondary: Everything else
    """
    
    weights = {
        'price': BaseStrategy.CRITICAL,             # 0.3 (inverse - lower is better)
        'battery_life': BaseStrategy.CRITICAL,      # 0.3
        'driver_size': BaseStrategy.IMPORTANT,      # 0.15
        'water_resistance': BaseStrategy.IMPORTANT, # 0.15
        'device_type': BaseStrategy.SECONDARY,      # 0.05
        'num_mics': BaseStrategy.SECONDARY,         # 0.05
    }
    
    def adjust_scores(self, normalized_scores, raw_specs):
        adjusted = normalized_scores.copy()
        
        # Price: Use normalized score for finer granularity
        # Already normalized with inverse (cheaper = higher score)
        # No override needed - normalized price already reflects value
        
        return adjusted


# Strategy registry
STRATEGIES = {
    'gaming': GamingStrategy(),
    'gym': GymStrategy(),
    'work_calls': WorkCallsStrategy(),
    'travel': TravelStrategy(),
    'casual_music': CasualMusicStrategy(),
}


def get_strategy(use_case_name: str) -> BaseStrategy:
    """Get strategy for a use case name"""
    return STRATEGIES.get(use_case_name, BaseStrategy())
