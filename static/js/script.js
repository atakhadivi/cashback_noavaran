// Main JavaScript file for the Cashback application

document.addEventListener('DOMContentLoaded', function() {
  console.log('Cashback application JavaScript initialized');
  
  // Initialize any interactive elements
  initializeComponents();
});

function initializeComponents() {
  // Add event listeners and initialize UI components
  
  // Example: Initialize tooltips if using Bootstrap
  if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
  }
}