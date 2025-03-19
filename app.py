from flask import Flask, request, render_template, jsonify
from translator import translate_aws_to_oci, validate_oci_policy

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/translate", methods=["POST"])
def translate():
    data = request.json
    aws_policy = data.get("aws_policy")
    oci_group = data.get("oci_group", "ImportedAWSGroup")
    oci_policy = translate_aws_to_oci(aws_policy, oci_group)
    validation_errors = validate_oci_policy(oci_policy)
    return jsonify({
        "oci_policy": oci_policy,
        "validation_errors": validation_errors
    })

if __name__ == "__main__":
    app.run(debug=True)
