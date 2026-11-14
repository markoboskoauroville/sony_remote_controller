package com.mantraproductions.sonyremote

/**
 * The two places a picture can come from. The phone has one Wi-Fi radio, so it is on one of them
 * at a time: switching is stop one, change network, start the other (PLAN.md §2c).
 */
enum class Source(val id: String, val title: String, val detail: String) {
    SONY_DIRECT("sony", "SONY DIRECT", "A7 V, over the camera's own Wi-Fi"),
    ACCSOON("accsoon", "ACCSOON", "CineView Nano picture, camera keys over Bluetooth");

    companion object {
        /** The source a saved id names, or none: a name from an older build is not an error. */
        fun fromId(id: String?): Source? = entries.firstOrNull { it.id == id }
    }
}

/** Every key on the rails, in rail order. The words are what the key shows. */
enum class Key(val word: String) {
    AF("AF"), MF("MF"), ISO("ISO"), SHUTTER("SHUT"), IRIS("F"), EV("EV"), WB("WB"),
    REC("REC"), SNAP("SNAP"), FULL("FULL");

    /** FULL is the viewer's own (nothing on the glass but the picture); every other key drives the camera. */
    val drivesCamera: Boolean get() = this != FULL
}

/** What a key shows: the RailButton language, grey off, green on, dark when it cannot. */
enum class Lit { OFF, ON, DEAD }

object Keys {
    /**
     * What each source will be able to do once it is built (PLAN.md §2c's table). Sony Direct reaches
     * every setting over PTP/IP; the Accsoon side reaches the camera only through its Bluetooth remote
     * service, which has buttons and jogs but no settings, so ISO, shutter, iris, EV and WB stay dark
     * there for good.
     */
    fun offers(source: Source, key: Key): Boolean = when (source) {
        Source.SONY_DIRECT -> true
        Source.ACCSOON -> key in setOf(Key.AF, Key.MF, Key.REC, Key.SNAP, Key.FULL)
    }

    /**
     * How a key is drawn now. A camera key is dark until its step is built AND the camera is there;
     * dark rather than hidden, so the rails never reshuffle and a hand learns where things are.
     */
    fun lit(source: Source, key: Key, built: Set<Key>, connected: Boolean, on: Boolean): Lit = when {
        !offers(source, key) -> Lit.DEAD
        key.drivesCamera && (key !in built || !connected) -> Lit.DEAD
        on -> Lit.ON
        else -> Lit.OFF
    }

    /** Step 0: nothing reaches the camera yet. Each step adds the keys it built. */
    val BUILT: Set<Key> = emptySet()
}

object Geometry {
    /**
     * The largest box of [aspect] that fits, and the margin left over across and down: where the
     * rails go. Copied from mantra-ndi's Mechanism.pictureBox, which carries the reasons.
     *
     * @return width, height, margin across, margin down
     */
    fun pictureBox(availableWidth: Int, availableHeight: Int, aspect: Double = 16.0 / 9.0): IntArray {
        if (availableWidth <= 0 || availableHeight <= 0 || aspect <= 0.0) return intArrayOf(0, 0, 0, 0)
        var width = availableWidth
        var height = Math.round(width / aspect).toInt()
        if (height > availableHeight) {
            height = availableHeight
            width = Math.round(height * aspect).toInt()
        }
        return intArrayOf(width, height, availableWidth - width, availableHeight - height)
    }

    /** The double tap that opens the sources counts only in the central half, so a hand at the edges never opens it. */
    fun inMiddle(x: Float, y: Float, width: Float, height: Float): Boolean =
        x in width * 0.25f..width * 0.75f && y in height * 0.25f..height * 0.75f
}
