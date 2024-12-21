// Export for module usage
export function showTab(tabName) {
  // Get all tab contents and buttons
  const tabContents = document.querySelectorAll(".tab-content");
  const tabButtons = document.querySelectorAll(".tab-button");

  // Hide all tab contents and remove active class from buttons
  tabContents.forEach((tab) => {
    tab.classList.remove("active");
  });
  tabButtons.forEach((button) => {
    button.classList.remove("active");
  });

  // Show selected tab and activate its button
  const selectedTab = document.getElementById(tabName);
  const selectedButton = document.querySelector(
    `button[onclick="window.showTab('${tabName}')"]`
  );

  if (selectedTab) selectedTab.classList.add("active");
  if (selectedButton) selectedButton.classList.add("active");
}

// Make it available globally
window.showTab = showTab;
