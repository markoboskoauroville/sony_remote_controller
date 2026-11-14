package com.mantraproductions.sonyremote

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class KeysTest {
    @Test fun sourcesSurviveTheirSavedId() {
        for (s in Source.entries) assertEquals(s, Source.fromId(s.id))
        assertNull(Source.fromId(null))
        assertNull(Source.fromId("ndi"))
    }

    @Test fun accsoonNeverOffersASetting() {
        for (k in listOf(Key.ISO, Key.SHUTTER, Key.IRIS, Key.EV, Key.WB)) {
            assertFalse(k.name, Keys.offers(Source.ACCSOON, k))
            assertEquals(Lit.DEAD, Keys.lit(Source.ACCSOON, k, Key.entries.toSet(), connected = true, on = false))
        }
    }

    @Test fun accsoonOffersTheBluetoothButtons() {
        for (k in listOf(Key.AF, Key.MF, Key.REC, Key.SNAP)) assertTrue(k.name, Keys.offers(Source.ACCSOON, k))
    }

    @Test fun sonyDirectOffersEverything() {
        for (k in Key.entries) assertTrue(k.name, Keys.offers(Source.SONY_DIRECT, k))
    }

    @Test fun stepZeroHasEveryCameraKeyDarkAndFullWorking() {
        for (s in Source.entries) for (k in Key.entries) {
            val lit = Keys.lit(s, k, Keys.BUILT, connected = false, on = false)
            assertEquals("$s $k", if (k == Key.FULL) Lit.OFF else Lit.DEAD, lit)
        }
    }

    @Test fun aBuiltKeyIsStillDarkWithoutTheCamera() {
        assertEquals(Lit.DEAD, Keys.lit(Source.SONY_DIRECT, Key.REC, setOf(Key.REC), connected = false, on = false))
        assertEquals(Lit.OFF, Keys.lit(Source.SONY_DIRECT, Key.REC, setOf(Key.REC), connected = true, on = false))
        assertEquals(Lit.ON, Keys.lit(Source.SONY_DIRECT, Key.REC, setOf(Key.REC), connected = true, on = true))
    }
}

class GeometryTest {
    @Test fun aWidePhoneGetsSideRails() {
        // a Pixel 7 held across, 2400 x 1080: the picture is 1920 wide and 480 is left for the rails
        assertArrayEquals(intArrayOf(1920, 1080, 480, 0), Geometry.pictureBox(2400, 1080))
    }

    @Test fun anUprightPhoneGetsBands() {
        assertArrayEquals(intArrayOf(1080, 608, 0, 1792), Geometry.pictureBox(1080, 2400))
    }

    @Test fun stillsAreThreeToTwo() {
        assertArrayEquals(intArrayOf(1620, 1080, 780, 0), Geometry.pictureBox(2400, 1080, 3.0 / 2.0))
    }

    @Test fun nothingToMeasureIsNoBox() {
        assertArrayEquals(intArrayOf(0, 0, 0, 0), Geometry.pictureBox(0, 1080))
    }

    @Test fun onlyTheMiddleOpensTheSources() {
        assertTrue(Geometry.inMiddle(500f, 500f, 1000f, 1000f))
        assertFalse(Geometry.inMiddle(100f, 500f, 1000f, 1000f))
        assertFalse(Geometry.inMiddle(500f, 900f, 1000f, 1000f))
    }
}
