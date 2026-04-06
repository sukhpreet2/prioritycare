/**
 * patients.js — Patient list page interactions.
 * Replaces Phase 3 in-memory delete with a real DELETE fetch() call.
 */

/**
 * Send a DELETE request for the given patient ID and remove the row from the DOM.
 *
 * @param {number} patientId - The integer patient ID.
 * @param {HTMLElement} rowEl - The table row element to remove on success.
 */
async function deletePatient(patientId, rowEl) {
    if (!confirm("Delete this patient record? This cannot be undone.")) {
        return;
    }

    try {
        const response = await fetch(`/patients/${patientId}`, {
            method: "DELETE",
            headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            throw new Error(data.error || `Server error: ${response.status}`);
        }

        const result = await response.json();
        if (result.success) {
            // Animate row removal
            rowEl.style.transition = "opacity 0.3s";
            rowEl.style.opacity = "0";
            setTimeout(() => rowEl.remove(), 300);
        }
    } catch (err) {
        console.error("Delete failed:", err);
        alert(`Could not delete patient: ${err.message}`);
    }
}

// Attach delete handlers to all delete buttons in the patient table
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-delete-patient]").forEach((btn) => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            const patientId = btn.dataset.deletePatient;
            const row = btn.closest("tr");
            if (patientId && row) {
                deletePatient(patientId, row);
            }
        });
    });
});
