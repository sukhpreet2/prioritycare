/**
 * new-patient.js — Handles triage prediction on the New Patient form.
 * Replaces Phase 3 console.log() placeholder with a real fetch() call.
 */

/**
 * Collect vital signs from the form and send them to the Flask predict endpoint.
 * Updates the DOM with the returned triage label, confidence, and suggested action.
 */
async function calculateTriagePrediction() {
    const formData = {
        age:        parseFloat(document.getElementById("age")?.value) || null,
        pain_level: parseFloat(document.getElementById("pain_level")?.value) || 0,
        resp_rate:  parseFloat(document.getElementById("resp_rate")?.value) || null,
        heart_rate: parseFloat(document.getElementById("heart_rate")?.value) || null,
        oxygen_sat: parseFloat(document.getElementById("oxygen_sat")?.value) || null,
    };

    // Show a loading state on the predict button
    const predictBtn = document.getElementById("predict-btn");
    if (predictBtn) {
        predictBtn.disabled = true;
        predictBtn.textContent = "Calculating…";
    }

    try {
        const response = await fetch("/patients/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData),
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const result = await response.json();

        // Populate triage result section (IDs match Phase 3 HTML)
        const labelEl = document.getElementById("triage-label");
        const confidenceEl = document.getElementById("triage-confidence");
        const actionEl = document.getElementById("triage-action");
        const resultSection = document.getElementById("triage-result");
        const hiddenLabel = document.getElementById("hidden-triage-label");
        const hiddenConf = document.getElementById("hidden-confidence");

        if (labelEl) {
            labelEl.textContent = result.label;
            // Apply Phase 3 badge CSS classes
            labelEl.className = labelEl.className.replace(/badge-(red|yellow|green)/g, "");
            labelEl.classList.add(`badge-${result.label.toLowerCase()}`);
        }

        if (confidenceEl) {
            confidenceEl.textContent = `${Math.round(result.confidence * 100)}% confidence`;
        }

        if (actionEl) {
            actionEl.textContent = result.suggested_action || "";
        }

        // Store hidden fields for form submission
        if (hiddenLabel) hiddenLabel.value = result.label;
        if (hiddenConf)  hiddenConf.value  = result.confidence;

        // Show the result card
        if (resultSection) resultSection.style.display = "block";

    } catch (err) {
        console.error("Prediction request failed:", err);
        const errorEl = document.getElementById("predict-error");
        if (errorEl) {
            errorEl.textContent = "Prediction unavailable — please try again.";
            errorEl.style.display = "block";
        }
    } finally {
        if (predictBtn) {
            predictBtn.disabled = false;
            predictBtn.textContent = "Predict Triage";
        }
    }
}

// Attach event listener once DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    const predictBtn = document.getElementById("predict-btn");
    if (predictBtn) {
        predictBtn.addEventListener("click", (e) => {
            e.preventDefault();
            calculateTriagePrediction();
        });
    }
});
