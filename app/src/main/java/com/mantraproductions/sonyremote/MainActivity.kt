package com.mantraproductions.sonyremote

import android.app.Activity
import android.content.res.Configuration
import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.view.GestureDetector
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.view.WindowInsets
import android.view.WindowInsetsController
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.TextView

/**
 * STEP 0 (PLAN.md §3): the stage, without a camera yet.
 *
 * The Mantra layout: the picture in its own shape in the middle, the keys in the black either side
 * of it (above and below when the phone is upright), and a double tap in the middle of the screen
 * that opens THE SOURCES, as Mantra Monitor does. The choice is kept and comes back at the next start.
 * Every camera key is dark until the step that builds it; FULL works, because it is the viewer's own.
 */
class MainActivity : Activity() {

    private val prefs by lazy { getSharedPreferences("remote", MODE_PRIVATE) }

    private lateinit var root: FrameLayout
    private lateinit var stage: LinearLayout
    private lateinit var railA: LinearLayout
    private lateinit var railB: LinearLayout
    private lateinit var picture: AspectFrame
    private lateinit var status: TextView
    private lateinit var picker: FrameLayout
    private lateinit var list: LinearLayout
    private val keys = LinkedHashMap<Key, RailButton>()

    private var source: Source? = null
    private var full = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        root = FrameLayout(this).apply { setBackgroundColor(Color.BLACK) }
        stage = LinearLayout(this).apply { gravity = Gravity.CENTER }
        railA = LinearLayout(this).apply { setPadding(dp(3), dp(3), dp(3), dp(3)) }
        railB = LinearLayout(this).apply { setPadding(dp(3), dp(3), dp(3), dp(3)) }
        picture = AspectFrame(this).apply { setBackgroundColor(INK) }
        status = word("", SAND, 12f).apply {
            gravity = Gravity.CENTER
            setPadding(dp(12), dp(8), dp(12), dp(8))
        }
        picture.addView(status, FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.WRAP_CONTENT, Gravity.CENTER))

        // Left rail (top when upright): focus and the exposure settings. Right rail: the triggers and FULL.
        for (k in listOf(Key.AF, Key.MF, Key.ISO, Key.SHUTTER, Key.IRIS, Key.EV, Key.WB)) railA.addView(key(k))
        for (k in listOf(Key.REC, Key.SNAP, Key.FULL)) railB.addView(key(k))
        keys.getValue(Key.SNAP).glyph = RailButton.Glyph.CAMERA
        keys.getValue(Key.FULL).setOnClickListener { setFull(true) }

        stage.addView(railA)
        stage.addView(picture)
        stage.addView(railB)
        root.addView(stage, FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT))

        picker = buildPicker()
        root.addView(picker, FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT))
        setContentView(root)

        val taps = GestureDetector(this, object : GestureDetector.SimpleOnGestureListener() {
            override fun onDoubleTap(e: MotionEvent): Boolean {
                // In FULL a double tap anywhere brings the keys back; otherwise only the middle opens the sources.
                if (full) setFull(false)
                else if (Geometry.inMiddle(e.x, e.y, root.width.toFloat(), root.height.toFloat())) showPicker(true)
                return true
            }
            override fun onDown(e: MotionEvent) = true
        })
        // Over the whole stage, under the keys: a key takes its own taps first.
        stage.setOnTouchListener { _, ev -> taps.onTouchEvent(ev) }

        arrange(resources.configuration.orientation)
        choose(Source.fromId(prefs.getString("source", null)), remember = false)
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (hasFocus) window.insetsController?.let {
            it.hide(WindowInsets.Type.systemBars())
            it.systemBarsBehavior = WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        }
    }

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        arrange(newConfig.orientation)
    }

    /** Across: rails left and right of the picture. Upright: bands above and below. The keys' order never changes. */
    private fun arrange(orientation: Int) {
        val across = orientation != Configuration.ORIENTATION_PORTRAIT
        stage.orientation = if (across) LinearLayout.HORIZONTAL else LinearLayout.VERTICAL
        for (rail in listOf(railA, railB)) {
            rail.orientation = if (across) LinearLayout.VERTICAL else LinearLayout.HORIZONTAL
            rail.layoutParams = if (across) LinearLayout.LayoutParams(dp(64), LinearLayout.LayoutParams.MATCH_PARENT)
                else LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(56))
            for (i in 0 until rail.childCount) rail.getChildAt(i).layoutParams =
                if (across) LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f)
                else LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.MATCH_PARENT, 1f)
        }
        picture.layoutParams = if (across) LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.MATCH_PARENT, 1f)
            else LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f)
    }

    private fun key(k: Key) = RailButton(this).apply { label = k.word }.also { keys[k] = it }

    private fun paintKeys() {
        val s = source
        for ((k, b) in keys) {
            val lit = if (s == null) (if (k.drivesCamera) Lit.DEAD else Lit.OFF)
                else Keys.lit(s, k, Keys.BUILT, connected = false, on = k == Key.FULL && full)
            b.state = when (lit) { Lit.ON -> RailButton.State.ON; Lit.OFF -> RailButton.State.OFF; Lit.DEAD -> RailButton.State.DEAD }
        }
    }

    private fun choose(s: Source?, remember: Boolean = true) {
        source = s
        if (remember && s != null) prefs.edit().putString("source", s.id).apply()
        status.text = when (s) {
            null -> "Double tap in the middle to choose a source"
            Source.SONY_DIRECT -> "SONY DIRECT · ${s.detail}\nnot connected: the camera link arrives in Step 1"
            Source.ACCSOON -> "ACCSOON · ${s.detail}\nnot connected: the CineView link arrives in Step A1"
        }
        paintKeys()
    }

    private fun setFull(on: Boolean) {
        full = on
        val v = if (on) View.INVISIBLE else View.VISIBLE
        railA.visibility = v; railB.visibility = v; status.visibility = v
        paintKeys()
    }

    // THE SOURCES: the list over the picture, as in Mantra Monitor. Words, not boxes; green is the one in use.
    private fun buildPicker() = FrameLayout(this).apply {
        setBackgroundColor(Color.parseColor("#E60B0D10"))
        visibility = View.GONE
        isClickable = true
        list = LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(28), dp(20), dp(28), dp(20))
        }
        addView(list, FrameLayout.LayoutParams(dp(420).coerceAtMost(resources.displayMetrics.widthPixels),
            FrameLayout.LayoutParams.WRAP_CONTENT, Gravity.CENTER))
    }

    private fun showPicker(on: Boolean) {
        picker.visibility = if (on) View.VISIBLE else View.GONE
        if (!on) return
        list.removeAllViews()
        val head = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL }
        head.addView(word("SOURCES", AMBER, 13f), LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f))
        head.addView(word("✕", SAND, 20f).apply { setOnClickListener { showPicker(false) } })
        list.addView(head)
        for (s in Source.entries) {
            val colour = if (s == source) RailButton.GREEN else SAND
            list.addView(word(s.title, colour, 16f).apply { setOnClickListener { showPicker(false); choose(s) } })
            list.addView(word(s.detail, QUIET, 11f).apply {
                setPadding(0, 0, 0, dp(10))
                setOnClickListener { showPicker(false); choose(s) }
            })
        }
    }

    private fun word(text: String, colour: Int, size: Float) = TextView(this).apply {
        this.text = text; setTextColor(colour); textSize = size
        typeface = Typeface.create(Typeface.MONOSPACE, Typeface.BOLD)
        setPadding(0, dp(10), 0, dp(4))
    }

    private fun dp(v: Int) = (v * resources.displayMetrics.density).toInt()

    companion object {
        // The Mantra palette (mantra-ndi res/values/colors.xml), fixed across every Mantra app.
        val INK: Int = Color.parseColor("#0B0D10")
        val SAND: Int = Color.parseColor("#F2DDB4")
        val AMBER: Int = Color.parseColor("#F59E0B")
        val QUIET: Int = Color.parseColor("#6E7A86")
    }
}
