import unittest
import xml.etree.ElementTree as ET

from uwert import BEISPIEL, lade_aufbau, svg


class TestUWert(unittest.TestCase):
    def setUp(self):
        self.e = lade_aufbau(BEISPIEL, 20.0, -10.0)

    def test_u_wert_beispielwand(self):
        # README: Innenputz / Hochlochziegel / 18 cm EPS / Putz → U = 0,169 W/m²K
        self.assertAlmostEqual(self.e.u, 0.169, places=3)
        self.assertAlmostEqual(self.e.rt, 0.13 + 0.015 / 0.70 + 0.25 / 0.45 + 0.18 / 0.035 + 0.01 / 0.80 + 0.04)

    def test_temperaturverlauf_endet_an_aussenoberflaeche(self):
        t = self.e.temperaturen()
        q = self.e.u * 30.0
        self.assertAlmostEqual(t[-1], -10.0 + q * self.e.rse)
        self.assertTrue(all(a > b for a, b in zip(t, t[1:])))

    def test_frsi(self):
        self.assertAlmostEqual(self.e.f_rsi, 1 - 0.13 * self.e.u)
        self.assertGreater(self.e.f_rsi, 0.71)

    def test_eigenes_lambda(self):
        e = lade_aufbau({"typ": "dcAussen", "schichten": [{"name": "X", "d_cm": 10, "lambda": 0.05}]}, 20, -10)
        self.assertAlmostEqual(e.rt, 0.10 + 2.0 + 0.04)

    def test_fehler(self):
        with self.assertRaises(ValueError):
            lade_aufbau({"schichten": [{"material": "Gibtsnicht", "d_cm": 5}]}, 20, -10)
        with self.assertRaises(ValueError):
            lade_aufbau({"schichten": [{"material": "Vollziegel", "d_cm": 0}]}, 20, -10)
        with self.assertRaises(ValueError):
            lade_aufbau({"typ": "xyz", "schichten": [{"material": "Vollziegel", "d_cm": 5}]}, 20, -10)

    def test_svg_ist_gueltiges_xml(self):
        root = ET.fromstring(svg(self.e))
        self.assertTrue(root.tag.endswith("svg"))


if __name__ == "__main__":
    unittest.main()
