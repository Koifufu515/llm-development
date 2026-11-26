import json
import pytest
from deepeval.test_case import LLMTestCase
from evaluation.router_metric import RouterCorrectnessMetric
from evaluation.itinerary_cases import ITINERARY_CASES
@pytest.mark.parametrize('expected,empty,skills,actual,result',[(True,False,[],True,1),(False,False,[],True,0),(False,True,[],False,0),(False,False,['weather_query'],False,1)])
def test_source_deterministic_metric(expected,empty,skills,actual,result):
 metric=RouterCorrectnessMetric(expected,skills,empty)
 tc=LLMTestCase(input='test',actual_output=json.dumps({'is_itinerary_planning':actual,'skills':[{'skill_name':'weather_query'}]}))
 assert metric.measure(tc)==result

def test_original_fixture_matrix_and_contradiction():
 assert len(ITINERARY_CASES)==6 and sum(c['positive'] for c in ITINERARY_CASES)==3
 with pytest.raises(ValueError):RouterCorrectnessMetric(False,['weather_query'],True)
