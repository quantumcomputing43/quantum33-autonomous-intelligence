package org.quantum33.autonomousagent

import android.os.Bundle
import android.graphics.Color
import android.view.View
import android.view.Gravity
import android.view.inputmethod.InputMethodManager
import android.content.Context
import android.widget.ScrollView
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.ComponentActivity
import com.chaquo.python.PyObject
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

class MainActivity : ComponentActivity() {
    private lateinit var secureStore: SecureStore

    private fun getAgent(): PyObject {
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
        return Python.getInstance().getModule("phone_agent_bridge")
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        secureStore = SecureStore(this)

        val header = TextView(this).apply {
            text = "QUANTUM33\nQUANTUM COMPUTER SIMULATION MATRIX"
            textSize = 22f
            setTextColor(Color.rgb(57, 255, 20))
            setPadding(12, 18, 12, 18)
        }

        val subtitle = TextView(this).apply {
            text = "AUTONOMOUS AGENT  •  THINK  •  SIMULATE  •  VERIFY"
            textSize = 11f
            setTextColor(Color.rgb(0, 255, 136))
            setPadding(12, 0, 12, 18)
        }

        val commandLabel = TextView(this).apply {
            text = "COMMAND TERMINAL"
            textSize = 13f
            setTextColor(Color.rgb(57, 255, 20))
            setPadding(0, 20, 0, 8)
        }

        val input = EditText(this).apply {
            hint = "Enter an explicit command"
            minLines = 3
            maxLines = 5
            setTextColor(Color.rgb(232, 255, 232))
            setHintTextColor(Color.rgb(143, 191, 154))
            setGravity(Gravity.TOP or Gravity.START)
            setPadding(14, 14, 14, 14)
            isSingleLine = false
        }
        val tokenInput = EditText(this).apply {
            hint = "GitHub token (stored encrypted on this phone)"
            minLines = 1
        }
        val repoInput = EditText(this).apply {
            hint = "Repository owner/name"
            setText("quantumcomputing43/quantum33-autonomous-intelligence")
        }
        val modelEndpointInput = EditText(this).apply {
            hint = "LLM endpoint (OpenAI-compatible, optional)"
        }
        val modelNameInput = EditText(this).apply {
            hint = "LLM model name (optional)"
        }
        val modelKeyInput = EditText(this).apply {
            hint = "LLM API key (optional; not persisted)"
        }
        val status = TextView(this).apply {
            text = if (secureStore.has("github_token"))
                "GitHub credential: configured (encrypted)"
            else
                "GitHub credential: not configured"
            setPadding(0, 16, 0, 16)
        }
        val output = TextView(this).apply {
            text = "SYSTEM // READY\nNo command has been executed."
            setTextColor(Color.rgb(232, 255, 232))
            setBackgroundResource(org.quantum33.autonomousagent.R.drawable.cyber_panel)
            setPadding(18, 18, 18, 18)
        }

        val saveToken = Button(this).apply { text = "Save GitHub Credential Securely" }
        val removeToken = Button(this).apply { text = "Remove GitHub Credential" }
        val saveModel = Button(this).apply { text = "Save LLM Configuration Securely" }
        val removeModel = Button(this).apply { text = "Remove LLM Configuration" }
        val run = Button(this).apply {
            text = "SEND COMMAND"
            minHeight = 52
            isAllCaps = false
        }

        if (secureStore.has("model_endpoint")) {
            modelEndpointInput.setText(secureStore.get("model_endpoint") ?: "")
            modelNameInput.setText(secureStore.get("model_name") ?: "")
        }

        saveToken.setOnClickListener {
            val token = tokenInput.text.toString()
            if (token.isNotBlank()) {
                secureStore.put("github_token", token)
                tokenInput.text.clear()
                status.text = "GitHub credential: configured (encrypted)"
                output.text = "Credential saved to Android Keystore-backed encrypted storage."
            } else {
                output.text = "No credential entered."
            }
        }

        removeToken.setOnClickListener {
            secureStore.remove("github_token")
            tokenInput.text.clear()
            status.text = "GitHub credential: not configured"
            output.text = "GitHub credential removed."
        }

        saveModel.setOnClickListener {
            val endpoint = modelEndpointInput.text.toString().trim()
            val model = modelNameInput.text.toString().trim()
            val key = modelKeyInput.text.toString()
            if (endpoint.isNotBlank() && model.isNotBlank() && key.isNotBlank()) {
                secureStore.put("model_endpoint", endpoint)
                secureStore.put("model_name", model)
                secureStore.put("model_api_key", key)
                modelKeyInput.text.clear()
                output.text = "LLM configuration saved to Android Keystore-backed encrypted storage."
            } else {
                output.text = "Endpoint, model name and API key are required."
            }
        }

        removeModel.setOnClickListener {
            secureStore.remove("model_endpoint")
            secureStore.remove("model_name")
            secureStore.remove("model_api_key")
            modelEndpointInput.text.clear()
            modelNameInput.text.clear()
            modelKeyInput.text.clear()
            output.text = "LLM configuration removed."
        }

        run.setOnClickListener {
            val command = input.text.toString().trim()
            val imm = getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
            imm.hideSoftInputFromWindow(input.windowToken, 0)
            if (command.isBlank()) {
                output.text = "No command entered."
                return@setOnClickListener
            }
            val explicitWrite = command.lowercase().contains("write") ||
                command.lowercase().contains("commit") ||
                command.lowercase().contains("push") ||
                command.lowercase().contains("pull request")

            val execute = {
                output.text = getAgent().callAttr(
                    "handle_command",
                    command,
                    repoInput.text.toString(),
                    secureStore.get("github_token") ?: "",
                    explicitWrite,
                    secureStore.get("model_endpoint") ?: modelEndpointInput.text.toString().trim(),
                    secureStore.get("model_name") ?: modelNameInput.text.toString().trim(),
                    secureStore.get("model_api_key") ?: modelKeyInput.text.toString().trim()
                ).toString()
            }

            if (explicitWrite) {
                CommandConfirmation.confirmWrite(
                    this,
                    "This command may modify a repository. Authorize this single operation only.",
                    execute
                )
            } else {
                execute()
            }
        }

        val content = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.BLACK)
            setPadding(16, 8, 16, 24)
            addView(header)
            addView(subtitle)
            addView(repoInput)
            addView(modelEndpointInput)
            addView(modelNameInput)
            addView(modelKeyInput)
            addView(tokenInput)
            addView(saveToken)
            addView(removeToken)
            addView(saveModel)
            addView(removeModel)
            status.setTextColor(Color.rgb(57, 255, 20))
            addView(status)
            addView(commandLabel)
            addView(input, LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ))
            addView(run, LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                56
            ))
            addView(output, LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { topMargin = 12 })
        }

        val scroll = ScrollView(this).apply {
            isFillViewport = true
            isVerticalScrollBarEnabled = true
            setBackgroundColor(Color.BLACK)
            addView(content)
        }

        setContentView(scroll)

        input.setOnFocusChangeListener { _, hasFocus ->
            if (hasFocus) {
                scroll.postDelayed({
                    scroll.smoothScrollTo(0, content.bottom)
                }, 150)
            }
        }
    }
}
