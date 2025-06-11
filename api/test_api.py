import pytest
from datetime import date
from flask import Flask
from jinja2 import Environment, FileSystemLoader
from .api import _get_date, get_test_display

def test_get_date_june_11_2025():
    # Test date: June 11, 2025
    test_date = date(2025, 6, 11)
    result = _get_date(test_date)
    
    # Basic assertions about the structure and content
    assert isinstance(result, dict)
    assert "day_name" in result
    assert "day_ord" in result
    assert "month" in result
    assert "year" in result
    assert "fast" in result
    assert "tone" in result
    assert "eothinon" in result
    assert "liturgy" in result
    assert "desig" in result
    assert "commem" in result
    assert "fore_after" in result
    assert "global_saints" in result
    assert "british_saints" in result
    assert "lections" in result
    assert "texts" in result
    
    # Specific assertions for June 11, 2025
    assert result["year"] == 2025
    assert result["month"] == "June"
    assert result["day_ord"] == "11th"
    
    # Check the structure of lections
    assert isinstance(result["lections"], dict)
    assert "basic" in result["lections"]
    assert "commem" in result["lections"]
    assert "liturgy" in result["lections"]

    assert result["lections"]["basic"] == ['Romans 1:18-27', 'Matthew 5:20-26']
    assert result["lections"]["commem"] == ['Acts 11:19-30', 'Luke 10:16-21']
    assert result["lections"]["liturgy"] == ['Acts 11:19-30', 'Matthew 5:20-26']
    assert result["texts"]["basic"][0].startswith('<em>Romans')
    assert result["texts"]["basic"][1].startswith('<em>Matthew')
    assert result["texts"]["commem"][0].startswith('<em>Acts')
    assert result["texts"]["commem"][1].startswith('<em>Luke')


def test_test_display_template():
    # Create test data
    test_date = date(2025, 6, 11)
    data = _get_date(test_date)
    
    # Create a Flask app for testing
    app = Flask(__name__)
    with app.test_request_context('/test-display?year=2025&month=6&day=11'):
        # Get the rendered template
        response = get_test_display()
        
        # Read the expected output file
        with open('api/test_res/test_api_output.html', 'r') as f:
            expected_output = f.read()
            
        # Compare the response with expected output
        if response.strip() != expected_output.strip():
            # Write the actual response to a file for comparison
            with open('api/test_res/test_api_output_actual.html', 'w') as f:
                f.write(response)
            
            # Assert that they match
            assert response.strip() == expected_output.strip(), \
                "Template output does not match expected output." \
                " diff api/test_res/test_api_output.html api/test_res/test_api_output_actual.html " \
                " for more details"
        