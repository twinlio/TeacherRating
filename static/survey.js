let currentTab = 0;
          showTab(currentTab);

          function showTab(n){
            var x = document.getElementsByClassName("step");
            x[n].style.display = "block";

   
            if (n == 0) {
            document.getElementById("prevBtn").style.display = "none";
            } else {
              document.getElementById("prevBtn").style.display = "inline";
            }
            if (n == (x.length - 1)) {
              document.getElementById("nextBtn").innerHTML = "Submit";
            } else {
              document.getElementById("nextBtn").innerHTML = "Next";
            }
            fixStepIndicator(n)
          }

          function nextPrev(n) {
            // This function will figure out which tab to display
            var x = document.getElementsByClassName("step");
            // Hide the current tab:
            x[currentTab].style.display = "none";
            // Increase or decrease the current tab by 1:
            currentTab = currentTab + n;
            // if you have reached the end of the form...
            if (currentTab >= x.length) {
              // ... the form gets submitted:
              document.getElementById("form").submit();
              return false;
            }
            // Otherwise, display the correct tab:
            showTab(currentTab);
          }

          function fixStepIndicator(n) {
            // This function removes the "active" class of all steps...
            var i, x = document.getElementsByClassName("indicator");
            for (i = 0; i < x.length; i++) {
              x[i].className = x[i].className.replace(" active", "");
            }
            //... and adds the "active" class on the current step:
            x[n].className += " active";
          }