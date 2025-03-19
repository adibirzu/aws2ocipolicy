from flask import Flask, request, render_template_string, send_file
from translator import translate_aws_to_oci
from io import BytesIO

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>AWS to OCI Policy Translator</title>
</head>
<body>
    <h2>AWS → OCI Policy Translator</h2>
    <form method="POST">
        <textarea name="aws_policy" rows="15" cols="80" placeholder="Paste AWS JSON Policy"></textarea><br>
        OCI Group Name: <input type="text" name="group_name" value="ImportedAWSGroup"/><br>
        <button type="submit">Translate to OCI Policy</button>
    </form>

    {% if oci_policy %}
        <h3>Generated OCI Policy:</h3>
        <pre>{{ oci_policy }}</pre>
        <form action="/download" method="POST">
            <input type="hidden" name="oci_policy" value="{{ oci_policy }}">
            <button type="submit">Download as File</button>
        </form>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    oci_policy = ""
    if request.method == "POST":
        aws_policy = request.form.get("aws_policy")
        group_name = request.form.get("group_name", "ImportedAWSGroup")
        if aws_policy:
            oci_policy = translate_aws_to_oci(aws_policy, group_name)
    return render_template_string(HTML_TEMPLATE, oci_policy=oci_policy)

@app.route("/download", methods=["POST"])
def download():
    oci_policy = request.form.get("oci_policy", "")
    buffer = BytesIO()
    buffer.write(oci_policy.encode())
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="oci_policy.txt")

if __name__ == "__main__":
    app.run(debug=True)
