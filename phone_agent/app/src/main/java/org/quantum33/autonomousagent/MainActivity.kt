package org.quantum33.autonomousagent

import android.os.Bundle
import android.text.InputType
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.activity.ComponentActivity
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

class MainActivity : ComponentActivity() {
    private lateinit var secureStore: SecureStore

    private fun field(hint: String, value: String = "") = EditText(this).apply {
        this.hint = hint
        setText(value)
        minLines = 1
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        secureStore = SecureStore(this)

        if (!Python.isStarted()) Python.start(AndroidPlatform(this))
        val agent = Python.getInstance().getModule("phone_agent_bridge")

        val sourceRepo = field(
            "Agent source repository owner/name",
            secureStore.get("source_repo") ?: "quantumcomputing43/quantum33-autonomous-intelligence"
        )
        val simulationRepo = field(
            "Simulation Matrix repository owner/name",
            secureStore.get("simulation_repo") ?: "quantumcomputing43/quantum33-simulation-matrix"
        )
        val simulationWorkflow = field(
            "Simulation workflow file/name",
            secureStore.get("simulation_workflow") ?: "simulation-matrix.yml"
        )
        val tokenInput = field("GitHub token (encrypted on this phone)")
        tokenInput.inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD

        val endpoint = field("LLM endpoint, e.g. https://.../v1",
            secureStore.get("model_endpoint") ?: "")
        val model = field("LLM model name", secureStore.get("model_name") ?: "")
        val modelKey = field("LLM API key (encrypted on this phone)")
        modelKey.inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD

        val command = field("Enter an explicit command for the Agent")
        command.minLines = 3

        val status = TextView(this).apply {
            text = "CONFIGURATION: NOT VALIDATED"
            setPadding(0, 16, 0, 16)
        }
        val output = TextView(this).apply {
            text = "Anonymous Simulation Matrix Agent\nSetup required before autonomous execution."
            setPadding(24, 24, 24, 24)
        }

        fun saveConfig() {
            secureStore.put("source_repo", sourceRepo.text.toString().trim())
            secureStore.put("simulation_repo", simulationRepo.text.toString().trim())
            secureStore.put("simulation_workflow", simulationWorkflow.text.toString().trim())
            val token = tokenInput.text.toString()
            if (token.isNotBlank()) secureStore.put("github_token", token)
            val ep = endpoint.text.toString().trim()
            val mn = model.text.toString().trim()
            val key = modelKey.text.toString()
            if (ep.isNotBlank()) secureStore.put("model_endpoint", ep)
            if (mn.isNotBlank()) secureStore.put("model_name", mn)
            if (key.isNotBlank()) secureStore.put("model_api_key", key)
            tokenInput.text.clear()
            modelKey.text.clear()
        }

        val save = Button(this).apply { text = "SAVE CONFIGURATION SECURELY" }
        val validate = Button(this).apply { text = "VALIDATE CONFIGURATION" }
        val run = Button(this).apply { text = "SEND COMMAND TO AGENT" }

        save.setOnClickListener {
            saveConfig()
            output.text = "Configuration saved in Android Keystore-backed storage."
        }

        validate.setOnClickListener {
            saveConfig()
            output.text = "Validating GitHub, LLM backend, source repo and Simulation Matrix..."
            val result = agent.callAttr(
                "validate_configuration",
                sourceRepo.text.toString().trim(),
                simulationRepo.text.toString().trim(),
                simulationWorkflow.text.toString().trim(),
                secureStore.get("github_token") ?: "",
                secureStore.get("model_endpoint") ?: endpoint.text.toString().trim(),
                secureStore.get("model_name") ?: model.text.toString().trim(),
                secureStore.get("model_api_key") ?: modelKey.text.toString().trim()
            ).toString()
            output.text = result
            status.text = if (result.startsWith("READY")) "CONFIGURATION: READY"
            else "CONFIGURATION: BLOCKED"
        }

        run.setOnClickListener {
            val text = command.text.toString().trim()
            if (text.isBlank()) {
                output.text = "No command entered."
                return@setOnClickListener
            }
            val explicitWrite = text.lowercase().let {
                it.contains("write") || it.contains("commit") || it.contains("push") ||
                it.contains("create file") || it.contains("update file") || it.contains("pull request") ||
                it.contains("fix") || it.contains("repair") || it.contains("modify") ||
                it.contains("develop") || it.contains("implement") || it.contains("run simulation") ||
                it.contains("simulation matrix") || it.contains("dispatch workflow")
            }
            val execute = {
                output.text = agent.callAttr(
                    "handle_command",
                    text,
                    sourceRepo.text.toString().trim(),
                    secureStore.get("github_token") ?: "",
                    explicitWrite,
                    secureStore.get("model_endpoint") ?: endpoint.text.toString().trim(),
                    secureStore.get("model_name") ?: model.text.toString().trim(),
                    secureStore.get("model_api_key") ?: modelKey.text.toString().trim(),
                    simulationRepo.text.toString().trim()
                ).toString()
            }
            if (explicitWrite) {
                CommandConfirmation.confirmWrite(
                    this,
                    "This Agent command may modify the source or simulation repository. Authorize this single operation only.",
                    execute
                )
            } else execute()
        }

        val content = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(24, 24, 24, 24)
            addView(TextView(context).apply { text = "AGENT CONFIGURATION" })
            addView(sourceRepo)
            addView(simulationRepo)
            addView(simulationWorkflow)
            addView(tokenInput)
            addView(endpoint)
            addView(model)
            addView(modelKey)
            addView(save)
            addView(validate)
            addView(status)
            addView(command)
            addView(run)
            addView(output)
        }
        setContentView(ScrollView(this).apply { addView(content) })
    }
}
