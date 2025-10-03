import unittest
import sqlite3
import os
from datetime import date
from unittest.mock import MagicMock, patch

# Assuming choir_cues.py is in the same directory or accessible
from cc_api.choir_cues import (
    Antiphon,
    get_data,
    get_antiphons,
    get_entrance_hymn,
    get_apolytikia,
    main
)

class TestChoirCues(unittest.TestCase):

    def setUp(self):
        # Set up connections to the actual databases
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..'))

        self.main_db_path = os.path.join(project_root, 'db', 'yocal', 'YOCal_Master.db')
        self.static_db_path = os.path.join(project_root, 'db', 'yocal', 'YOCal.db')

        self.main_conn = sqlite3.connect(self.main_db_path)
        self.static_conn = sqlite3.connect(self.static_db_path)
        self.main_conn.row_factory = sqlite3.Row
        self.static_conn.row_factory = sqlite3.Row
        self.main_cur = self.main_conn.cursor()
        self.static_cur = self.static_conn.cursor()


    def tearDown(self):
        self.main_conn.close()
        self.static_conn.close()

    def test_get_data(self):
        target_date = date(2023, 12, 25)
        data = get_data(self.main_cur, target_date)
        self.assertEqual(data['day_name'], 'Monday')
        self.assertEqual(data['major_commem'], 'Nativity of our Lord and Saviour Jesus Christ')

    def test_get_antiphons(self):
        target_date = date(2023, 9, 14)
        antiphons = get_antiphons(self.static_cur, target_date)
        self.assertEqual(len(antiphons), 3)
        self.assertIsInstance(antiphons[0], Antiphon)
        self.assertEqual(antiphons[0].verses, [
            'O God, my God, hear me; why have You forsaken me?',
            'The words of my transgressions are far from my salvation.',
            'O my God, I will cry out by day, but You will not hear me.',
            'But You dwell among the saints, O praise of Israel.',
            'Glory...both now and ever...'
        ])
        self.assertEqual(antiphons[0].chorus, 'Through the intercessions of the Theotokos, Savior, save us.')

    def test_get_antiphons_no_results(self):
        target_date = date(2023, 1, 1)
        antiphons = get_antiphons(self.static_cur, target_date)
        self.assertFalse(antiphons)

    def test_get_entrance_hymn(self):
        target_date = date(2023, 9, 15)
        hymn = get_entrance_hymn(self.static_cur, target_date)
        self.assertEqual(
            hymn,
            "Exalt the Lord our God, and worship at the footstool of his feet; for he is holy."
            " Save us, O Son of God, who were crucified in the flesh. We sing to you, Alleluia."
        )

    def test_get_entrance_hymn_no_result(self):
        target_date = date(2023, 1, 1)
        hymn = get_entrance_hymn(self.static_cur, target_date)
        self.assertIsNone(hymn)

    def test_get_apolytikia_sunday_forefeast(self):
        # Sunday, Forefeast of the Nativity
        data = {
            'day_name': 'Sunday',
            'tone': 'Tone 1',
            'major_commem': None,
            'fore_after': 'Forefeast of the Nativity'
        }
        apolytikia = get_apolytikia(self.static_cur, data)
        self.assertEqual(len(apolytikia[0]), 1)
        self.assertEqual(apolytikia[0][0][0], 'Resurrectional Troparion, tone 1')
        self.assertIsInstance(apolytikia[0][0][1], str)
        self.assertEqual(
            apolytikia[0][0][1],
            "The stone having been sealed by the Pharisees and chief priests, and Your all-immaculate body"
            " being guarded by soldiers, You rose on the third day, O Lord and Savior, granting life unto the"
            " world. Then the powers of the heavens cried out to You, O Giver of Life, and shouted, “Glory"
            " to Your resurrection, O Christ! Glory to Your eternal rule! Glory to Your plan for saving us,"
            " only benevolent God!”"
        )

    def test_get_apolytikia_major_feast(self):
        # Sunday, Resurrectional Troparion Tone 8
        data = {
            'day_name': 'Sunday',
            'tone': 'Tone 8',
            'major_commem': None,
            'fore_after': None
        }
        apolytikia = get_apolytikia(self.static_cur, data)
        self.assertEqual(len(apolytikia[0]), 1)
        self.assertEqual(apolytikia[0][0][0], 'Resurrectional Troparion, tone 8')
        self.assertEqual(
            apolytikia[0][0][1],
            "You descended from on high, O compassionate One, and consented to a three-day burial, to free"
            " us from the passions. O Lord, our life and resurrection, glory to You!"
        )

    def test_get_apolytikia_sunday_only(self):
        # Sunday, no feast
        data = {
            'day_name': 'Sunday',
            'tone': 'Tone 3',
            'major_commem': None,
            'fore_after': None
        }
        apolytikia = get_apolytikia(self.static_cur, data)
        self.assertEqual(len(apolytikia[0]), 1)
        self.assertEqual(apolytikia[0][0][0], 'Resurrectional Troparion, tone 3')
        self.assertEqual(
            apolytikia[0][0][1],
            "Let the heavens be glad. Let the earth rejoice exceedingly. For the Lord has shown strength"
            " with his arm. He trampled death by death. He became the first-born of the dead. Out of the"
            " belly of Hades, He has rescued us, and to the world He has granted the great mercy."
        )

    @patch('cc_api.choir_cues.argparse.ArgumentParser')
    @patch('cc_api.choir_cues.sqlite3')
    @patch('cc_api.choir_cues.Environment')
    @patch('cc_api.choir_cues.get_data')
    @patch('cc_api.choir_cues.get_antiphons')
    @patch('cc_api.choir_cues.get_entrance_hymn')
    @patch('cc_api.choir_cues.get_apolytikia')
    @patch('builtins.print')
    def test_main(self, mock_print, mock_get_apolytikia, mock_get_entrance_hymn,
                  mock_get_antiphons, mock_get_data, mock_env, mock_sqlite, mock_argparse):
        # Mock argparse
        mock_args = MagicMock()
        mock_args.date = '2023-12-25'
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_argparse.return_value = mock_parser

        # Mock sqlite connections and cursors
        mock_main_conn = MagicMock()
        mock_static_conn = MagicMock()
        mock_main_cur = MagicMock()
        mock_static_cur = MagicMock()
        mock_sqlite.connect.side_effect = [mock_main_conn, mock_static_conn]
        mock_main_conn.__enter__().cursor.return_value = mock_main_cur
        mock_static_conn.__enter__().cursor.return_value = mock_static_cur

        # Mock data-fetching functions
        mock_data = {'key': 'value'}
        mock_get_data.return_value = mock_data
        mock_get_antiphons.return_value = 'antiphons'
        mock_get_entrance_hymn.return_value = 'entrance_hymn'
        mock_get_apolytikia.return_value = 'apolytikia'

        # Mock Jinja2 environment and template
        mock_template = MagicMock()
        mock_loader = MagicMock()
        mock_env.return_value = mock_loader
        mock_loader.get_template.return_value = mock_template

        main()

        # Assertions
        mock_argparse.assert_called_once()
        mock_sqlite.connect.assert_any_call(self.main_db_path)
        mock_sqlite.connect.assert_any_call(self.static_db_path)

        target_date = date(2023, 12, 25)
        mock_get_data.assert_called_once_with(mock_main_cur, target_date)
        mock_get_antiphons.assert_called_once_with(mock_static_cur, target_date)
        mock_get_entrance_hymn.assert_called_once_with(mock_static_cur, target_date)
        mock_get_apolytikia.assert_called_once_with(mock_static_cur, mock_data)

        mock_env.assert_called_once()
        mock_loader.get_template.assert_called_with("cc_template.html")

        expected_render_data = {
            'key': 'value',
            'antiphons': 'antiphons',
            'entrance_hymn': 'entrance_hymn',
            'apolytikia': 'apolytikia'
        }
        mock_template.render.assert_called_once_with(**expected_render_data)
        mock_print.assert_called_once_with(mock_template.render.return_value)


if __name__ == '__main__':
    unittest.main()
