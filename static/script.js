function translatePolicy(){
    let aws_policy = document.getElementById('aws_policy').value;
    let oci_group = document.getElementById('oci_group').value;

    fetch('/translate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({aws_policy, oci_group})
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('oci_policy_output').textContent = data.oci_policy;
        visualizeConditions(data.oci_policy);
        showValidationResults(data.validation_errors);
    });
}

function visualizeConditions(policy){
    const conditionDiv = document.getElementById('condition_visualizer');
    conditionDiv.innerHTML = '';
    const conditions = policy.match(/where (.+)/g);
    if (conditions) {
        conditions.forEach(cond => {
            const condElem = document.createElement('div');
            condElem.textContent = `Condition: ${cond.replace('where ', '')}`;
            condElem.classList.add('condition');
            conditionDiv.appendChild(condElem);
        });
    }
}

function showValidationResults(errors){
    if(errors.length > 0){
        alert("Validation Errors:\n" + errors.join("\n"));
    } else {
        alert("Policy Validated Successfully!");
    }
}
function openDocs(){
  document.getElementById("docsModal").style.display = "block";
}

function closeDocs(){
  document.getElementById("docsModal").style.display = "none";
}

// Close modal when clicking outside the content
window.onclick = function(event) {
  let modal = document.getElementById("docsModal");
  if (event.target == modal) {
    modal.style.display = "none";
  }
}
