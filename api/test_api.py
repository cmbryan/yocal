import pytest
from datetime import date
from flask import Flask
from jinja2 import Environment, FileSystemLoader
from .api import _get_date, get_test_display


def test_get_date_june_11_2025():
    """
    Test the _get_date function for June 11, 2025

    This is a day with a commemoration, a fore-feast, and a liturgy.

    """
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


def test_get_date_june_12_2025():
    """
    Test the _get_date function for June 12, 2025

    This is a day without a commemoration

    """
    test_date = date(2025, 6, 12)
    result = _get_date(test_date)
    
    assert isinstance(result, dict)
    
    # Check the structure of lections
    assert isinstance(result["lections"], dict)
    assert "basic" in result["lections"]
    assert "commem" in result["lections"]
    assert "liturgy" in result["lections"]

    assert result["lections"]["basic"] == ['Romans 1:28-2:9', 'Matthew 5:27-32']
    assert not result["lections"]["commem"]
    assert result["lections"]["liturgy"] == result["lections"]["basic"]
    assert result["texts"]["basic"][0].startswith('<em>Romans')
    assert result["texts"]["basic"][1].startswith('<em>Matthew')
    assert not result["texts"]["commem"]


@pytest.mark.parametrize("test_date,expected_file", [
    (date(2025, 6, 11), 'api/test_res/test_api_output_june_11.html'),
    (date(2025, 6, 12), 'api/test_res/test_api_output_june_12.html'),
])
def test_test_display_template(test_date, expected_file):
    # Create test data
    data = _get_date(test_date)
    
    # Create a Flask app for testing
    app = Flask(__name__)
    with app.test_request_context(f'/test-display?year={test_date.year}&month={test_date.month}&day={test_date.day}'):
        # Get the rendered template
        response = get_test_display()
        
        # Read the expected output file
        with open(expected_file, 'r') as f:
            expected_output = f.read()
            
        # Compare the response with expected output
        if response.strip() != expected_output.strip():
            # Write the actual response to a file for comparison
            actual_file = expected_file.replace('.html', '_actual.html')
            with open(actual_file, 'w') as f:
                f.write(response)
            
            # Assert that they match
            assert response.strip() == expected_output.strip(), \
                f"Template output does not match expected output for {test_date}." \
                f" diff {expected_file} {actual_file} for more details"
