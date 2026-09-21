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
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
        val py = Python.getInstance()
        val agent = py.getModule("phone_agent_bridge")

        val input = EditText(this).apply {
            hint = "Enter an explicit command"
            minLines = 3
        }
        val output = TextView(this).apply {
            text = "Quantum33 Autonomous Agent\nReady — no command has been executed."
            setPadding(24, 24, 24, 24)
        }
        val run = Button(this).apply { text = "Send Command" }

        run.setOnClickListener {
            val command = input.text.toString()
            output.text = agent.callAttr("handle_command", command).toString()
        }

        setContentView(LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(24, 24, 24, 24)
            addView(input)
            addView(run)
            addView(output)
        })
    }
}
