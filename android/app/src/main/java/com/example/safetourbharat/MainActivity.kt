package com.example.safetourbharat

import android.Manifest
import android.annotation.SuppressLint
import android.app.AlertDialog
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.view.View
import android.view.ViewGroup
import android.webkit.*
import android.widget.*
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

class MainActivity : ComponentActivity() {

    private lateinit var webView: WebView
    private lateinit var progressBar: ProgressBar
    private lateinit var errorLayout: LinearLayout
    private lateinit var errorText: TextView

    private var filePathCallback: ValueCallback<Array<Uri>>? = null
    private var pendingGeoOrigin: String? = null
    private var pendingGeoCallback: GeolocationPermissions.Callback? = null

    private val PREFS_NAME = "SafeTourPrefs"
    private val KEY_SERVER_URL = "server_url"
    private val DEFAULT_SERVER_URL = "http://10.0.2.2:8000"
    private val LAN_HINT_URL = "http://192.168.1.104:8000"

    private val fileChooserLauncher: ActivityResultLauncher<Intent> =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
            if (filePathCallback != null) {
                val results: Array<Uri>? = if (result.resultCode == RESULT_OK && result.data != null) {
                    val data = result.data
                    if (data?.clipData != null) {
                        val count = data.clipData!!.itemCount
                        Array(count) { i -> data.clipData!!.getItemAt(i).uri }
                    } else if (data?.data != null) {
                        arrayOf(data.data!!)
                    } else null
                } else null
                filePathCallback?.onReceiveValue(results)
                filePathCallback = null
            }
        }

    private val locationPermissionLauncher: ActivityResultLauncher<Array<String>> =
        registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { permissions ->
            val fineGranted = permissions[Manifest.permission.ACCESS_FINE_LOCATION] ?: false
            val coarseGranted = permissions[Manifest.permission.ACCESS_COARSE_LOCATION] ?: false
            if (fineGranted || coarseGranted) {
                pendingGeoCallback?.invoke(pendingGeoOrigin, true, false)
            } else {
                pendingGeoCallback?.invoke(pendingGeoOrigin, false, false)
            }
            pendingGeoCallback = null
            pendingGeoOrigin = null
        }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val rootLayout = FrameLayout(this).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
        }

        webView = WebView(this).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            setLayerType(View.LAYER_TYPE_HARDWARE, null)
        }

        progressBar = ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal).apply {
            layoutParams = FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                8
            )
            isIndeterminate = false
            max = 100
            visibility = View.GONE
        }

        // Native Quick Action Bar at the top or bottom
        val headerLayout = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            layoutParams = FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            ).apply {
                topMargin = 0
            }
            setBackgroundColor(0xEE0B132B.toInt()) // Sleek dark navy theme
            setPadding(24, 12, 24, 12)
        }

        val titleView = TextView(this).apply {
            text = "SafeTour Bharat \uD83D\uDEE1\uFE0F"
            setTextColor(0xFFFFFFFF.toInt())
            textSize = 15f
            setTypeface(null, android.graphics.Typeface.BOLD)
            layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
        }

        val portalBtn = Button(this).apply {
            text = "EOC Portal"
            textSize = 11f
            setTextColor(0xFF38EF7D.toInt())
            setBackgroundColor(0x3310B981.toInt())
            setOnClickListener {
                val currentBase = getServerUrl()
                if (currentBase.startsWith("http")) {
                    webView.loadUrl("$currentBase/responder")
                } else {
                    webView.loadUrl("file:///android_asset/www/responder.html")
                }
            }
        }

        val sosBtn = Button(this).apply {
            text = "SOS 112"
            textSize = 11f
            setTextColor(0xFFFF4B2B.toInt())
            setBackgroundColor(0x33FF416C.toInt())
            setOnClickListener {
                val dialIntent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:112"))
                startActivity(dialIntent)
            }
        }

        val settingsBtn = ImageButton(this).apply {
            setImageResource(android.R.drawable.ic_menu_preferences)
            setBackgroundColor(0x00000000)
            setColorFilter(0xFFE2E8F0.toInt())
            setOnClickListener {
                showServerConfigDialog()
            }
        }

        headerLayout.addView(titleView)
        headerLayout.addView(portalBtn)
        headerLayout.addView(sosBtn)
        headerLayout.addView(settingsBtn)

        // Native Error Layout
        errorLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = android.view.Gravity.CENTER
            setBackgroundColor(0xFF0F172A.toInt())
            setPadding(48, 48, 48, 48)
            visibility = View.GONE
            layoutParams = FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
        }

        errorText = TextView(this).apply {
            text = "Unable to connect to SafeTour Bharat Backend"
            setTextColor(0xFFF87171.toInt())
            textSize = 18f
            gravity = android.view.Gravity.CENTER
            setPadding(0, 0, 0, 24)
        }

        val retryBtn = Button(this).apply {
            text = "Retry Connection"
            setBackgroundColor(0xFF2563EB.toInt())
            setTextColor(0xFFFFFFFF.toInt())
            setOnClickListener {
                errorLayout.visibility = View.GONE
                webView.visibility = View.VISIBLE
                loadActiveUrl()
            }
        }

        val configBtn = Button(this).apply {
            text = "Change Server IP / Mode"
            setBackgroundColor(0xFF334155.toInt())
            setTextColor(0xFFE2E8F0.toInt())
            setOnClickListener {
                showServerConfigDialog()
            }
        }

        val offlineBtn = Button(this).apply {
            text = "Load Bundled Offline Mode"
            setBackgroundColor(0xFF059669.toInt())
            setTextColor(0xFFFFFFFF.toInt())
            setOnClickListener {
                setServerUrl("file:///android_asset/www/index.html")
                errorLayout.visibility = View.GONE
                webView.visibility = View.VISIBLE
                webView.loadUrl("file:///android_asset/www/index.html")
            }
        }

        errorLayout.addView(errorText)
        errorLayout.addView(retryBtn)
        errorLayout.addView(configBtn)
        errorLayout.addView(offlineBtn)

        rootLayout.addView(webView)
        rootLayout.addView(headerLayout)
        rootLayout.addView(progressBar)
        rootLayout.addView(errorLayout)
        setContentView(rootLayout)

        configureWebView()
        requestInitialPermissions()

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (webView.canGoBack()) {
                    webView.goBack()
                } else {
                    finish()
                }
            }
        })

        loadActiveUrl()
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun configureWebView() {
        val s: WebSettings = webView.settings
        s.javaScriptEnabled = true
        s.domStorageEnabled = true
        s.databaseEnabled = true
        s.setGeolocationEnabled(true)
        s.allowFileAccess = true
        s.allowContentAccess = true
        s.cacheMode = WebSettings.LOAD_DEFAULT
        s.useWideViewPort = true
        s.loadWithOverviewMode = true
        s.displayZoomControls = false
        s.builtInZoomControls = true
        s.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW

        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView?, newProgress: Int) {
                if (newProgress < 100) {
                    progressBar.visibility = View.VISIBLE
                    progressBar.progress = newProgress
                } else {
                    progressBar.visibility = View.GONE
                }
            }

            override fun onGeolocationPermissionsShowPrompt(
                origin: String?,
                callback: GeolocationPermissions.Callback?
            ) {
                val fineGranted = ContextCompat.checkSelfPermission(
                    this@MainActivity,
                    Manifest.permission.ACCESS_FINE_LOCATION
                ) == PackageManager.PERMISSION_GRANTED

                val coarseGranted = ContextCompat.checkSelfPermission(
                    this@MainActivity,
                    Manifest.permission.ACCESS_COARSE_LOCATION
                ) == PackageManager.PERMISSION_GRANTED

                if (fineGranted || coarseGranted) {
                    callback?.invoke(origin, true, false)
                } else {
                    pendingGeoOrigin = origin
                    pendingGeoCallback = callback
                    locationPermissionLauncher.launch(
                        arrayOf(
                            Manifest.permission.ACCESS_FINE_LOCATION,
                            Manifest.permission.ACCESS_COARSE_LOCATION
                        )
                    )
                }
            }

            override fun onShowFileChooser(
                webView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                this@MainActivity.filePathCallback?.onReceiveValue(null)
                this@MainActivity.filePathCallback = filePathCallback

                val intent = fileChooserParams?.createIntent() ?: Intent(Intent.ACTION_GET_CONTENT).apply {
                    type = "image/*"
                    addCategory(Intent.CATEGORY_OPENABLE)
                }

                try {
                    fileChooserLauncher.launch(intent)
                } catch (e: Exception) {
                    this@MainActivity.filePathCallback = null
                    return false
                }
                return true
            }
        }

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val url = request?.url?.toString() ?: return false
                if (url.startsWith("tel:")) {
                    val intent = Intent(Intent.ACTION_DIAL, Uri.parse(url))
                    startActivity(intent)
                    return true
                }
                if (url.startsWith("mailto:")) {
                    val intent = Intent(Intent.ACTION_SENDTO, Uri.parse(url))
                    startActivity(intent)
                    return true
                }
                if (url.startsWith("geo:")) {
                    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                    startActivity(intent)
                    return true
                }
                return false
            }

            override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                super.onPageStarted(view, url, favicon)
                errorLayout.visibility = View.GONE
                webView.visibility = View.VISIBLE
            }

            override fun onReceivedError(
                view: WebView?,
                request: WebResourceRequest?,
                error: WebResourceError?
            ) {
                super.onReceivedError(view, request, error)
                if (request?.isForMainFrame == true) {
                    val failedUrl = request.url.toString()
                    errorText.text = "Connection Failed:\n$failedUrl\n\nEnsure backend server is running."
                    webView.visibility = View.GONE
                    errorLayout.visibility = View.VISIBLE
                }
            }
        }
    }

    private fun requestInitialPermissions() {
        val fineGranted = ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED

        if (!fineGranted) {
            locationPermissionLauncher.launch(
                arrayOf(
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION
                )
            )
        }
    }

    private fun getServerUrl(): String {
        val prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        return prefs.getString(KEY_SERVER_URL, DEFAULT_SERVER_URL) ?: DEFAULT_SERVER_URL
    }

    private fun setServerUrl(url: String) {
        val prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        prefs.edit().putString(KEY_SERVER_URL, url).apply()
    }

    private fun loadActiveUrl() {
        val url = getServerUrl()
        webView.loadUrl(url)
    }

    private fun showServerConfigDialog() {
        val builder = AlertDialog.Builder(this)
        builder.setTitle("Server Backend Configuration")

        val container = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(50, 40, 50, 10)
        }

        val hint = TextView(this).apply {
            text = "Select or enter your SafeTour Bharat backend address:"
            textSize = 13f
            setPadding(0, 0, 0, 16)
        }

        val input = EditText(this).apply {
            setText(getServerUrl())
            setSingleLine()
        }

        val quickBtnEmulator = Button(this).apply {
            text = "Use Emulator (10.0.2.2:8000)"
            textSize = 12f
            setOnClickListener { input.setText(DEFAULT_SERVER_URL) }
        }

        val quickBtnLan = Button(this).apply {
            text = "Use LAN IP ($LAN_HINT_URL)"
            textSize = 12f
            setOnClickListener { input.setText(LAN_HINT_URL) }
        }

        val quickBtnOffline = Button(this).apply {
            text = "Use Bundled Offline Assets"
            textSize = 12f
            setOnClickListener { input.setText("file:///android_asset/www/index.html") }
        }

        container.addView(hint)
        container.addView(input)
        container.addView(quickBtnEmulator)
        container.addView(quickBtnLan)
        container.addView(quickBtnOffline)

        builder.setView(container)

        builder.setPositiveButton("Connect & Save") { dialog, _ ->
            val targetUrl = input.text.toString().trim()
            if (targetUrl.isNotEmpty()) {
                setServerUrl(targetUrl)
                errorLayout.visibility = View.GONE
                webView.visibility = View.VISIBLE
                webView.loadUrl(targetUrl)
                Toast.makeText(this, "Connecting to $targetUrl", Toast.LENGTH_SHORT).show()
            }
            dialog.dismiss()
        }

        builder.setNegativeButton("Cancel") { dialog, _ ->
            dialog.dismiss()
        }

        builder.show()
    }
}
