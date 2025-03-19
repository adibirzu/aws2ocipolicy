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
    });
}

function downloadPolicy(){
    const text = document.getElementById('oci_policy_output').textContent;
    const blob = new Blob([text], {type: 'text/plain'});
    const anchor = document.createElement('a');
    anchor.href = URL.createObjectURL(blob);
    anchor.download = "oci_policy.txt";
    anchor.click();
}
