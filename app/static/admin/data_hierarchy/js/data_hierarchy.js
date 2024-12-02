console.log('Starting data_hierarchy.js');

import { initChart } from './chart.js';
import { showSidebar, closeSidebar } from './sidebar.js';
import { handleFormSubmit, handleUserFormSubmit } from './forms.js';

document.addEventListener('DOMContentLoaded', () => {
  // Load the data and initialize the chart
  initChart(data);


  // Set up event listeners

  const entityForm = document.getElementById('entity-form');
  if (entityForm) {
      entityForm.addEventListener('submit', (event) => {
          handleFormSubmit(event);
      });
  }

  const userForm = document.getElementById('user-form');
  if (userForm) {
      userForm.addEventListener('submit', (event) => {
          handleUserFormSubmit(event);
      });
  }  
  
  document.getElementById("open-entity-drawer").addEventListener("click", () => {
    document.getElementById("entity-drawer").style.display = "block";
  });

  document.getElementById("open-user-drawer").addEventListener("click", () => {
    document.getElementById("user-drawer").style.display = "block";
  });

  document.getElementById("close-drawer").addEventListener("click", () => {
    document.getElementById("entity-drawer").style.display = "none";
  });

  document.getElementById("close-user-drawer").addEventListener("click", () => {
    document.getElementById("user-drawer").style.display = "none";
  });

});


