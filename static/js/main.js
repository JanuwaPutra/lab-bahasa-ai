/**
 * Main JavaScript for Lab Bahasa AI
 */

document.addEventListener("DOMContentLoaded", function () {
  // Add active class to current navigation item
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll(".nav-link");

  navLinks.forEach((link) => {
    if (link.getAttribute("href") === currentPath) {
      link.classList.add("active");
    }
  });



  // Initialize Bootstrap popovers if they exist
  if (typeof bootstrap !== "undefined" && bootstrap.Popover) {
    const popoverTriggerList = [].slice.call(
      document.querySelectorAll('[data-bs-toggle="popover"]')
    );
    popoverTriggerList.map(function (popoverTriggerEl) {
      return new bootstrap.Popover(popoverTriggerEl);
    });
  }

  // Flash message auto-hide
  const flashMessages = document.querySelectorAll(".alert-dismissible");
  flashMessages.forEach((message) => {
    setTimeout(() => {
      const closeButton = message.querySelector(".btn-close");
      if (closeButton) {
        closeButton.click();
      } else {
        message.style.display = "none";
      }
    }, 5000); // Hide after 5 seconds
  });

  // Helper function to format timestamps
  window.formatDateTime = function (dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  // Helper function for AJAX requests
  window.fetchData = async function (url, options = {}) {
    try {
      const response = await fetch(url, options);
      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Fetch error:", error);
      throw error;
    }
  };

  // Helper function to show alerts
  window.showAlert = function (
    message,
    type = "info",
    container = "body",
    timeout = 5000
  ) {
    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute("role", "alert");

    alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

    const targetContainer = document.querySelector(container);
    if (targetContainer) {
      targetContainer.prepend(alertDiv);
    } else {
      document.body.prepend(alertDiv);
    }

    if (timeout > 0) {
      setTimeout(() => {
        alertDiv.classList.remove("show");
        setTimeout(() => alertDiv.remove(), 150);
      }, timeout);
    }

    return alertDiv;
  };

  // Toggle sidebar
  const sidebarCollapse = document.getElementById('sidebarCollapse');
  const sidebar = document.getElementById('sidebar');
  const content = document.getElementById('content');
  const sidebarCollapseBtn = document.getElementById('sidebarCollapseBtn');
  
  if (sidebarCollapse) {
    sidebarCollapse.addEventListener('click', function() {
      sidebar.classList.toggle('active');
      content.classList.toggle('active');
      
      // Add/remove overlay class on body for mobile
      if (window.innerWidth < 768) {
        document.body.classList.toggle('sidebar-active');
      }
    });
  }
  
  // Close sidebar with X button on mobile
  if (sidebarCollapseBtn) {
    sidebarCollapseBtn.addEventListener('click', function() {
      sidebar.classList.toggle('active');
      content.classList.toggle('active');
      document.body.classList.remove('sidebar-active');
    });
  }
  
  // Close sidebar when clicking outside on mobile
  document.addEventListener('click', function(event) {
    if (
      window.innerWidth < 768 && 
      sidebar && 
      !sidebar.contains(event.target) && 
      !sidebarCollapse.contains(event.target) &&
      sidebar.classList.contains('active')
    ) {
      sidebar.classList.remove('active');
      content.classList.remove('active');
      document.body.classList.remove('sidebar-active');
    }
  });
  
  // Auto-open sidebar on desktop
  window.addEventListener('resize', function() {
    if (window.innerWidth > 768 && sidebar) {
      sidebar.classList.remove('active');
      content.classList.remove('active');
      document.body.classList.remove('sidebar-active');
    }
  });
  
  // Auto-close sidebar on mobile on page load
  if (window.innerWidth < 768 && sidebar) {
    sidebar.classList.add('active');
    content.classList.remove('active');
  }
  
  // Word count for essays in assessment pages
  const textareas = document.querySelectorAll('textarea[data-word-count]');
  textareas.forEach(textarea => {
    const wordCountDisplay = document.getElementById(textarea.dataset.wordCount);
    if (wordCountDisplay) {
      textarea.addEventListener('input', function() {
        const wordCount = textarea.value.trim().split(/\s+/).filter(Boolean).length;
        wordCountDisplay.textContent = wordCount;
      });
    }
  });
});

