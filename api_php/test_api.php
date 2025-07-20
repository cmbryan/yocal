<?php

use PHPUnit\Framework\TestCase;

require_once 'functions.php';

class test_api extends TestCase
{
    public function testGetDateJune112025()
    {
        $test_date = new DateTime('2025-06-11');
        $result = _get_date($test_date);

        $this->assertIsArray($result);
        $this->assertArrayHasKey('day_name', $result);
        $this->assertArrayHasKey('day_ord', $result);
        $this->assertArrayHasKey('month', $result);
        $this->assertArrayHasKey('year', $result);
        $this->assertArrayHasKey('fast', $result);
        $this->assertArrayHasKey('tone', $result);
        $this->assertArrayHasKey('eothinon', $result);
        $this->assertArrayHasKey('liturgy', $result);
        $this->assertArrayHasKey('desig', $result);
        $this->assertArrayHasKey('commem', $result);
        $this->assertArrayHasKey('fore_after', $result);
        $this->assertArrayHasKey('global_saints', $result);
        $this->assertArrayHasKey('british_saints', $result);
        $this->assertArrayHasKey('lections', $result);
        $this->assertArrayHasKey('texts', $result);

        $this->assertEquals(2025, $result['year']);
        $this->assertEquals('June', $result['month']);
        $this->assertEquals('11th', $result['day_ord']);

        $this->assertIsArray($result['lections']);
        $this->assertArrayHasKey('basic', $result['lections']);
        $this->assertArrayHasKey('commem', $result['lections']);
        $this->assertArrayHasKey('liturgy', $result['lections']);

        $this->assertEquals(['Romans 1:18-27', 'Matthew 5:20-26'], $result['lections']['basic']);
        $this->assertEquals(['Acts 11:19-30', 'Luke 10:16-21'], $result['lections']['commem']);
        $this->assertEquals(['Acts 11:19-30', 'Matthew 5:20-26'], $result['lections']['liturgy']);

        $this->assertStringStartsWith('<em>Romans', $result['texts']['basic'][0]);
        $this->assertStringStartsWith('<em>Matthew', $result['texts']['basic'][1]);
        $this->assertStringStartsWith('<em>Acts', $result['texts']['commem'][0]);
        $this->assertStringStartsWith('<em>Luke', $result['texts']['commem'][1]);
    }

    public function testGetDateJune122025()
    {
        $test_date = new DateTime('2025-06-12');
        $result = _get_date($test_date);

        $this->assertIsArray($result);

        $this->assertIsArray($result['lections']);
        $this->assertArrayHasKey('basic', $result['lections']);
        $this->assertArrayHasKey('commem', $result['lections']);
        $this->assertArrayHasKey('liturgy', $result['lections']);

        $this->assertEquals(['Romans 1:28-2:9', 'Matthew 5:27-32'], $result['lections']['basic']);
        $this->assertEmpty($result['lections']['commem']);
        $this->assertEquals($result['lections']['basic'], $result['lections']['liturgy']);

        $this->assertStringStartsWith('<em>Romans', $result['texts']['basic'][0]);
        $this->assertStringStartsWith('<em>Matthew', $result['texts']['basic'][1]);
        $this->assertEmpty($result['texts']['commem']);
    }

    /**
     * @dataProvider displayTestProvider
     */
    public function testTestDisplayTemplate($test_date, $expected_file)
    {
        $data = _get_date($test_date);
        $response = render_template(__DIR__ . '/templates/test_display.html.twig', ['data' => $data]);
        $expected_output = file_get_contents($expected_file);

        // Extract content up to the debug section to ignore debug output differences
        $response_body = substr($response, 0, strpos($response, 'Debug:<br/>'));
        $expected_body = substr($expected_output, 0, strpos($expected_output, 'Debug:<br/>'));

        $response_body = substr($response, 0, strpos($response, 'Debug:<br/>'));
        $expected_body = substr($expected_output, 0, strpos($expected_output, 'Debug:<br/>'));

        $dom_response = new DOMDocument();
        @$dom_response->loadHTML($response_body, LIBXML_HTML_NOIMPLIED | LIBXML_HTML_NODEFDTD);
        $dom_expected = new DOMDocument();
        @$dom_expected->loadHTML($expected_body, LIBXML_HTML_NOIMPLIED | LIBXML_HTML_NODEFDTD);

        $this->assertEqualXMLStructure($dom_expected->documentElement, $dom_response->documentElement);
    }

    public function displayTestProvider()
    {
        return [
            [new DateTime('2025-06-11'), __DIR__ . '/../api_python/test_res/test_api_output_june_11.html'],
            [new DateTime('2025-06-12'), __DIR__ . '/../api_python/test_res/test_api_output_june_12.html'],
        ];
    }
}
