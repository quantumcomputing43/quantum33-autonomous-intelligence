package org.quantum33.autonomousagent

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.ComponentActivity
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

class MainActivity : ComponentActivity() {
    private lateinit var secureStore: SecureStore

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        secureStore = SecureStore(this)

        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
        val py = Python.getInstance()
        val agent = py.getModule("phone_agent_bridge")

        val input = EditText(this).apply {
            hint = "Enter an explicit command"
            minLines = 3
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
            text = "Quantum33 Autonomous Agent\nReady — no command has been executed."
            setPadding(24, 24, 24, 24)
        }

        val saveToken = Button(this).apply { text = "Save GitHub Credential Securely" }
        val removeToken = Button(this).apply { text = "Remove GitHub Credential" }
        val saveModel = Button(this).apply { text = "Save LLM Configuration Securely" }
        val removeModel = Button(this).apply { text = "Remove LLM Configuration" }
        val run = Button(this).apply { text = "Send Command" }

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
            if (command.isBlank()) {
                output.text = "No command entered."
                return@setOnClickListener
            }
            val explicitWrite = command.lowercase().contains("write") ||
                command.lowercase().contains("commit") ||
                command.lowercase().contains("push") ||
                command.lowercase().contains("pull request")
            if (explicitWrite) {
                CommandConfirmation.confirmWrite(
                    this,
                    "This command may modify a repository. Authorize this single operation only."
                ) {
                    output.text = agent.callAttr(
                        "handle_command",
                        command,
                        repoInput.text.toString(),
                        secureStore.get("github_token") ?: "",
                        true,
                        secureStore.get("model_endpoint") ?: modelEndpointInput.text.toString().trim(),
                        secureStore.get("model_name") ?: modelNameInput.text.toString().trim(),
                        secureStore.get("model_api_key") ?: modelKeyInput.text.toString().trim()
                    ).toString()
                }
            } else {
                output.text = agent.callAttr(
                    "handle_command",
                    command,
                    repoInput.text.toString(),
                    secureStore.get("github_token") ?: "",
                    false,
                    secureStore.get("model_endpoint") ?: modelEndpointInput.text.toString().trim(),
                    secureStore.get("model_name") ?: modelNameInput.text.toString().trim(),
                    secureStore.get("model_api_key") ?: modelKeyInput.text.toString().trim()
                ).toString()
            }
        }

        setContentView(LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(24, 24, 24, 24)
            addView(repoInput)
            addView(modelEndpointInput)
            addView(modelNameInput)
            addView(modelKeyInput)
            addView(tokenInput)
            addView(saveToken)
            addView(removeToken)
            addView(saveModel)
            addView(removeModel)
            addView(status)
            addView(input)
            addView(run)
            addView(output)
        })
    }
}
