/**
 * patient-detail.js — Patient detail page edit and save interactions.
 * Replaces Phase 3 in-memory edit save with a real PUT fetch() call.
 */

/**
 * Collect edited vitals from the inline form and PUT them to the API.
 *
 * @param {number} patientId - The integer patient ID.
 */
async function savePatientEdits(patientId) {
    const saveBtn = document.getElementById("save-btn");

    // Collect fields that may be editable
    const payload = {};
    const fieldIds = [
        "full_name", "age", "pain_level", "resp_rate",
        "heart_rate", "oxygen_sat", "bp_systolic", "bp_diastolic", "symptoms",
    ];

    fieldIds.forEach((fieldId) => {
        const el = document.getElementById(`edit-${fieldId}`);
        if (el) {
            const val = el.value.trim();
            payload[fieldId] = val === "" ? null : val;
        }
    });

    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.textContent = "Saving…";
    }

    try {
        const response = await fetch(`/patients/${patientId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            throw new Error(data.error || `Server error: ${response.status}`);
        }

        const updated = await response.json();

        // Reflect updated values back into display elements (Phase 3 DOM IDs)
        Object.entries(updated).forEach(([key, val]) => {
            const displayEl = document.getElementById(`display-${key}`);
            if (displayEl && val !== null && val !== undefined) {
                displayEl.textContent = val;
            }
        });

        // Show success toast if present
        const toast = document.getElementById("save-success");
        if (toast) {
            toast.style.display = "block";
            setTimeout(() => (toast.style.display = "none"), 3000);
        }

        // Close edit panel if present
        const editPanel = document.getElementById("edit-panel");
        if (editPanel) editPanel.style.display = "none";

    } catch (err) {
        console.error("Save failed:", err);
        const errorEl = document.getElementById("save-error");
        if (errorEl) {
            errorEl.textContent = `Save failed: ${err.message}`;
            errorEl.style.display = "block";
        }
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.textContent = "Save Changes";
        }
    }
}

// Wire up save button with the patient ID from a data attribute
document.addEventListener("DOMContentLoaded", () => {
    const saveBtn = document.getElementById("save-btn");
    if (saveBtn) {
        const patientId = saveBtn.dataset.patientId;
        saveBtn.addEventListener("click", (e) => {
            e.preventDefault();
            if (patientId) savePatientEdits(patientId);
        });
    }
});
