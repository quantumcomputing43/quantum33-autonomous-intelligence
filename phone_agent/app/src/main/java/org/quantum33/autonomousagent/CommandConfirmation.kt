package org.quantum33.autonomousagent

import android.app.AlertDialog
import android.content.Context

object CommandConfirmation {
    fun confirmWrite(context: Context, description: String, onApproved: () -> Unit) {
        AlertDialog.Builder(context)
            .setTitle("Explicit authorization required")
            .setMessage(description)
            .setNegativeButton("Cancel", null)
            .setPositiveButton("Authorize once") { _, _ -> onApproved() }
            .show()
    }
}
