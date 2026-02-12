document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Build participants list HTML
        let participantsHTML = '';
        if (details.participants.length > 0) {
          participantsHTML = `
            <div class="participants-section">
              <p><strong>Participants:</strong></p>
              <ul class="participants-list">
                ${details.participants.map(email => `
                  <li>
                    <span class="participant-email">${email}</span>
                    <button class="delete-btn" onclick="removeParticipant('${name}', '${email}')" title="Remove participant">
                      ✕
                    </button>
                  </li>
                `).join('')}
              </ul>
            </div>
          `;
        } else {
          participantsHTML = `
            <div class="participants-section">
              <p><strong>Participants:</strong> <em>No signups yet</em></p>
            </div>
          `;
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${participantsHTML}
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        
        // Refresh activities list to show the new participant
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});

// Function to remove a participant from an activity
async function removeParticipant(activityName, email) {
  if (!confirm(`Are you sure you want to remove ${email} from ${activityName}?`)) {
    return;
  }

  try {
    const response = await fetch(
      `/activities/${encodeURIComponent(activityName)}/signup?email=${encodeURIComponent(email)}`,
      {
        method: "DELETE",
      }
    );

    const result = await response.json();

    if (response.ok) {
      // Reload activities to show updated list
      const activitiesList = document.getElementById("activities-list");
      const activitySelect = document.getElementById("activity");
      
      // Clear existing activities
      activitiesList.innerHTML = "<p>Reloading activities...</p>";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';
      
      // Fetch updated activities
      await fetchActivities();
      
      // Show success message
      const messageDiv = document.getElementById("message");
      messageDiv.textContent = result.message;
      messageDiv.className = "success";
      messageDiv.classList.remove("hidden");
      
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } else {
      alert(result.detail || "Failed to remove participant");
    }
  } catch (error) {
    alert("Failed to remove participant. Please try again.");
    console.error("Error removing participant:", error);
  }
}

// Make fetchActivities globally accessible
window.fetchActivities = document.addEventListener ? 
  function() {
    const activitiesList = document.getElementById("activities-list");
    const activitySelect = document.getElementById("activity");
    return fetch("/activities")
      .then(response => response.json())
      .then(activities => {
        activitiesList.innerHTML = "";
        Object.entries(activities).forEach(([name, details]) => {
          const activityCard = document.createElement("div");
          activityCard.className = "activity-card";
          const spotsLeft = details.max_participants - details.participants.length;
          let participantsHTML = '';
          if (details.participants.length > 0) {
            participantsHTML = `
              <div class="participants-section">
                <p><strong>Participants:</strong></p>
                <ul class="participants-list">
                  ${details.participants.map(email => `
                    <li>
                      <span class="participant-email">${email}</span>
                      <button class="delete-btn" onclick="removeParticipant('${name}', '${email}')" title="Remove participant">
                        ✕
                      </button>
                    </li>
                  `).join('')}
                </ul>
              </div>
            `;
          } else {
            participantsHTML = `
              <div class="participants-section">
                <p><strong>Participants:</strong> <em>No signups yet</em></p>
              </div>
            `;
          }
          activityCard.innerHTML = `
            <h4>${name}</h4>
            <p>${details.description}</p>
            <p><strong>Schedule:</strong> ${details.schedule}</p>
            <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
            ${participantsHTML}
          `;
          activitiesList.appendChild(activityCard);
          const option = document.createElement("option");
          option.value = name;
          option.textContent = name;
          activitySelect.appendChild(option);
        });
      });
  } : null;
