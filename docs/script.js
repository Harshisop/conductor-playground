// Replace this with your deployed Google Apps Script URL
const APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyeKwjrPHwjJW1ArXSNPcPFlQHVqHxVVdlv2Jp0UhAVQGpds7tP0vsifX551p53QSi-/exec";

const form = document.getElementById("registration-form");
const statusDiv = document.getElementById("status");
const submitBtn = document.getElementById("submit-btn");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("name").value.trim();
    const keywords = document.getElementById("keywords").value.trim();

    // Collect checked locations + custom
    const checkedLocations = Array.from(
        document.querySelectorAll('input[name="location"]:checked')
    ).map((cb) => cb.value);

    const customLocation = document.getElementById("custom-location").value.trim();
    if (customLocation) {
        customLocation.split(",").forEach((loc) => {
            const trimmed = loc.trim();
            if (trimmed) checkedLocations.push(trimmed);
        });
    }
    const locations = checkedLocations.join(", ");

    const sources = Array.from(
        document.querySelectorAll('input[name="source"]:checked')
    ).map((cb) => cb.value).join(", ");

    const jobTypes = Array.from(
        document.querySelectorAll('input[name="job_type"]:checked')
    ).map((cb) => cb.value).join(", ");

    // Validate
    if (!name || !keywords) {
        showStatus("Please fill in your name and keywords.", "error");
        return;
    }
    if (!locations) {
        showStatus("Please select at least one location.", "error");
        return;
    }
    if (!sources) {
        showStatus("Please select at least one job source.", "error");
        return;
    }
    if (!jobTypes) {
        showStatus("Please select at least one job type.", "error");
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Registering...";

    const payload = {
        name: name,
        keywords: keywords,
        locations: locations,
        sources: sources,
        job_types: jobTypes,
    };

    try {
        const response = await fetch(APPS_SCRIPT_URL, {
            method: "POST",
            headers: { "Content-Type": "text/plain" },
            body: JSON.stringify(payload),
        });

        const result = await response.json();

        if (result.status === "ok") {
            showStatus(result.message, "success");
            form.reset();
        } else {
            showStatus(result.message || "Something went wrong.", "error");
        }
    } catch (err) {
        // Apps Script redirects can make the response opaque
        // If we get here, the request likely succeeded
        showStatus(
            "Registration submitted! Your jobs will appear in the Google Sheet within 3 days.",
            "success"
        );
        form.reset();
    }

    submitBtn.disabled = false;
    submitBtn.textContent = "Register";
});

function showStatus(message, type) {
    statusDiv.textContent = message;
    statusDiv.className = "status " + type;
}
